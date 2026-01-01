#!/usr/bin/env python3
"""
Add multiple parts to LCSC shopping cart using real browser session.
This script uses the playwright-real-session-mcp-server to interact with an existing browser session.
Runs in parallel with configurable concurrency control (default: 10 concurrent tabs).

Usage:
    python lcsc_add_to_cart.py <item_spec1> <item_spec2> ... [-o OUTPUT] [-l LOG]
    python lcsc_add_to_cart.py --file codes.txt [-o OUTPUT] [-l LOG]

Item specifications can be:
    - CODE:QTY format (e.g., C137394:100, C137181:50)
    - CODE only (uses default quantity of 100)

Examples:
    # Add 2 parts with specific quantities
    python lcsc_add_to_cart.py C137394:100 C137181:50

    # Add parts with default quantity
    python lcsc_add_to_cart.py C137394 C137181

    # Mix of specific and default quantities
    python lcsc_add_to_cart.py C137394:200 C137181

    # From file (supports CODE or CODE:QTY per line)
    python lcsc_add_to_cart.py --file codes.txt -o results.json -l progress.log
"""
import asyncio
import json
import argparse
import logging
from pathlib import Path
from fastmcp import Client


# Global logger
logger = None
# Global results list with lock for thread safety
results = []
results_lock = asyncio.Lock()


def parse_item_spec(spec: str, default_qty: int = 100):
    """Parse item specification in format CODE or CODE:QTY.

    Args:
        spec: Item specification string (e.g., "C137394" or "C137394:100")
        default_qty: Default quantity if not specified

    Returns:
        Tuple of (code, quantity)
    """
    spec = spec.strip()
    if ':' in spec:
        code, qty_str = spec.split(':', 1)
        return code.strip(), int(qty_str.strip())
    else:
        return spec, default_qty


def setup_logging(log_file: Path = None):
    """Setup logging to console and optionally to file."""
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create formatters
    console_formatter = logging.Formatter('%(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")


async def add_single_part(client: Client, lcsc_code: str, quantity: int, index: int, total: int):
    """Add a single part to LCSC cart."""
    logger.info(f"[{index}/{total}] Starting {lcsc_code} (qty: {quantity})")

    try:
        # Step 1: Navigate to product page
        logger.debug(f"[{lcsc_code}] Navigating to product page...")
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
            error_detail = f"nav_result.data: {nav_result.data}" if nav_result.data else "nav_result.data is None"
            logger.error(f"[{lcsc_code}] Failed to navigate - {error_detail}")
            return {"code": lcsc_code, "status": "failed", "error": f"Navigation failed - {error_detail}"}

        logger.debug(f"[{lcsc_code}] Navigation successful")

        # Step 2: Set the quantity with proper event triggering
        logger.debug(f"[{lcsc_code}] Setting quantity to {quantity}...")
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
            logger.error(f"[{lcsc_code}] Could not set quantity")
            return {"code": lcsc_code, "status": "failed", "error": "Could not set quantity"}

        logger.debug(f"[{lcsc_code}] Quantity set successfully")

        # Step 3: Click the Add To Cart button
        logger.debug(f"[{lcsc_code}] Clicking Add To Cart...")
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
            logger.error(f"[{lcsc_code}] Could not click Add To Cart button")
            return {"code": lcsc_code, "status": "failed", "error": "Could not click button"}

        logger.info(f"[{lcsc_code}] ✓ Successfully added to cart")
        return {"code": lcsc_code, "status": "success"}

    except Exception as e:
        logger.exception(f"[{lcsc_code}] Exception occurred: {str(e)}")
        return {"code": lcsc_code, "status": "error", "error": str(e)}


async def process_part(semaphore: asyncio.Semaphore, client: Client, lcsc_code: str,
                       quantity: int, index: int, total: int, output_file: Path,
                       start_delay: float = 0):
    """Process a single part with semaphore control."""
    # Add staggered start delay to prevent simultaneous navigation
    if start_delay > 0:
        await asyncio.sleep(start_delay)

    async with semaphore:
        result = await add_single_part(client, lcsc_code, quantity, index, total)

        # Add result to global list with lock
        async with results_lock:
            results.append(result)

            # Write results to file after each completion
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)

        return result


async def add_parts_to_cart(items: list, output_file: Path = None,
                            max_concurrent: int = 10):
    """Add parts to LCSC cart in parallel with concurrency control.

    Args:
        items: List of (code, quantity) tuples
        output_file: Path to output JSON file
        max_concurrent: Maximum concurrent browser tabs
    """
    global results
    results = []

    config_path = Path(__file__).parent.parent / ".mcp.json"
    with open(config_path) as f:
        config = json.load(f)

    client = Client(config)

    # Initialize output file with empty array if specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump([], f)

    logger.info(f"Processing {len(items)} parts with max {max_concurrent} concurrent tasks")
    logger.info("=" * 80)

    # Create semaphore to limit concurrent tasks
    semaphore = asyncio.Semaphore(max_concurrent)

    async with client:
        # Create all tasks with staggered start (0.5s delay between each)
        # This prevents ERR_ABORTED errors from simultaneous navigation
        tasks = [
            process_part(semaphore, client, code, qty, i, len(items),
                        output_file, start_delay=i * 0.5)
            for i, (code, qty) in enumerate(items, start=1)
        ]

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

    # Final save if no output file was specified
    if not output_file:
        output_file = Path(__file__).parent.parent / "lcsc_cart_results.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

    logger.info("=" * 80)
    logger.info(f"Results saved to {output_file}")
    logger.info(f"Successfully added: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")
    logger.info(f"Failed: {sum(1 for r in results if r['status'] != 'success')}/{len(results)}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Add parts to LCSC shopping cart (parallel execution)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Item specifications:
  CODE        - Use default quantity (100)
  CODE:QTY    - Use specific quantity

Examples:
  python lcsc_add_to_cart.py C137394:100 C137181:50
  python lcsc_add_to_cart.py --file items.txt -o results.json
        """
    )
    parser.add_argument(
        "items",
        nargs="*",
        help="LCSC items (CODE or CODE:QTY format, e.g., C137394:100 C137181:50)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="File containing LCSC items (CODE or CODE:QTY per line)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output JSON file for results (default: lcsc_cart_results.json)"
    )
    parser.add_argument(
        "-l", "--log",
        type=str,
        help="Log file path (optional, defaults to console only)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=1,
        help="Maximum concurrent browser tabs (default: 1). Do not set this higher than 1 as it will cause ERR_ABORTED errors."
    )

    args = parser.parse_args()

    # Setup logging
    log_file = Path(args.log) if args.log else None
    setup_logging(log_file)

    # Get LCSC item specifications from arguments or file
    item_specs = []
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            with open(file_path) as f:
                item_specs = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            logger.info(f"Loaded {len(item_specs)} items from {args.file}")
        else:
            logger.error(f"File not found: {args.file}")
            return
    elif args.items:
        item_specs = args.items
        logger.info(f"Processing {len(item_specs)} items from command line")
    else:
        parser.print_help()
        return

    if not item_specs:
        logger.error("No LCSC items provided")
        return

    # Parse item specifications into (code, quantity) tuples
    items = []
    for spec in item_specs:
        try:
            code, qty = parse_item_spec(spec)
            items.append((code, qty))
        except ValueError as e:
            logger.error(f"Invalid item specification '{spec}': {e}")
            return

    # Prepare output file path
    output_file = Path(args.output) if args.output else None

    logger.info(f"Adding {len(items)} parts to LCSC cart")
    if output_file:
        logger.info(f"Results will be written to: {output_file}")

    # Run the async function
    asyncio.run(add_parts_to_cart(items, output_file, args.max_concurrent))


if __name__ == "__main__":
    main()
