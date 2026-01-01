#!/usr/bin/env python3
"""
Fetch current LCSC pricing and MOQ for a list of LCSC part codes.
Outputs results to a JSON file for further processing.

Usage:
    python check_lcsc_pricing.py <input_json> <output_json>

Input JSON format:
    [
        {"lcsc_code": "C137394", "value": "0Ω", "mpn": "RC1206FR-070RL"},
        ...
    ]
"""

import asyncio
import json
import sys
from pathlib import Path
from fastmcp import Client

async def fetch_single_part(client, part: dict, idx: int, total: int, semaphore: asyncio.Semaphore) -> dict:
    """Fetch pricing for a single part with semaphore-controlled concurrency."""
    lcsc_code = part.get("lcsc_code")
    value = part.get("value", "")
    mpn = part.get("mpn", "")

    async with semaphore:
        print(f"Processing {idx}/{total}: {lcsc_code} ({value})", file=sys.stderr)

        try:
            result = await client.call_tool(
                "playwright-mcp-server_browser_execute_bulk",
                {
                    "commands": [
                        {
                            "tool": "browser_navigate",
                            "args": {
                                "url": f"https://www.lcsc.com/product-detail/{lcsc_code}.html",
                                "silent_mode": True
                            }
                        },
                        {
                            "tool": "browser_wait_for",
                            "args": {
                                "text": "Standard Packaging"
                            }
                        },
                        {
                            "tool": "browser_snapshot",
                            "args": {
                                "jmespath_query": "[[].children[].children[].children[].children[].children[?role == 'table'], [].children[].children[].children[].children[].children[].children[?role == 'table']] | [] | [].children[1].children[:6].{qty: children[0].children[0].name.value, unit_price: children[1].name.value, ext_price: children[2].name.value} | []",
                                "output_format": "json"
                            },
                            "return_result": True
                        }
                    ],
                    "stop_on_error": True,
                    "return_all_results": False
                }
            )

            # Extract pricing data from the result
            bulk_results = result.data.get("results", [])
            pricing_snapshot = bulk_results[-1] if bulk_results else None

            # Parse pricing data
            pricing = []
            if pricing_snapshot and "snapshot" in pricing_snapshot:
                pricing = pricing_snapshot["snapshot"]

            return {
                "lcsc_code": lcsc_code,
                "value": value,
                "mpn": mpn,
                "pricing": pricing,
                "success": True,
                "index": idx
            }

        except Exception as e:
            print(f"Error processing {lcsc_code}: {e}", file=sys.stderr)
            return {
                "lcsc_code": lcsc_code,
                "value": value,
                "mpn": mpn,
                "error": str(e),
                "success": False,
                "index": idx
            }


async def get_lcsc_pricing(parts_list: list, output_file: Path, max_concurrent: int = 15) -> None:
    """Fetch LCSC pricing for all parts in parallel with controlled concurrency."""
    config_path = Path(__file__).parent.parent / ".mcp.json"
    with open(config_path) as f:
        config = json.load(f)

    client = Client(config)

    # Initialize the output file with an empty array
    with open(output_file, 'w') as f:
        f.write('[\n')

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)

    async with client:
        # Create all tasks
        tasks = [
            fetch_single_part(client, part, idx + 1, len(parts_list), semaphore)
            for idx, part in enumerate(parts_list)
        ]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

        # Sort by original index to maintain order
        results.sort(key=lambda x: x.get("index", 0))

        # Write all results to file
        for idx, entry in enumerate(results):
            # Remove the index field before writing
            entry_copy = {k: v for k, v in entry.items() if k != "index"}

            if idx > 0:
                with open(output_file, 'a') as f:
                    f.write(',\n')

            with open(output_file, 'a') as f:
                json.dump(entry_copy, f, indent=2)

    # Close the JSON array
    with open(output_file, 'a') as f:
        f.write('\n]\n')

def main():
    if len(sys.argv) != 3:
        print("Usage: python check_lcsc_pricing.py <input_json> <output_json>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    # Load input data
    with open(input_file) as f:
        parts_list = json.load(f)

    max_concurrent = 15
    print(f"Starting to process {len(parts_list)} parts...", file=sys.stderr)
    print(f"Max concurrent requests: {max_concurrent}", file=sys.stderr)
    print(f"Results will be written to {output_file}", file=sys.stderr)
    print("", file=sys.stderr)

    # Fetch pricing in parallel (writes to output_file when complete)
    asyncio.run(get_lcsc_pricing(parts_list, output_file, max_concurrent))

    # Load results to generate summary
    with open(output_file) as f:
        results = json.load(f)

    print(f"\n✓ Results saved to {output_file}", file=sys.stderr)
    print(f"Processed {len(results)} parts", file=sys.stderr)
    print(f"Successful: {sum(1 for r in results if r.get('success'))}", file=sys.stderr)
    print(f"Failed: {sum(1 for r in results if not r.get('success'))}", file=sys.stderr)

if __name__ == "__main__":
    main()
