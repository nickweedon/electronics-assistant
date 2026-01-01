#!/usr/bin/env python3
"""
Add multiple parts to LCSC shopping cart using real browser session.
This script uses the playwright-real-session-mcp-server to interact with an existing browser session.

Usage:
    python lcsc_add_to_cart.py <lcsc_code1> <lcsc_code2> ... [--qty QUANTITY] [-o OUTPUT]
    python lcsc_add_to_cart.py --file codes.txt [--qty QUANTITY] [-o OUTPUT]

Examples:
    # Add 2 parts with default quantity (100)
    python lcsc_add_to_cart.py C137394 C137181

    # Add parts from file with custom quantity and output file
    python lcsc_add_to_cart.py --file lcsc_codes.txt --qty 50 -o results.json
"""
import asyncio
import json
import argparse
from pathlib import Path
from fastmcp import Client


async def add_parts_to_cart(lcsc_codes: list, quantity: int = 100, output_file: Path = None):
    """Add parts to LCSC cart - processes one item at a time sequentially."""
    config_path = Path(__file__).parent.parent / ".mcp.json"
    with open(config_path) as f:
        config = json.load(f)

    client = Client(config)
    results = []

    # Initialize output file with empty array if specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump([], f)

    async with client:
        for i, lcsc_code in enumerate(lcsc_codes, start=1):
            print(f"\n[{i}/{len(lcsc_codes)}] Adding {lcsc_code} (qty: {quantity})...")

            try:
                # Step 1: Navigate to product page
                print(f"  → Navigating to product page...")
                nav_result = await client.call_tool(
                    "playwright-real-session-mcp-server_browser_navigate",
                    {
                        "url": f"https://www.lcsc.com/product-detail/{lcsc_code}.html",
                        "silent_mode": True
                    }
                )

                # Wait after navigation
                await asyncio.sleep(1)

                if not nav_result.data or not nav_result.data.get("success"):
                    print(f"  ✗ Failed to navigate to {lcsc_code}")
                    results.append({"code": lcsc_code, "status": "failed", "error": "Navigation failed"})
                    continue

                # Step 2: Set the quantity with proper event triggering
                print(f"  → Setting quantity to {quantity}...")
                set_qty_result = await client.call_tool(
                    "playwright-real-session-mcp-server_browser_evaluate",
                    {
                        "function": f"""() => {{
                            const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
                            const qtyInput = inputs.find(inp => inp.placeholder && (inp.placeholder.includes('Qty') || inp.placeholder.includes('Quantity')));
                            if (qtyInput) {{
                                qtyInput.focus();
                                qtyInput.value = '';
                                qtyInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                qtyInput.value = '{quantity}';
                                qtyInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                qtyInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                qtyInput.blur();
                                return {{ success: true, value: qtyInput.value, id: qtyInput.id }};
                            }}
                            return {{ success: false, error: 'Quantity input not found' }};
                        }}"""
                    }
                )

                # Wait after setting quantity
                await asyncio.sleep(0.5)

                # Check if quantity was set successfully
                eval_data = str(set_qty_result.content[0].text) if set_qty_result.content else ""
                if "\"success\": false" in eval_data or "'success': False" in eval_data:
                    print(f"  ✗ Could not set quantity for {lcsc_code}")
                    results.append({"code": lcsc_code, "status": "failed", "error": "Could not set quantity"})
                    continue

                # Step 3: Click the Add To Cart button
                print(f"  → Clicking Add To Cart...")
                click_result = await client.call_tool(
                    "playwright-real-session-mcp-server_browser_evaluate",
                    {
                        "function": "() => { const buttons = Array.from(document.querySelectorAll('button')); const addButton = buttons.find(b => b.textContent.includes('Add To Cart')); if (addButton) { addButton.click(); return { success: true, clicked: true }; } return { success: false, error: 'Button not found' }; }"
                    }
                )

                # Wait after clicking
                await asyncio.sleep(0.5)

                # Check if click was successful
                click_data = str(click_result.content[0].text) if click_result.content else ""
                if "\"success\": false" in click_data or "'success': False" in click_data:
                    print(f"  ✗ Could not click Add To Cart for {lcsc_code}")
                    results.append({"code": lcsc_code, "status": "failed", "error": "Could not click button"})
                    continue

                print(f"  ✓ Successfully added {lcsc_code}")
                results.append({"code": lcsc_code, "status": "success"})

            except Exception as e:
                print(f"  ✗ Exception for {lcsc_code}: {str(e)}")
                results.append({"code": lcsc_code, "status": "error", "error": str(e)})

            # Write results after each item to keep file valid
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)

    # Final save if no output file was specified
    if not output_file:
        output_file = Path(__file__).parent.parent / "lcsc_cart_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

    print(f"\n\nResults saved to {output_file}")
    print(f"Successfully added: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")
    print(f"Failed: {sum(1 for r in results if r['status'] != 'success')}/{len(results)}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Add parts to LCSC shopping cart",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "codes",
        nargs="*",
        help="LCSC product codes (e.g., C137394 C137181)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="File containing LCSC codes (one per line)"
    )
    parser.add_argument(
        "--qty",
        type=int,
        default=100,
        help="Quantity to order for each part (default: 100)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output JSON file for results (default: lcsc_cart_results.json)"
    )

    args = parser.parse_args()

    # Get LCSC codes from arguments or file
    lcsc_codes = []
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            with open(file_path) as f:
                lcsc_codes = [line.strip() for line in f if line.strip()]
        else:
            print(f"Error: File not found: {args.file}")
            return
    elif args.codes:
        lcsc_codes = args.codes
    else:
        parser.print_help()
        return

    if not lcsc_codes:
        print("Error: No LCSC codes provided")
        return

    # Prepare output file path
    output_file = Path(args.output) if args.output else None

    print(f"Adding {len(lcsc_codes)} parts to LCSC cart with quantity {args.qty} each")
    if output_file:
        print(f"Results will be written to: {output_file}")
    asyncio.run(add_parts_to_cart(lcsc_codes, args.qty, output_file))


if __name__ == "__main__":
    main()
