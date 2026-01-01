#!/usr/bin/env python3
"""
LCSC management tool - supports multiple operations via subcommands.

Subcommands:
    add-to-cart     Add parts to LCSC cart (sequential execution)
    list-cart       List all items currently in the cart
    open-cart       Open the cart in browser for manual review
    check-pricing   Check pricing and MOQ for LCSC parts (parallel execution)

Examples:
    # Add parts to cart
    python lcsc_tool.py add-to-cart C137394:100 C137181:50
    python lcsc_tool.py add-to-cart --file codes.txt -o results.json -l progress.log

    # List cart contents
    python lcsc_tool.py list-cart
    python lcsc_tool.py list-cart -o cart_summary.json
    python lcsc_tool.py list-cart --format table

    # Open cart in browser
    python lcsc_tool.py open-cart

    # Check pricing
    python lcsc_tool.py check-pricing input.json output.json
    python lcsc_tool.py check-pricing input.json output.json --max-concurrent 20
    python lcsc_tool.py check-pricing mpn_input.json output.json --max-concurrent 1  # For MPN searches
"""
import asyncio
import json
import argparse
import logging
import sys
from pathlib import Path
from fastmcp import Client


# Global logger
logger = None


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

    # Clear existing handlers
    logger.handlers.clear()

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


def load_mcp_config(server_name: str):
    """Load and filter MCP configuration for a specific server.

    Args:
        server_name: Name of the MCP server to filter for

    Returns:
        Filtered config dict containing only the specified server
    """
    config_path = Path(__file__).parent.parent / ".mcp.json"
    with open(config_path) as f:
        full_config = json.load(f)

    # Filter to only use the specified server
    if server_name not in full_config["mcpServers"]:
        raise ValueError(f"Server '{server_name}' not found in .mcp.json")

    return {
        "mcpServers": {
            server_name: full_config["mcpServers"][server_name]
        }
    }


def _check_success(result):
    """Check if a browser evaluation result indicates success.

    Args:
        result: CallToolResult from browser_evaluate

    Returns:
        bool: True if successful, False otherwise
    """
    eval_data = str(result.content[0].text) if result.content else ""
    return not ('"success": false' in eval_data or "'success': False" in eval_data)


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


# ============================================================================
# ADD TO CART FUNCTIONALITY
# ============================================================================

async def add_single_part(client: Client, lcsc_code: str, quantity: int, index: int, total: int):
    """Add a single part to LCSC cart.

    Args:
        client: FastMCP client instance
        lcsc_code: LCSC part code (e.g., "C137394")
        quantity: Quantity to add
        index: Current item index (for progress reporting)
        total: Total number of items

    Returns:
        dict: Result with status and error information if applicable
    """
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


async def add_parts_to_cart(items: list, output_file: Path = None):
    """Add parts to LCSC cart sequentially.

    Args:
        items: List of (code, quantity) tuples
        output_file: Path to output JSON file

    Returns:
        list: Results for each part
    """
    results = []

    config = load_mcp_config("playwright-real-session-mcp-server")
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


# ============================================================================
# LIST CART FUNCTIONALITY
# ============================================================================

async def list_cart_contents(output_file: Path = None, output_format: str = "table"):
    """List all items currently in LCSC cart.

    Args:
        output_file: Optional path to save results as JSON
        output_format: Output format - 'table' or 'json'

    Returns:
        dict: Cart data
    """
    config = load_mcp_config("playwright-real-session-mcp-server")
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


# ============================================================================
# OPEN CART FUNCTIONALITY
# ============================================================================

async def open_cart_in_browser():
    """Open LCSC cart in browser and keep it open for manual review.

    This function navigates to the cart page and keeps the browser session
    active so the user can manually review and interact with the cart.
    """
    config = load_mcp_config("playwright-real-session-mcp-server")
    client = Client(config)

    logger.info("Opening LCSC cart in browser...")
    logger.info("The browser will remain open for you to review the cart.")
    logger.info("Press Ctrl+C when you're done to close this script.")

    async with client:
        # Navigate to cart
        await client.call_tool(
            "browser_navigate",
            {
                "url": "https://www.lcsc.com/cart",
                "silent_mode": True
            }
        )

        logger.info("✓ Cart page loaded successfully")
        logger.info("Browser is ready for your review. Press Ctrl+C to exit.")

        # Keep the script running to maintain the browser session
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nClosing browser session...")


# ============================================================================
# CHECK PRICING FUNCTIONALITY
# ============================================================================

async def fetch_single_part_pricing(client, part: dict, idx: int, total: int, semaphore: asyncio.Semaphore) -> dict:
    """Fetch pricing for a single part with semaphore-controlled concurrency.

    Args:
        client: FastMCP client instance
        part: Part dict with lcsc_code OR mpn (plus optional value)
        idx: Current item index (1-based)
        total: Total number of parts
        semaphore: Asyncio semaphore for concurrency control

    Returns:
        dict: Pricing data or error information
    """
    lcsc_code = part.get("lcsc_code")
    value = part.get("value", "")
    mpn = part.get("mpn", "")

    async with semaphore:
        # Determine if we need to search for the LCSC code first
        if not lcsc_code and mpn:
            print(f"Processing {idx}/{total}: Searching for MPN {mpn}", file=sys.stderr)

            try:
                # Search for the product by MPN
                search_result = await client.call_tool(
                    "browser_execute_bulk",
                    {
                        "commands": [
                            {
                                "tool": "browser_navigate",
                                "args": {
                                    "url": f"https://www.lcsc.com/search?q={mpn}",
                                    "silent_mode": True
                                }
                            },
                            {
                                "tool": "browser_wait_for",
                                "args": {"time": 5}
                            },
                            {
                                "tool": "browser_evaluate",
                                "args": {
                                    "function": "() => { const productLinks = document.querySelectorAll('a[href*=\"/product-detail/C\"]'); if (productLinks.length === 0) return { found: false, message: 'No product links found' }; const firstLink = productLinks[0]; const productUrl = firstLink.href; const productCode = productUrl.match(/C\\d+/)?.[0]; if (!productCode) return { found: false, message: 'Could not extract product code' }; let mpnFound = firstLink.textContent?.trim(); const row = firstLink.closest('tr'); let manufacturer = ''; if (row) { const mfgLink = row.querySelector('a[href*=\"/brand-detail/\"]'); if (mfgLink) manufacturer = mfgLink.textContent?.trim(); } return { found: true, count: 1, results: [{ mpn: mpnFound, lcscCode: productCode, manufacturer, productUrl, productCode }] }; }"
                                },
                                "return_result": True
                            }
                        ],
                        "stop_on_error": True,
                        "return_all_results": False
                    }
                )

                # Extract search results from browser_execute_bulk response
                bulk_results = search_result.data.get("results", [])
                last_result = bulk_results[-1] if bulk_results else None

                # Parse the evaluation result from the text content
                search_data = None
                if last_result and "content" in last_result:
                    content = last_result["content"]
                    if content and len(content) > 0:
                        text_content = content[0].get("text", "")
                        # Extract JSON from the "### Result\n{...}" format
                        if "### Result" in text_content:
                            json_start = text_content.find("{")
                            json_end = text_content.find("\n\n###", json_start)
                            if json_start >= 0:
                                json_str = text_content[json_start:json_end if json_end > 0 else None]
                                try:
                                    search_data = json.loads(json_str)
                                except json.JSONDecodeError:
                                    pass

                if not search_data or not search_data.get("found"):
                    return {
                        "lcsc_code": None,
                        "value": value,
                        "mpn": mpn,
                        "error": "MPN not found in LCSC catalog",
                        "success": False,
                        "index": idx
                    }

                search_results = search_data.get("results", [])
                if not search_results:
                    return {
                        "lcsc_code": None,
                        "value": value,
                        "mpn": mpn,
                        "error": "No matching products found",
                        "success": False,
                        "index": idx
                    }

                # Use the first result
                first_result = search_results[0]
                lcsc_code = first_result.get("lcscCode") or first_result.get("productCode")
                found_mpn = first_result.get("mpn", mpn)
                manufacturer = first_result.get("manufacturer", "")

                if not lcsc_code:
                    return {
                        "lcsc_code": None,
                        "value": value,
                        "mpn": mpn,
                        "error": "Could not extract LCSC code from search results",
                        "success": False,
                        "index": idx
                    }

                print(f"  Found: {lcsc_code} ({found_mpn} by {manufacturer})", file=sys.stderr)

            except Exception as e:
                print(f"Error searching for MPN {mpn}: {e}", file=sys.stderr)
                return {
                    "lcsc_code": None,
                    "value": value,
                    "mpn": mpn,
                    "error": f"Search failed: {str(e)}",
                    "success": False,
                    "index": idx
                }

        # Now fetch pricing with the LCSC code
        if not lcsc_code:
            return {
                "lcsc_code": None,
                "value": value,
                "mpn": mpn,
                "error": "No LCSC code available",
                "success": False,
                "index": idx
            }

        print(f"Processing {idx}/{total}: {lcsc_code} ({value})", file=sys.stderr)

        try:
            result = await client.call_tool(
                "browser_execute_bulk",
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
                        },
                        {
                            "tool": "browser_evaluate",
                            "args": {
                                "function": r"""() => {
                                    // Extract manufacturer
                                    const mfgLink = document.querySelector('a[href*="/brand-detail/"]');
                                    const manufacturer = mfgLink ? mfgLink.textContent.trim() : 'N/A';

                                    // Extract description from meta tag (most reliable)
                                    let description = 'N/A';
                                    const metaDesc = document.querySelector('meta[name="description"]');
                                    if (metaDesc) {
                                        description = metaDesc.getAttribute('content') || 'N/A';
                                    }

                                    // If no meta description, try h1 title
                                    if (description === 'N/A') {
                                        const h1 = document.querySelector('h1');
                                        if (h1) {
                                            description = h1.textContent.trim();
                                        }
                                    }

                                    // Extract stock quantity
                                    let stock = 'N/A';
                                    const bodyText = document.body.textContent || '';

                                    // LCSC shows "In-Stock:" on one line and the number on the next line
                                    const lines = bodyText.split('\n');
                                    for (let i = 0; i < lines.length; i++) {
                                        if (lines[i].includes('In-Stock:')) {
                                            // Check next 3 lines for a number
                                            for (let j = 1; j <= 3 && i + j < lines.length; j++) {
                                                const nextLine = lines[i + j].trim();
                                                const numberMatch = nextLine.match(/^([0-9,]+)$/);
                                                if (numberMatch) {
                                                    stock = numberMatch[1].replace(/,/g, '');
                                                    break;
                                                }
                                            }
                                            break;
                                        }
                                    }

                                    // Fallback: try inline patterns
                                    if (stock === 'N/A') {
                                        const stockPatterns = [
                                            /In Stock[:\\s]+([0-9,]+)/i,
                                            /Stock[:\\s]+([0-9,]+)/i,
                                            /([0-9,]+)\\s*pcs in stock/i
                                        ];

                                        for (const pattern of stockPatterns) {
                                            const match = bodyText.match(pattern);
                                            if (match) {
                                                stock = match[1].replace(/,/g, '');
                                                break;
                                            }
                                        }
                                    }

                                    return {
                                        manufacturer: manufacturer,
                                        description: description,
                                        stock: stock
                                    };
                                }"""
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
            pricing_snapshot = bulk_results[-2] if len(bulk_results) >= 2 else None
            details_result = bulk_results[-1] if bulk_results else None

            # Parse pricing data
            pricing = []
            if pricing_snapshot and "snapshot" in pricing_snapshot:
                pricing = pricing_snapshot["snapshot"]

            # Parse manufacturer, description, and stock
            manufacturer = "N/A"
            description = "N/A"
            stock = "N/A"

            if details_result and "content" in details_result:
                content = details_result["content"]
                if content and len(content) > 0:
                    text_content = content[0].get("text", "")
                    # Extract JSON from the "### Result\n{...}" format
                    if "### Result" in text_content:
                        json_start = text_content.find("{")
                        json_end = text_content.find("\n\n###", json_start)
                        if json_start >= 0:
                            json_str = text_content[json_start:json_end if json_end > 0 else None]
                            try:
                                details_data = json.loads(json_str)
                                manufacturer = details_data.get("manufacturer", "N/A")
                                description = details_data.get("description", "N/A")
                                stock = details_data.get("stock", "N/A")
                            except json.JSONDecodeError:
                                pass

            return {
                "lcsc_code": lcsc_code,
                "value": value,
                "mpn": mpn,
                "manufacturer": manufacturer,
                "description": description,
                "stock": stock,
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
                "manufacturer": "N/A",
                "description": "N/A",
                "stock": "N/A",
                "error": str(e),
                "success": False,
                "index": idx
            }


async def check_lcsc_pricing(parts_list: list, output_file: Path, max_concurrent: int = 15) -> None:
    """Fetch LCSC pricing for all parts in parallel with controlled concurrency.

    Writes results to JSON file incrementally as each part completes.
    Results are sorted by original index to maintain input order in output file.

    Args:
        parts_list: List of part dicts with lcsc_code, value, mpn
        output_file: Path to write results JSON
        max_concurrent: Maximum concurrent requests (default: 15)
    """
    config = load_mcp_config("playwright-mcp-server")
    client = Client(config)

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)

    # Track all results by index
    results_dict = {}
    completed_count = 0

    # Initialize the output file with empty array
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump([], f)

    logger.info(f"Starting to process {len(parts_list)} parts with max {max_concurrent} concurrent requests")
    logger.info(f"Results will be written incrementally to: {output_file}")

    def write_current_results():
        """Write all completed results in index order to file."""
        # Sort results by index and remove index field
        sorted_results = []
        for idx in sorted(results_dict.keys()):
            entry = results_dict[idx]
            entry_clean = {k: v for k, v in entry.items() if k != "index"}
            sorted_results.append(entry_clean)

        # Write to file
        with open(output_file, 'w') as f:
            json.dump(sorted_results, f, indent=2)

    async with client:
        # Create all tasks
        tasks = [
            fetch_single_part_pricing(client, part, idx + 1, len(parts_list), semaphore)
            for idx, part in enumerate(parts_list)
        ]

        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            result = await coro
            idx = result.get("index", 0) - 1  # Convert 1-based to 0-based
            results_dict[idx] = result
            completed_count += 1

            # Log completion
            status = "✓" if result.get("success") else "✗"
            lcsc_code = result.get("lcsc_code", "N/A")
            value = result.get("value", "")
            logger.info(f"{status} [{completed_count}/{len(parts_list)}] {lcsc_code} ({value})")

            # Write all completed results to file after each completion
            write_current_results()

    logger.info(f"✓ All parts processed. Results saved to {output_file}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="LCSC management tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add parts to cart
  python lcsc_tool.py add-to-cart C137394:100 C137181:50
  python lcsc_tool.py add-to-cart --file codes.txt -o results.json

  # List cart contents
  python lcsc_tool.py list-cart
  python lcsc_tool.py list-cart -o cart.json --format json

  # Open cart in browser
  python lcsc_tool.py open-cart

  # Check pricing
  python lcsc_tool.py check-pricing input.json output.json
  python lcsc_tool.py check-pricing input.json output.json --max-concurrent 20
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

    # open-cart command
    open_parser = subparsers.add_parser(
        "open-cart",
        help="Open LCSC cart in browser for manual review"
    )
    open_parser.add_argument(
        "-l", "--log",
        type=str,
        help="Log file path (optional, defaults to console only)"
    )

    # check-pricing command
    pricing_parser = subparsers.add_parser(
        "check-pricing",
        help="Check pricing and MOQ for LCSC parts"
    )
    pricing_parser.add_argument(
        "input_file",
        type=str,
        help="Input JSON file with parts (format: [{\"lcsc_code\": \"C137394\"} or {\"mpn\": \"RC1206FR-070RL\"}, optional \"value\": \"0Ω\"])"
    )
    pricing_parser.add_argument(
        "output_file",
        type=str,
        help="Output JSON file for pricing results"
    )
    pricing_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=15,
        help="Maximum concurrent requests (default: 15, use 1 for MPN searches for better reliability)"
    )
    pricing_parser.add_argument(
        "-l", "--log",
        type=str,
        help="Log file path (optional, defaults to console only)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Setup logging for commands that support it
    if hasattr(args, 'log'):
        log_file = Path(args.log) if args.log else None
        setup_logging(log_file)
    else:
        setup_logging()

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

    elif args.command == "open-cart":
        asyncio.run(open_cart_in_browser())

    elif args.command == "check-pricing":
        input_file = Path(args.input_file)
        output_file = Path(args.output_file)

        # Load input data
        with open(input_file) as f:
            parts_list = json.load(f)

        max_concurrent = args.max_concurrent
        logger.info(f"Loaded {len(parts_list)} parts from {input_file}")
        logger.info(f"Max concurrent requests: {max_concurrent}")
        logger.info("")

        # Fetch pricing in parallel (writes to output_file incrementally)
        asyncio.run(check_lcsc_pricing(parts_list, output_file, max_concurrent))

        # Load results to generate summary
        with open(output_file) as f:
            results = json.load(f)

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"Summary:")
        logger.info(f"  Total processed: {len(results)}")
        logger.info(f"  Successful: {sum(1 for r in results if r.get('success'))}")
        logger.info(f"  Failed: {sum(1 for r in results if not r.get('success'))}")
        logger.info(f"  Results file: {output_file}")
        logger.info("=" * 80)


if __name__ == "__main__":
    main()
