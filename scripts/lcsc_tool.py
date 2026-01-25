#!/usr/bin/env python3
"""
LCSC management tool - supports multiple operations via subcommands.

Subcommands:
    add-to-cart     Add parts to LCSC cart (sequential, uses real browser session)
    list-cart       List all items currently in the cart
    open-cart       Open the cart in browser for manual review
    check-pricing   Check pricing and MOQ for LCSC parts (parallel execution)
    search          Search LCSC catalog by keyword/specs (parallel execution)
    create-bom-file Create LCSC BOM CSV file from part codes and quantities

Concurrency:
    The check-pricing and search commands use a dynamically created browser pool
    with isolated instances, enabling safe concurrent requests. Use --max-concurrent
    to control the number of parallel browser instances (default: 5).

Examples:
    # Add parts to cart (uses real browser session for login state)
    python lcsc_tool.py add-to-cart C137394:100 C137181:50
    python lcsc_tool.py add-to-cart --file codes.txt -o results.json -l progress.log

    # List cart contents
    python lcsc_tool.py list-cart
    python lcsc_tool.py list-cart -o cart_summary.json
    python lcsc_tool.py list-cart --format table

    # Open cart in browser
    python lcsc_tool.py open-cart

    # Check pricing (with concurrency)
    python lcsc_tool.py check-pricing input.json output.json
    python lcsc_tool.py check-pricing input.json output.json --max-concurrent 3

    # Search catalog (with concurrency)
    python lcsc_tool.py search input.json output.json
    python lcsc_tool.py search input.json output.json --max-concurrent 10
    python lcsc_tool.py search -s "1206 resistor 10k"  # Output to stdout (quiet by default)
    python lcsc_tool.py search -s "1206 resistor 10k" --verbose  # Show progress messages
    python lcsc_tool.py search -s "1206 resistor 10k" 2>/dev/null  # Clean JSON only (suppress MCP logs)
    python lcsc_tool.py search -s "capacitor 10uF" output.json  # Save to file

    # Create BOM file (using MPNs)
    python lcsc_tool.py create-bom-file RC1206FR-071RL:100 RC1206FR-070RL:50 -o bom.csv
    python lcsc_tool.py create-bom-file --file mpns.txt -o bom.csv

    # Create BOM file (using LCSC codes for guaranteed matching)
    python lcsc_tool.py create-bom-file --file lcsc_codes.txt -o bom.csv --lcsc-codes
"""
import asyncio
import json
import argparse
import logging
import sys
import csv
import os
import contextlib
from pathlib import Path
from urllib.parse import quote_plus
from fastmcp import Client


# Global logger
logger = None


@contextlib.contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output."""
    stderr_fd = sys.stderr.fileno()
    # Save the original stderr file descriptor
    with os.fdopen(os.dup(stderr_fd), 'wb') as old_stderr:
        # Open /dev/null for writing
        with open(os.devnull, 'wb') as devnull:
            # Redirect stderr to /dev/null
            os.dup2(devnull.fileno(), stderr_fd)
            try:
                yield
            finally:
                # Restore stderr
                os.dup2(old_stderr.fileno(), stderr_fd)


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


def create_isolated_mcp_config(num_instances: int = 5) -> dict:
    """Create MCP config for isolated browser pool with specified instance count.

    This generates a self-contained MCP configuration that runs playwright in Docker
    with the specified number of isolated browser instances. Each instance can handle
    concurrent requests without interference.

    Args:
        num_instances: Number of browser instances to create (default: 5)

    Returns:
        MCP configuration dict for use with fastmcp.Client
    """
    return {
        "mcpServers": {
            "playwright-mcp-server": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "-v", "/mnt/c/docker/blob-storage:/mnt/blob-storage",
                    "-e", "BLOB_STORAGE_ROOT=/mnt/blob-storage",
                    "-e", "BLOB_MAX_SIZE_MB=2048",
                    "-e", "BLOB_TTL_HOURS=24",
                    "-e", "BLOB_SIZE_THRESHOLD_KB=50",
                    "-e", "BLOB_CLEANUP_INTERVAL_MINUTES=60",
                    "-e", "PW_MCP_PROXY_TIMEOUT_ACTION=15000",
                    "-e", "PW_MCP_PROXY_TIMEOUT_NAVIGATION=5000",
                    "-e", f"PW_MCP_PROXY__ISOLATED_INSTANCES={num_instances}",
                    "-e", "PW_MCP_PROXY__ISOLATED_IS_DEFAULT=true",
                    "-e", "PW_MCP_PROXY__ISOLATED_BROWSER=chrome",
                    "-e", "PW_MCP_PROXY__ISOLATED_HEADLESS=true",
                    "-e", "PW_MCP_PROXY__ISOLATED_NO_SANDBOX=true",
                    "-e", "PW_MCP_PROXY__ISOLATED_ISOLATED=true",
                    "-e", "PW_MCP_PROXY__ISOLATED_VIEWPORT_SIZE=1920x1080",
                    "-e", "PW_MCP_PROXY__ISOLATED_ENABLE_STEALTH=true",
                    "playwright-proxy-mcp:latest",
                    "uv", "run", "playwright-proxy-mcp"
                ]
            }
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

async def fetch_single_part_pricing(client, part: dict, idx: int, total: int, semaphore: asyncio.Semaphore, max_retries: int = 3) -> dict:
    """Fetch pricing for a single part with semaphore-controlled concurrency and retry logic.

    Args:
        client: FastMCP client instance
        part: Part dict with lcsc_code OR mpn (plus optional value)
        idx: Current item index (1-based)
        total: Total number of parts
        semaphore: Asyncio semaphore for concurrency control
        max_retries: Maximum number of retry attempts for transient failures (default: 3)

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
                # Search using direct API call (much faster than UI navigation)
                # Need to navigate to LCSC first to establish session
                search_body = {
                    "keyword": mpn,
                    "catalogIdList": [],
                    "brandIdList": [],
                    "encapValueList": [],
                    "isStock": False,  # Search all products, not just in-stock
                    "isOtherSuppliers": False,
                    "isAsianBrand": False,
                    "isDeals": False,
                    "isEnvironment": False,
                    "paramNameValueMap": {},
                    "currentPage": 1,
                    "pageSize": 5  # Only need first few results
                }

                # First navigate to LCSC to establish session, then make API call
                search_result = await client.call_tool(
                    "browser_execute_bulk",
                    {
                        "commands": [
                            {
                                "tool": "browser_navigate",
                                "args": {
                                    "url": "https://www.lcsc.com",
                                    "silent_mode": True
                                }
                            },
                            {
                                "tool": "browser_wait_for",
                                "args": {"time": 2}
                            },
                            {
                                "tool": "browser_run_code",
                                "args": {
                                    "code": f"""
                                    async (page) => {{
                                        const response = await page.evaluate(async () => {{
                                            const res = await fetch('https://wmsc.lcsc.com/ftps/wm/product/query/list', {{
                                                method: 'POST',
                                                headers: {{
                                                    'Content-Type': 'application/json;charset=UTF-8',
                                                    'Accept': 'application/json, text/plain, */*'
                                                }},
                                                body: JSON.stringify({json.dumps(search_body)})
                                            }});
                                            return await res.json();
                                        }});
                                        return response;
                                    }}
                                    """
                                },
                                "return_result": True
                            }
                        ],
                        "stop_on_error": True,
                        "return_all_results": False
                    }
                )

                # Extract search results from browser_execute_bulk response
                search_data = None
                if hasattr(search_result, 'data') and search_result.data:
                    results = search_result.data.get("results", [])
                    if results and len(results) > 0:
                        # The browser_run_code result is the last item
                        code_result = results[-1]
                        if code_result and "content" in code_result:
                            content = code_result["content"]
                            if content and len(content) > 0:
                                content_item = content[0]
                                if isinstance(content_item, dict) and 'text' in content_item:
                                    text = content_item['text']
                                    # Extract JSON from "### Result\n{...}" format
                                    if "### Result" in text:
                                        json_start = text.find("{", text.find("### Result"))
                                        json_end = text.find("\n\n###", json_start)
                                        if json_start >= 0:
                                            json_str = text[json_start:json_end if json_end > 0 else None]
                                            try:
                                                search_data = json.loads(json_str)
                                            except json.JSONDecodeError as e:
                                                print(f"  JSON parse error: {e}", file=sys.stderr)

                if not search_data or search_data.get("code") != 200:
                    return {
                        "lcsc_code": None,
                        "value": value,
                        "mpn": mpn,
                        "error": "MPN search API request failed",
                        "success": False,
                        "index": idx
                    }

                result_data = search_data.get("result", {})
                products = result_data.get("dataList", [])

                if not products or result_data.get("totalRow", 0) == 0:
                    return {
                        "lcsc_code": None,
                        "value": value,
                        "mpn": mpn,
                        "error": "No matching products found",
                        "success": False,
                        "index": idx
                    }

                # Use the first result
                first_product = products[0]
                lcsc_code = first_product.get("productCode")
                found_mpn = first_product.get("productModel", mpn)
                manufacturer = first_product.get("brandNameEn", "")

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

        # Retry loop for transient failures
        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                # Navigate and wait for page to fully load (SPA needs 6+ seconds)
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
                                    "time": 6
                                }
                            },
                            {
                                "tool": "browser_evaluate",
                                "args": {
                                    "function": """() => {
                                    // Extract all product information in one comprehensive pass
                                    const bodyText = document.body.innerText || document.body.textContent || '';

                                    // Extract manufacturer - use structured field approach
                                    let manufacturer = 'N/A';

                                    // Look for "Manufacturer" followed by tab/newline and the value
                                    const mfgPatterns = [
                                        /Manufacturer[\\t\\s]*\\n+([A-Za-z][A-Za-z0-9\\s&\\-,.'()]+?)(?:\\n|Asian Brands|$)/i,
                                        /Manufacturer[:\\t\\s]+([A-Za-z][A-Za-z0-9\\s&\\-,.'()]+?)(?:\\t|\\n|$)/i
                                    ];

                                    for (const pattern of mfgPatterns) {
                                        const match = bodyText.match(pattern);
                                        if (match) {
                                            manufacturer = match[1].trim();
                                            // Remove trailing "Asian Brands" or similar suffixes
                                            manufacturer = manufacturer.replace(/\\s+(Asian|European|American)\\s+Brands.*$/i, '').trim();
                                            break;
                                        }
                                    }

                                    // Extract MPN - look for "Mfr. Part #" field
                                    let mpn = '';
                                    const mpnPatterns = [
                                        /Mfr\\.?\\s*Part\\s*#[:\\t\\s]*\\n*([A-Z0-9][A-Z0-9\\-_./+]+)/i,
                                        /Part\\s*Number[:\\t\\s]*\\n*([A-Z0-9][A-Z0-9\\-_./+]+)/i,
                                        /MPN[:\\t\\s]*\\n*([A-Z0-9][A-Z0-9\\-_./+]+)/i
                                    ];

                                    for (const pattern of mpnPatterns) {
                                        const match = bodyText.match(pattern);
                                        if (match) {
                                            mpn = match[1].trim();
                                            break;
                                        }
                                    }

                                    // Extract description - prioritize structured fields
                                    let description = 'N/A';

                                    // Method 1: Look for "Description" field in product specs
                                    const descMatch = bodyText.match(/Description[:\\t\\s]*\\n*([^\\n]{20,200})/i);
                                    if (descMatch) {
                                        description = descMatch[1].trim();
                                    }

                                    // Method 2: Look for "Key Attributes" field
                                    if (description === 'N/A') {
                                        const keyAttrMatch = bodyText.match(/Key Attributes[:\\t\\s]*\\n*([^\\n]{20,200})/i);
                                        if (keyAttrMatch) {
                                            description = keyAttrMatch[1].trim();
                                        }
                                    }

                                    // Method 3: Meta description tag
                                    if (description === 'N/A') {
                                        const metaDesc = document.querySelector('meta[name=\"description\"]');
                                        if (metaDesc && metaDesc.content) {
                                            description = metaDesc.content.trim();
                                        }
                                    }

                                    // Method 4: H1 title
                                    if (description === 'N/A') {
                                        const h1 = document.querySelector('h1');
                                        if (h1) {
                                            description = h1.textContent.trim();
                                        }
                                    }

                                    // Extract stock - look for stock information
                                    let stock = 'N/A';
                                    const stockPatterns = [
                                        /In[- ]?Stock:?[\\t\\s]*([0-9,]+)/i,
                                        /Stock:?[\\t\\s]*([0-9,]+)/i,
                                        /([0-9,]+)\\s*(?:pcs|pieces|units)\\s*(?:in|available)/i,
                                        /Stock\\s*Qty[.:]?[\\t\\s]*([0-9,]+)/i,
                                        /Available[:\\t\\s]+([0-9,]+)/i
                                    ];

                                    for (const pattern of stockPatterns) {
                                        const match = bodyText.match(pattern);
                                        if (match) {
                                            stock = match[1].replace(/,/g, '');
                                            break;
                                        }
                                    }

                                    // Check for out-of-stock indicators and return 0 instead of N/A
                                    if (stock === 'N/A') {
                                        const outOfStockPatterns = [
                                            /out\\s*of\\s*stock/i,
                                            /sold\\s*out/i,
                                            /unavailable/i,
                                            /no\\s*stock/i,
                                            /stock:\\s*0\\b/i,
                                            /in-stock:\\s*0\\b/i
                                        ];
                                        for (const pattern of outOfStockPatterns) {
                                            if (bodyText.match(pattern)) {
                                                stock = '0';
                                                break;
                                            }
                                        }
                                    }

                                    // Extract pricing table - look for pricing information
                                    const pricingRows = [];
                                    const priceTables = document.querySelectorAll('table');

                                    for (const table of priceTables) {
                                        const tableText = table.innerText;
                                        // Look for pricing table indicators
                                        if (tableText.includes('Unit Price') || (tableText.includes('Qty') && tableText.includes('$'))) {
                                            const rows = table.querySelectorAll('tr');
                                            for (const row of rows) {
                                                const cells = row.querySelectorAll('td');
                                                if (cells.length >= 2) {
                                                    const qty = cells[0].textContent.trim();
                                                    const price = cells[1].textContent.trim();

                                                    // Only add if qty looks like a number and price has $
                                                    if (qty.match(/^\\d+/) && price.includes('$')) {
                                                        pricingRows.push({
                                                            qty: qty,
                                                            unit_price: price,
                                                            ext_price: cells.length >= 3 ? cells[2].textContent.trim() : ''
                                                        });
                                                    }
                                                }
                                            }
                                            // Only use first pricing table found
                                            if (pricingRows.length > 0) break;
                                        }
                                    }

                                    return {
                                        manufacturer: manufacturer,
                                        mpn: mpn,
                                        description: description,
                                        stock: stock,
                                        pricing: pricingRows
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

                # Extract data from the result
                bulk_results = result.data.get("results", [])

                # Results order: [navigate, wait_for, browser_evaluate]
                # With return_all_results=False, results array still has all positions but
                # only commands with return_result=True have actual data (others are null)
                # browser_evaluate is at index 2 (third command)
                page_scrape_result = bulk_results[2] if len(bulk_results) >= 3 else None

                # Initialize with defaults
                manufacturer = "N/A"
                found_mpn = mpn  # Keep original MPN if not found on page
                description = "N/A"
                stock = "N/A"
                pricing = []

                # Parse the browser_evaluate result
                if page_scrape_result and "content" in page_scrape_result:
                    content = page_scrape_result["content"]
                    if content and len(content) > 0:
                        text_content = content[0].get("text", "")
                        if "### Result" in text_content:
                            json_start = text_content.find("{")
                            # Look for the end of JSON - either "\n###" or end of string
                            json_end = text_content.find("\n###", json_start)
                            if json_start >= 0:
                                json_str = text_content[json_start:json_end if json_end > 0 else len(text_content)].strip()
                                try:
                                    details_data = json.loads(json_str)
                                    manufacturer = details_data.get("manufacturer", "N/A")
                                    page_mpn = details_data.get("mpn", "")
                                    if page_mpn:
                                        found_mpn = page_mpn
                                    else:
                                        found_mpn = mpn  # Keep original if not found
                                    description = details_data.get("description", "N/A")
                                    stock = details_data.get("stock", "N/A")
                                    pricing = details_data.get("pricing", [])
                                except json.JSONDecodeError as e:
                                    print(f"  JSON parse error for {lcsc_code}: {e}", file=sys.stderr)
                                    print(f"  Attempted to parse: {json_str[:500]}", file=sys.stderr)
                                    # Keep defaults if parsing fails

                # Validate that we got meaningful data - check if key fields are populated
                # If MPN is empty AND manufacturer is N/A AND no pricing, treat as transient failure
                has_mpn = found_mpn and found_mpn != mpn  # Got a new MPN from the page
                has_manufacturer = manufacturer and manufacturer != "N/A"
                has_pricing = len(pricing) > 0
                has_description = description and description != "N/A"

                if not has_mpn and not has_manufacturer and not has_pricing and not has_description:
                    # No meaningful data extracted - likely a page load failure
                    if attempt < max_retries:
                        print(f"  Attempt {attempt}/{max_retries} failed: No data extracted, retrying...", file=sys.stderr)
                        await asyncio.sleep(2)  # Wait before retry
                        continue  # Retry
                    else:
                        # All retries exhausted
                        return {
                            "lcsc_code": lcsc_code,
                            "value": value,
                            "mpn": mpn,
                            "manufacturer": "N/A",
                            "description": "N/A",
                            "stock": "0",
                            "pricing": [],
                            "error": "Failed to extract product data after multiple attempts",
                            "success": False,
                            "index": idx
                        }

                # Convert stock "N/A" to "0" for consistency (out-of-stock items)
                if stock == "N/A":
                    stock = "0"

                return {
                    "lcsc_code": lcsc_code,
                    "value": value,
                    "mpn": found_mpn,
                    "manufacturer": manufacturer,
                    "description": description,
                    "stock": stock,
                    "pricing": pricing,
                    "success": True,
                    "index": idx
                }

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    print(f"  Attempt {attempt}/{max_retries} failed: {e}, retrying...", file=sys.stderr)
                    await asyncio.sleep(2)  # Wait before retry
                    continue  # Retry
                else:
                    print(f"Error processing {lcsc_code} after {max_retries} attempts: {e}", file=sys.stderr)

        # All retries exhausted due to exceptions
        return {
            "lcsc_code": lcsc_code,
            "value": value,
            "mpn": mpn,
            "manufacturer": "N/A",
            "description": "N/A",
            "stock": "0",
            "error": last_error or "Unknown error after retries",
            "success": False,
            "index": idx
        }


async def check_lcsc_pricing(parts_list: list, output_file: Path, max_concurrent: int = 5) -> None:
    """Fetch LCSC pricing for all parts with concurrent browser instances.

    Writes results to JSON file incrementally as each part completes.
    Results are sorted by original index to maintain input order in output file.

    Uses a dynamically created browser pool with the specified number of isolated
    instances, enabling safe concurrent requests without race conditions.

    Args:
        parts_list: List of part dicts with lcsc_code, value, mpn
        output_file: Path to write results JSON
        max_concurrent: Maximum concurrent browser instances (default: 5)
    """
    # Create isolated browser pool with the specified number of instances
    config = create_isolated_mcp_config(max_concurrent)
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

    logger.info(f"Starting to process {len(parts_list)} parts with {max_concurrent} concurrent browser instances")
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
# SEARCH FUNCTIONALITY
# ============================================================================

async def search_single_product(client: Client, search_spec: dict, idx: int, total: int, semaphore: asyncio.Semaphore, limit: int = None, quiet: bool = False) -> dict:
    """Search LCSC catalog for a product matching the specification with pagination support.

    Args:
        client: FastMCP client instance
        search_spec: Dict with search parameters (e.g., {"keywords": "1206 1% 1Ω resistor", "value": "1Ω"})
        idx: Current item index (1-based)
        total: Total number of searches
        semaphore: Asyncio semaphore for concurrency control
        limit: Maximum number of results to return (None = all results up to 5000)
        quiet: If True, suppress progress messages (default: False)

    Returns:
        dict: Search results with matching products or error information
    """
    keywords = search_spec.get("keywords", "")
    value = search_spec.get("value", "")

    if not keywords:
        return {
            "keywords": keywords,
            "value": value,
            "error": "No keywords provided",
            "success": False,
            "products": [],
            "index": idx
        }

    async with semaphore:
        if not quiet:
            print(f"Processing {idx}/{total}: Searching for '{keywords}'", file=sys.stderr)

        try:
            # Navigate and wait for page to load
            nav_result = await client.call_tool(
                "browser_navigate",
                {
                    "url": f"https://www.lcsc.com/search?q={quote_plus(keywords)}",
                    "silent_mode": True
                }
            )

            # Extract browser_instance from navigation result to ensure subsequent calls use the same instance
            browser_instance = None
            if hasattr(nav_result, 'data') and nav_result.data and 'browser_instance' in nav_result.data:
                browser_instance = nav_result.data['browser_instance']

            await asyncio.sleep(5)

            # Use browser_run_code to paginate with proper context separation
            # State (seen Set, allProducts) stays in Node.js context
            # Product extraction happens in browser context via page.evaluate
            max_products = limit if limit else 5000
            run_code_args = {
                "code": f"""async (page) => {{
                        const maxProducts = {max_products};
                        const allProducts = [];
                        const seen = new Set();

                        // Extract products from current page (runs in browser context)
                        async function extractCurrentPage() {{
                            return await page.evaluate(() => {{
                                const productLinks = document.querySelectorAll('a[href*="/product-detail/C"]');
                                let pageProducts = [];

                                productLinks.forEach((link) => {{
                                    const productUrl = link.href;
                                    const productCode = productUrl.match(/C\\d+/)?.[0];
                                    if (!productCode) return;

                                    let mpn = link.textContent?.trim();
                                    const row = link.closest('tr');
                                    let manufacturer = '';
                                    let description = '';
                                    let stock = '';
                                    let price = '';

                                    if (row) {{
                                        const mfgLink = row.querySelector('a[href*="/brand-detail/"]');
                                        if (mfgLink) manufacturer = mfgLink.textContent?.trim();

                                        const stockButtons = row.querySelectorAll('button');
                                        for (const btn of stockButtons) {{
                                            const text = btn.textContent?.trim();
                                            if (text && text.match(/^[\\d,]+$/)) {{
                                                stock = text.replace(/,/g, '');
                                                break;
                                            }}
                                        }}

                                        const cells = row.querySelectorAll('td');
                                        for (const cell of cells) {{
                                            const text = cell.textContent?.trim();
                                            if (text && text.length > 30 && (text.includes('Ω') || text.includes('Resistor') || text.includes('Capacitor'))) {{
                                                description = text;
                                                break;
                                            }}
                                        }}

                                        const priceRows = row.querySelectorAll('table tr');
                                        for (const priceRow of priceRows) {{
                                            const priceCells = priceRow.querySelectorAll('td');
                                            if (priceCells.length >= 2) {{
                                                const priceText = priceCells[1].textContent?.trim();
                                                if (priceText && priceText.startsWith('$')) {{
                                                    price = priceText;
                                                    break;
                                                }}
                                            }}
                                        }}
                                    }}

                                    pageProducts.push({{
                                        mpn,
                                        lcscCode: productCode,
                                        manufacturer,
                                        description,
                                        stock,
                                        price,
                                        productUrl
                                    }});
                                }});

                                return pageProducts;
                            }});
                        }}

                        // Click next page button and wait (runs in Node.js context)
                        async function goToNextPage() {{
                            try {{
                                const hasNext = await page.evaluate(() => {{
                                    const currentActive = document.querySelector('button.v-pagination__item--active');
                                    if (!currentActive) return false;
                                    const currentPage = parseInt(currentActive.textContent.trim());

                                    const nextButtons = Array.from(document.querySelectorAll('button.v-pagination__item')).filter(btn => {{
                                        const btnPage = parseInt(btn.textContent.trim());
                                        return btnPage === currentPage + 1;
                                    }});

                                    if (nextButtons.length > 0) {{
                                        nextButtons[0].click();
                                        return true;
                                    }}
                                    return false;
                                }});

                                if (hasNext) {{
                                    await page.waitForTimeout(3000);  // Wait for page to update
                                    return true;
                                }}
                                return false;
                            }} catch (e) {{
                                return false;
                            }}
                        }}

                        // Extract first page
                        let pageProducts = await extractCurrentPage();

                        // Deduplicate in Node.js context
                        for (const product of pageProducts) {{
                            if (!seen.has(product.lcscCode)) {{
                                seen.add(product.lcscCode);
                                allProducts.push(product);
                            }}
                        }}

                        // Keep paginating while we have products and haven't hit limit
                        let pageCount = 1;
                        while (allProducts.length < maxProducts && pageCount < 200) {{
                            const hasNext = await goToNextPage();
                            if (!hasNext) break;

                            pageProducts = await extractCurrentPage();
                            if (pageProducts.length === 0) break;

                            // Deduplicate in Node.js context
                            for (const product of pageProducts) {{
                                if (!seen.has(product.lcscCode)) {{
                                    seen.add(product.lcscCode);
                                    allProducts.push(product);
                                    if (allProducts.length >= maxProducts) break;
                                }}
                            }}

                            pageCount++;
                        }}

                        // Trim to limit and return
                        return allProducts.slice(0, maxProducts);
                    }}"""
            }
            # Add browser_instance if we captured one from navigation
            if browser_instance:
                run_code_args["browser_instance"] = browser_instance

            code_result = await client.call_tool(
                "browser_run_code",
                run_code_args
            )

            # Parse the result from browser_run_code
            # The result is in .content[0].text as a markdown-formatted string
            # containing: "### Result\n[...json array...]\n### Ran Playwright code\n..."
            all_products = []
            if code_result.content:
                content = code_result.content
                if content and len(content) > 0:
                    text = content[0].text

                    # Check if result is double-encoded (JSON-serialized CallToolResult)
                    if text.startswith('{"content":['):
                        outer_data = json.loads(text)
                        text = outer_data['content'][0]['text']

                    # Extract JSON array from markdown text
                    # Format: "### Result\n[...]\n### Ran Playwright code\n..."
                    # Note: Only ONE newline between result and the "Ran Playwright code" section
                    import re
                    match = re.search(r'### Result\n(\[.*?\])\n### Ran Playwright code', text, re.DOTALL)
                    if match:
                        all_products = json.loads(match.group(1))
                        if not isinstance(all_products, list):
                            all_products = [all_products] if all_products else []

            if not all_products:
                return {
                    "keywords": keywords,
                    "value": value,
                    "total_found": 0,
                    "success": True,
                    "products": [],
                    "index": idx
                }

            if not quiet:
                logger.info(f"✓ [{idx}/{total}] Found {len(all_products)} products for '{keywords}'")

            return {
                "keywords": keywords,
                "value": value,
                "products": all_products,
                "total_found": len(all_products),
                "success": True,
                "index": idx
            }

        except Exception as e:
            if not quiet:
                logger.error(f"✗ [{idx}/{total}] Error searching for '{keywords}': {e}")
            return {
                "keywords": keywords,
                "value": value,
                "error": str(e),
                "success": False,
                "products": [],
                "index": idx
            }


async def search_lcsc_catalog(search_specs: list, output_file: Path = None, limit: int = None, max_concurrent: int = 5, quiet: bool = False) -> list:
    """Search LCSC catalog for multiple products with concurrent browser instances.

    Optionally writes results to JSON file incrementally as each search completes.
    Results are sorted by original index to maintain input order.

    Uses a dynamically created browser pool with the specified number of isolated
    instances, enabling safe concurrent searches without interference.

    Args:
        search_specs: List of search specification dicts with keywords and optional value
        output_file: Optional path to write results JSON (if None, results only returned)
        limit: Maximum number of results per search (None = all results)
        max_concurrent: Maximum concurrent browser instances (default: 5)
        quiet: If True, suppress all progress and logging messages (default: False)

    Returns:
        list: Search results sorted by original index
    """
    # Create isolated browser pool with the specified number of instances
    config = create_isolated_mcp_config(max_concurrent)

    # In quiet mode, suppress stderr to hide MCP server startup messages
    stderr_context = suppress_stderr() if quiet else contextlib.nullcontext()

    with stderr_context:
        client = Client(config)

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)

        # Track all results by index
        results_dict = {}
        completed_count = 0

        # Initialize the output file with empty array if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump([], f)

        if not quiet:
            logger.info(f"Starting to search for {len(search_specs)} products with {max_concurrent} concurrent browser instances")
            if output_file:
                logger.info(f"Results will be written incrementally to: {output_file}")

        def write_current_results():
            """Write all completed results in index order to file."""
            # Sort results by index and remove index field
            sorted_results = []
            for idx in sorted(results_dict.keys()):
                entry = results_dict[idx]
                entry_clean = {k: v for k, v in entry.items() if k != "index"}
                sorted_results.append(entry_clean)

            # Write to file if output_file specified
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(sorted_results, f, indent=2)

            return sorted_results

        async with client:
            # Create all tasks
            tasks = [
                search_single_product(client, spec, idx + 1, len(search_specs), semaphore, limit, quiet)
                for idx, spec in enumerate(search_specs)
            ]

            # Process results as they complete
            for coro in asyncio.as_completed(tasks):
                result = await coro
                idx = result.get("index", 0) - 1  # Convert 1-based to 0-based
                results_dict[idx] = result
                completed_count += 1

                # Write all completed results to file after each completion
                write_current_results()

        final_results = write_current_results()

        if not quiet:
            if output_file:
                logger.info(f"✓ All searches processed. Results saved to {output_file}")
            else:
                logger.info(f"✓ All searches processed.")

        return final_results


# ============================================================================
# CREATE BOM FILE FUNCTIONALITY
# ============================================================================

async def create_bom_file(items: list, output_file: Path, use_lcsc_codes: bool = False):
    """Create LCSC BOM CSV file from MPNs or LCSC codes and quantities.

    Args:
        items: List of (part_number, quantity) tuples
        output_file: Path to output CSV file
        use_lcsc_codes: If True, treat items as LCSC codes and populate "LCSC Part Number" column
                       If False, treat items as MPNs and populate "Manufacture Part Number" column

    Returns:
        None
    """
    part_type = "LCSC code" if use_lcsc_codes else "MPN"
    logger.info(f"Processing {len(items)} parts to create BOM file (using {part_type}s)")
    logger.info("=" * 80)

    # Store BOM rows
    bom_rows = []

    # Process each item - no need for async operations
    for i, (part_number, qty) in enumerate(items, start=1):
        logger.info(f"[{i}/{len(items)}] Adding {part_type}: {part_number} (qty: {qty})")

        # Add to BOM rows - populate the appropriate column based on mode
        if use_lcsc_codes:
            bom_rows.append({
                "Quantity": qty,
                "LCSC Part Number(optional)": part_number
            })
        else:
            bom_rows.append({
                "Quantity": qty,
                "Manufacture Part Number": part_number
            })

    # Write CSV file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Header matching the template
        fieldnames = [
            "Quantity",
            "Manufacture Part Number",
            "Manufacturer(optional)",
            "Description(optional)",
            "LCSC Part Number(optional)",
            "Package(optional)",
            "Customer Part Number(optional)",
            "",
            ""
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Write each row
        for row in bom_rows:
            writer.writerow(row)

    logger.info("=" * 80)
    logger.info(f"BOM file created: {output_file}")
    logger.info(f"Total parts: {len(bom_rows)}")


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

  # Search catalog
  python lcsc_tool.py search search_input.json search_results.json
  python lcsc_tool.py search search_input.json search_results.json --limit 100
  python lcsc_tool.py search -s "1206 resistor 10k"  # Output to stdout
  python lcsc_tool.py search -s "capacitor 10uF" results.json  # Save to file

  # Create BOM file (using MPNs)
  python lcsc_tool.py create-bom-file RC1206FR-071RL:100 RC1206FR-070RL:50 -o bom.csv
  python lcsc_tool.py create-bom-file --file mpns.txt -o bom.csv

  # Create BOM file (using LCSC codes for guaranteed matching)
  python lcsc_tool.py create-bom-file --file lcsc_codes.txt -o bom.csv --lcsc-codes
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
        default=5,
        help="Maximum concurrent browser instances (default: 5)"
    )
    pricing_parser.add_argument(
        "-l", "--log",
        type=str,
        help="Log file path (optional, defaults to console only)"
    )

    # search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search LCSC catalog by keywords/specifications"
    )
    search_parser.add_argument(
        "input_file",
        type=str,
        nargs="?",
        help="Input JSON file with search specs (format: [{\"keywords\": \"1206 1%% 1Ω resistor\", \"value\": \"1Ω\"}])"
    )
    search_parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        help="Output JSON file for search results (optional, outputs to stdout if not specified)"
    )
    search_parser.add_argument(
        "-s", "--search",
        type=str,
        help="Direct keyword search string (alternative to input file)"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of results per search (default: no limit)"
    )
    search_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent browser instances (default: 5)"
    )
    search_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show progress messages and logging (default: quiet mode)"
    )
    search_parser.add_argument(
        "-l", "--log",
        type=str,
        help="Log file path (optional, defaults to console only)"
    )

    # create-bom-file command
    bom_parser = subparsers.add_parser(
        "create-bom-file",
        help="Create LCSC BOM CSV file from MPNs or LCSC codes and quantities"
    )
    bom_parser.add_argument(
        "items",
        nargs="*",
        help="Part numbers (PART or PART:QTY format, e.g., RC1206FR-071RL:100 or C107107:100)"
    )
    bom_parser.add_argument(
        "--file",
        type=str,
        help="File containing part numbers (PART or PART:QTY per line)"
    )
    bom_parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output CSV file for BOM (required)"
    )
    bom_parser.add_argument(
        "--lcsc-codes",
        action="store_true",
        help="Treat input as LCSC codes (e.g., C107107) instead of MPNs. Populates 'LCSC Part Number' column for guaranteed part matching."
    )
    bom_parser.add_argument(
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
        logger.info(f"Using {max_concurrent} concurrent browser instances")
        logger.info("")

        # Fetch pricing (writes to output_file incrementally)
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

    elif args.command == "search":
        # Determine quiet mode (opposite of verbose)
        quiet_mode = not args.verbose

        # Determine input source: direct search string or input file
        if args.search:
            # Direct keyword search
            search_specs = [{"keywords": args.search, "value": ""}]
            if not quiet_mode:
                logger.info(f"Searching for: '{args.search}'")
        elif args.input_file:
            # Load from input file
            input_file = Path(args.input_file)
            with open(input_file) as f:
                search_specs = json.load(f)
            if not quiet_mode:
                logger.info(f"Loaded {len(search_specs)} search specifications from {input_file}")
        else:
            logger.error("Error: Either provide an input file or use -s/--search for direct keyword search")
            search_parser.print_help()
            return

        # Determine output destination
        output_file = Path(args.output_file) if args.output_file else None

        limit = args.limit
        max_concurrent = args.max_concurrent
        if not quiet_mode:
            if limit:
                logger.info(f"Results limit per search: {limit}")
            logger.info(f"Using {max_concurrent} concurrent browser instances")
            logger.info("")

        # Search catalog with concurrent browser instances
        results = asyncio.run(search_lcsc_catalog(search_specs, output_file, limit, max_concurrent, quiet_mode))

        # Generate summary
        if not quiet_mode:
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"Summary:")
            logger.info(f"  Total searches: {len(results)}")
            logger.info(f"  Successful: {sum(1 for r in results if r.get('success'))}")
            logger.info(f"  Failed: {sum(1 for r in results if not r.get('success'))}")
            logger.info(f"  Total products found: {sum(r.get('total_found', 0) for r in results if r.get('success'))}")
            if output_file:
                logger.info(f"  Results file: {output_file}")
            logger.info("=" * 80)

        # Output to stdout if no output file specified
        if not output_file:
            print(json.dumps(results, indent=2))

    elif args.command == "create-bom-file":
        # Get part number specifications from arguments or file
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
            bom_parser.print_help()
            return

        if not item_specs:
            part_type = "LCSC codes" if args.lcsc_codes else "MPNs"
            logger.error(f"No {part_type} provided")
            return

        # Parse item specifications into (part_number, quantity) tuples
        items = []
        for spec in item_specs:
            try:
                part_number, qty = parse_item_spec(spec)
                items.append((part_number, qty))
            except ValueError as e:
                logger.error(f"Invalid item specification '{spec}': {e}")
                return

        # Prepare output file path
        output_file = Path(args.output)

        logger.info(f"Creating BOM file for {len(items)} parts")
        logger.info(f"Output file: {output_file}")

        # Run the async function (keeping async for consistency, even though not strictly needed)
        asyncio.run(create_bom_file(items, output_file, use_lcsc_codes=args.lcsc_codes))


if __name__ == "__main__":
    main()
