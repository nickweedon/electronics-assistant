#!/usr/bin/env python3
"""
LCSC cart management tool - supports multiple operations via subcommands.

Subcommands:
    add-to-cart     Add parts to LCSC cart (parallel execution)
    list-cart       List all items currently in the cart

Examples:
    # Add parts to cart
    python lcsc_cart.py add-to-cart C137394:100 C137181:50
    python lcsc_cart.py add-to-cart --file codes.txt -o results.json -l progress.log

    # List cart contents
    python lcsc_cart.py list-cart
    python lcsc_cart.py list-cart -o cart_summary.json
    python lcsc_cart.py list-cart --format table
"""
import asyncio
import json
import argparse
import logging
from pathlib import Path
from fastmcp import Client


# Global logger
logger = None
# Global results list
results = []


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


def load_playwright_config():
    """Load and filter MCP configuration for playwright-real-session-mcp-server.

    Returns:
        Filtered config dict containing only the playwright real session server
    """
    config_path = Path(__file__).parent.parent / ".mcp.json"
    with open(config_path) as f:
        full_config = json.load(f)

    # Filter to only use playwright-real-session-mcp-server
    return {
        "mcpServers": {
            "playwright-real-session-mcp-server": full_config["mcpServers"]["playwright-real-session-mcp-server"]
        }
    }


async def add_single_part(client: Client, lcsc_code: str, quantity: int, index: int, total: int):
    """Add a single part to LCSC cart."""
    logger.info(f"[{index}/{total}] Starting {lcsc_code} (qty: {quantity})")

    try:
        # Step 1: Navigate to product page
        logger.debug(f"[{lcsc_code}] Navigating to product page...")
        nav_result = await client.call_tool(
            "browser_navigate",
            {
                "url": f"https://www.lcsc.com/product-detail/{lcsc_code}.html",
                "silent_mode": True
            }
        )
        await asyncio.sleep(1)

        if not nav_result.data or not nav_result.data.get("success"):
            error_detail = f"nav_result.data: {nav_result.data}" if nav_result.data else "nav_result.data is None"
            logger.error(f"[{lcsc_code}] Failed to navigate - {error_detail}")
            return {"code": lcsc_code, "status": "failed", "error": f"Navigation failed - {error_detail}"}

        logger.debug(f"[{lcsc_code}] Navigation successful")

        # Step 2: Set the quantity with proper event triggering
        logger.debug(f"[{lcsc_code}] Setting quantity to {quantity}...")
        set_qty_result = await client.call_tool(
            "browser_evaluate",
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
        await asyncio.sleep(0.5)

        # Check if quantity was set successfully
        if not _check_success(set_qty_result):
            logger.error(f"[{lcsc_code}] Could not set quantity")
            return {"code": lcsc_code, "status": "failed", "error": "Could not set quantity"}

        logger.debug(f"[{lcsc_code}] Quantity set successfully")

        # Step 3: Click the Add To Cart button
        logger.debug(f"[{lcsc_code}] Clicking Add To Cart...")
        click_result = await client.call_tool(
            "browser_evaluate",
            {
                "function": "() => { const buttons = Array.from(document.querySelectorAll('button')); const addButton = buttons.find(b => b.textContent.includes('Add To Cart')); if (addButton) { addButton.click(); return { success: true, clicked: true }; } return { success: false, error: 'Button not found' }; }"
            }
        )
        await asyncio.sleep(0.5)

        # Check if click was successful
        if not _check_success(click_result):
            logger.error(f"[{lcsc_code}] Could not click Add To Cart button")
            return {"code": lcsc_code, "status": "failed", "error": "Could not click button"}

        logger.info(f"[{lcsc_code}] ✓ Successfully added to cart")
        return {"code": lcsc_code, "status": "success"}

    except Exception as e:
        logger.exception(f"[{lcsc_code}] Exception occurred: {str(e)}")
        return {"code": lcsc_code, "status": "error", "error": str(e)}


def _check_success(result):
    """Check if a browser evaluation result indicates success.

    Args:
        result: CallToolResult from browser_evaluate

    Returns:
        bool: True if successful, False otherwise
    """
    eval_data = str(result.content[0].text) if result.content else ""
    return not ('"success": false' in eval_data or "'success': False" in eval_data)


async def add_parts_to_cart(items: list, output_file: Path = None):
    """Add parts to LCSC cart sequentially.

    Args:
        items: List of (code, quantity) tuples
        output_file: Path to output JSON file
    """
    global results
    results = []

    config = load_playwright_config()
    client = Client(config)

    # Initialize output file with empty array if specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump([], f)

    logger.info(f"Processing {len(items)} parts sequentially")
    logger.info("=" * 80)

    async with client:
        # Process each item sequentially with a small delay between each
        for i, (code, qty) in enumerate(items, start=1):
            result = await add_single_part(client, code, qty, i, len(items))
            results.append(result)

            # Write results to file after each completion
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)

            # Small delay to prevent overwhelming the server
            await asyncio.sleep(0.5)

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


def _extract_cart_data_from_result(result):
    """Extract cart data from browser evaluation result.

    Handles various result formats including double-encoded JSON and markdown blocks.

    Args:
        result: CallToolResult from browser_evaluate

    Returns:
        dict: Parsed cart data or empty structure if parsing fails
    """
    if not result.content:
        return {"items": [], "cartTotal": "N/A", "totalItems": 0}

    result_text = result.content[0].text

    # Check if result_text is a JSON-serialized CallToolResult (double-encoding issue)
    if result_text.startswith('{"content":['):
        logger.info("Detected double-encoded result, extracting nested text")
        outer_data = json.loads(result_text)
        result_text = outer_data['content'][0]['text']

    # Extract JSON from markdown result block
    if "### Result\n{" in result_text:
        json_start = result_text.index("### Result\n{") + len("### Result\n")
        json_end = result_text.index("\n\n###", json_start) if "\n\n###" in result_text[json_start:] else len(result_text)
        json_text = result_text[json_start:json_end]
        return json.loads(json_text)
    else:
        return json.loads(result_text)


async def list_cart_contents(output_file: Path = None, output_format: str = "table"):
    """List all items currently in LCSC cart.

    Args:
        output_file: Optional path to save results as JSON
        output_format: Output format - 'table' or 'json'
    """
    config = load_playwright_config()
    client = Client(config)

    logger.info("Fetching cart contents from LCSC...")

    async with client:
        # Navigate to cart
        await client.call_tool(
            "browser_navigate",
            {
                "url": "https://www.lcsc.com/cart",
                "silent_mode": True
            }
        )
        await asyncio.sleep(2)

        # Extract cart data using JavaScript
        result = await client.call_tool(
            "browser_evaluate",
            {
                "function": """() => {
                    const items = [];
                    const seen = new Set();

                    // Find all product links to identify cart items
                    const productLinks = document.querySelectorAll('a[href*="/product-detail/C"]');

                    productLinks.forEach((link) => {
                        const urlMatch = link.href.match(/C(\\d+)/);
                        if (!urlMatch) return;
                        const lcscCode = 'C' + urlMatch[1];

                        // Skip duplicates and the "View" link
                        if (seen.has(lcscCode) || link.textContent?.trim() === 'View') return;
                        seen.add(lcscCode);

                        // Find the container for this product (walk up the DOM)
                        // We need a container that has BOTH quantity inputs AND pricing info
                        let container = link.parentElement;
                        let depth = 0;
                        while (container && depth < 15) {
                            const hasQuantityInput = container.querySelectorAll('input[type="text"]').length > 0;
                            const hasPricing = container.textContent.includes('Unit Price') && container.textContent.includes('$');

                            if (hasQuantityInput && hasPricing) {
                                break;
                            }

                            container = container.parentElement;
                            depth++;
                        }

                        if (!container) return;

                        // Extract data from the container
                        let mpn = 'N/A';
                        let manufacturer = 'N/A';
                        let description = 'N/A';
                        let quantity = 'N/A';
                        let unitPrice = 'N/A';
                        let extPrice = 'N/A';

                        // Get all text content in order
                        const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null, false);
                        const textNodes = [];
                        let node;
                        while (node = walker.nextNode()) {
                            const text = node.textContent.trim();
                            if (text) textNodes.push(text);
                        }

                        // Find MPN - usually comes right after LCSC code
                        const lcscIndex = textNodes.findIndex(t => t === lcscCode);
                        if (lcscIndex >= 0 && lcscIndex < textNodes.length - 1) {
                            const nextText = textNodes[lcscIndex + 1];
                            if (nextText.match(/^[A-Z0-9][A-Z0-9\\-]+$/) && !nextText.includes('YAGEO')) {
                                mpn = nextText;
                            }
                        }

                        // Find manufacturer link
                        const mfgLink = container.querySelector('a[href*="/brand-detail/"]');
                        if (mfgLink) {
                            manufacturer = mfgLink.textContent.trim();
                        }

                        // Find description - text containing Ω, Resistor, etc.
                        for (const text of textNodes) {
                            if (text.includes('Ω') || text.includes('Resistor') || text.includes('Capacitor') ||
                                text.includes('µF') || text.includes('pF')) {
                                description = text;
                                break;
                            }
                        }

                        // Find quantity input - look for textbox role in ARIA
                        const qtyInputs = container.querySelectorAll('input[type="text"], input[role="textbox"]');
                        for (const input of qtyInputs) {
                            const val = input.value || input.getAttribute('value') || input.getAttribute('aria-valuenow');
                            if (val && val.match(/^\\d+$/)) {
                                quantity = val;
                                break;
                            }
                        }

                        // If still no quantity, try looking for it in the text nodes
                        if (quantity === 'N/A') {
                            // Look for a standalone number that's not part of a price or code
                            for (let i = 0; i < textNodes.length; i++) {
                                const text = textNodes[i];
                                if (text.match(/^\\d{1,4}$/) && !textNodes[i-1]?.includes('$') && !textNodes[i+1]?.includes('$')) {
                                    quantity = text;
                                    break;
                                }
                            }
                        }

                        // Find prices - look for $ followed by digits
                        const pricePattern = /\\$(\\d+\\.\\d{2,})/g;
                        const priceMatches = [];
                        for (const text of textNodes) {
                            const match = text.match(pricePattern);
                            if (match) {
                                priceMatches.push(...match);
                            }
                        }

                        // Typically: first price is unit price, second is extended price
                        if (priceMatches.length >= 2) {
                            unitPrice = priceMatches[0];
                            extPrice = priceMatches[1];
                        } else if (priceMatches.length === 1) {
                            extPrice = priceMatches[0];
                        }

                        items.push({
                            lcscCode,
                            mpn,
                            manufacturer,
                            description,
                            quantity,
                            unitPrice,
                            extPrice
                        });
                    });

                    // Find cart total
                    let cartTotal = 0;
                    const allText = document.body.textContent || '';
                    const totalMatch = allText.match(/Total[:\\s]*\\$([\\d,]+\\.\\d{2})/i);
                    if (totalMatch) {
                        cartTotal = parseFloat(totalMatch[1].replace(/,/g, ''));
                    }

                    return {
                        items,
                        cartTotal: cartTotal > 0 ? `$${cartTotal.toFixed(2)}` : 'N/A',
                        totalItems: items.length
                    };
                }"""
            }
        )

        cart_data = _extract_cart_data_from_result(result)

    # Save to JSON file if requested
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(cart_data, f, indent=2)
        logger.info(f"Cart data saved to {output_file}")

    # Format output
    if output_format == "json":
        print(json.dumps(cart_data, indent=2))
    else:
        # Table format
        _print_cart_table(cart_data)

    return cart_data


def _print_cart_table(cart_data):
    """Print cart data in formatted table.

    Args:
        cart_data: Dictionary containing items, cartTotal, and totalItems
    """
    print("\n" + "=" * 120)
    print(f"LCSC Cart Summary - {cart_data['totalItems']} items")
    print("=" * 120)
    print(f"{'LCSC Code':<12} {'MPN':<20} {'Manufacturer':<15} {'Qty':<8} {'Unit Price':<12} {'Ext Price':<12} Description")
    print("-" * 120)

    for item in cart_data['items']:
        desc = item['description']
        if len(desc) > 30:
            desc = desc[:27] + "..."

        print(f"{item['lcscCode']:<12} {item['mpn']:<20} {item['manufacturer']:<15} "
              f"{item['quantity']:<8} {item['unitPrice']:<12} {item['extPrice']:<12} {desc}")

    print("-" * 120)
    print(f"{'':>85}Cart Total: {cart_data['cartTotal']}")
    print("=" * 120 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="LCSC cart management tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add parts to cart
  python lcsc_cart.py add-to-cart C137394:100 C137181:50
  python lcsc_cart.py add-to-cart --file codes.txt -o results.json

  # List cart contents
  python lcsc_cart.py list-cart
  python lcsc_cart.py list-cart -o cart.json --format json
        """
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # add-to-cart command
    add_parser = subparsers.add_parser(
        "add-to-cart",
        help="Add parts to LCSC shopping cart"
    )
    add_parser.add_argument(
        "items",
        nargs="*",
        help="LCSC items (CODE or CODE:QTY format, e.g., C137394:100 C137181:50)"
    )
    add_parser.add_argument(
        "--file",
        type=str,
        help="File containing LCSC items (CODE or CODE:QTY per line)"
    )
    add_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output JSON file for results (default: lcsc_cart_results.json)"
    )
    add_parser.add_argument(
        "-l", "--log",
        type=str,
        help="Log file path (optional, defaults to console only)"
    )

    # list-cart command
    list_parser = subparsers.add_parser(
        "list-cart",
        help="List all items in LCSC cart"
    )
    list_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output JSON file for cart data (optional)"
    )
    list_parser.add_argument(
        "--format",
        type=str,
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)"
    )
    list_parser.add_argument(
        "-l", "--log",
        type=str,
        help="Log file path (optional, defaults to console only)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Setup logging
    log_file = Path(args.log) if hasattr(args, 'log') and args.log else None
    setup_logging(log_file)

    # Execute command
    if args.command == "add-to-cart":
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
            add_parser.print_help()
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
        asyncio.run(add_parts_to_cart(items, output_file))

    elif args.command == "list-cart":
        output_file = Path(args.output) if args.output else None
        asyncio.run(list_cart_contents(output_file, args.format))


if __name__ == "__main__":
    main()
