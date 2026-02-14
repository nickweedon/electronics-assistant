---
name: lcsc-supplier
description: Automate LCSC electronics supplier interactions using Playwright scripts for search, pricing, BOM creation, and cart operations.
user-invokable: true
---
# LCSC Supplier

Automate LCSC electronics supplier interactions using Playwright scripts for search, pricing, BOM creation, and cart operations.

## Overview

This skill provides a streamlined interface for interacting with LCSC (Shenzhen Lichuang E-Commerce Co., Ltd.), a major electronics component supplier. Since LCSC has no public API, all operations use automated Playwright scripts that navigate the LCSC website to perform searches, retrieve pricing, create BOMs, and manage cart operations.

**Key capabilities:**

- Search LCSC catalog by keywords with automatic pagination
- Retrieve detailed pricing tiers and product specifications
- Generate LCSC-compatible BOM CSV files for batch ordering
- Add items to cart and manage orders
- Enforce pricing rules (MOQ, stock availability, quantity matching)

**Architecture:**

- All operations use Playwright scripts in `playwright/lcsc.com/`
- Scripts output structured JSON for easy parsing and automation
- Replaces deprecated `scripts/lcsc_tool.py` with modular Node.js approach

## When to Use This Skill

Auto-invoke this skill when the user needs to:

- **Search for components** on LCSC (e.g., "search LCSC for 1206 resistors")
- **Check pricing** for LCSC part codes or MPNs
- **Create BOM files** for LCSC bulk ordering
- **Add items to cart** on LCSC
- **Compare prices** from LCSC (vs Digikey, Mouser, Farnell)
- **Verify stock availability** for LCSC parts
- **Generate order lists** from LCSC catalog

## Prerequisites

This skill **ALWAYS invokes the `/playwright` skill first** to ensure Playwright and dependencies are properly installed.

If Playwright is not installed, the playwright skill will handle installation:

```bash
bash ~/.claude/skills/playwright/scripts/install-playwright.sh
```

This installs globally:

- `playwright` - Core library
- `playwright-extra` - Plugin framework
- `puppeteer-extra-plugin-stealth` - Stealth features
- Browser binaries (Chromium by default)

## Available LCSC Actions

All scripts are located in `playwright/lcsc.com/<action>/` and use the Playwright skill framework.

### ✅ search - Search LCSC Catalog

**Status**: Working
**Purpose**: Search for components by keywords with automatic pagination

**Location**: `playwright/lcsc.com/search/`

**Parameters:**

- `--keywords` (required): Search query (e.g., "1206 resistor 10k", "capacitor 10uF")
- `--maxResults` (optional): Maximum number of products to return (default: 100)
- `--timeout` (optional): Timeout in milliseconds (default: 10000)
- `--headless` (optional): Run headless (default: true)
- `--screenshot` (optional): Take screenshot (default: false)

**Usage:**

```bash
cd playwright/lcsc.com/search
./run.sh --keywords="1206 resistor 10k" --maxResults=50
```

**Output:**

```json
{
  "success": true,
  "data": {
    "keywords": "1206 resistor 10k",
    "total_found": 42,
    "products": [
      {
        "mpn": "RC1206FR-0710KL",
        "lcscCode": "C137394",
        "manufacturer": "YAGEO",
        "description": "±1% 10kΩ 1206 Chip Resistor",
        "stock": "15000",
        "price": "$0.0028",
        "productUrl": "https://www.lcsc.com/product-detail/C137394.html"
      }
    ]
  },
  "metadata": {
    "url": "https://www.lcsc.com/search?q=1206+resistor+10k",
    "timestamp": "2026-02-14T10:30:00.000Z",
    "duration": 12345,
    "browser": "chromium"
  }
}
```

**Features:**

- Automatic pagination through all result pages
- Deduplication of LCSC codes
- Stealth mode to avoid bot detection
- Progress logging to stderr (clean JSON to stdout)
- Error screenshots on failure

**Use cases:**

- Find available components matching specifications
- Compare multiple manufacturers for the same component
- Build a list of candidates before checking detailed pricing

### ✅ check-pricing - Get Detailed Pricing

**Status**: Working
**Purpose**: Retrieve complete product specifications and all pricing tiers

**Location**: `playwright/lcsc.com/check-pricing/`

**Parameters:**

- `--lcscCode` or `--code` (required): LCSC part code (e.g., "C137394")
- `--timeout` (optional): Timeout in milliseconds (default: 10000)
- `--headless` (optional): Run headless (default: true)
- `--screenshot` (optional): Take screenshot (default: false)

**Usage:**

```bash
cd playwright/lcsc.com/check-pricing
./run.sh --lcscCode="C137394"
```

**Output:**

```json
{
  "success": true,
  "data": {
    "lcscCode": "C137394",
    "mpn": "RC1206FR-070RL",
    "manufacturer": "YAGEO",
    "description": "0Ω 1206 Chip Resistor - Surface Mount",
    "stock": "198300",
    "pricing": [
      {
        "qty": "100+",
        "unit_price": "$ 0.0043",
        "ext_price": "$ 0.43"
      },
      {
        "qty": "500+",
        "unit_price": "$ 0.0029",
        "ext_price": "$ 1.45"
      }
    ]
  },
  "metadata": {
    "url": "https://www.lcsc.com/product-detail/C137394.html",
    "timestamp": "2026-02-14T18:30:00.000Z",
    "duration": 8234,
    "browser": "chromium"
  }
}
```

**Features:**

- Complete product information extraction
- All pricing tiers with quantity breaks
- Stock availability checking
- Robust regex-based extraction
- Error screenshots with part code in filename

**Use cases:**

- Price comparison against Digikey/Mouser
- Verify MOQ (Minimum Order Quantity) requirements
- Check stock before adding to cart
- Determine best quantity for price breaks

### ✅ create-bom-file - Generate BOM CSV

**Status**: Working
**Purpose**: Create LCSC-compatible BOM CSV files for batch ordering

**Location**: `playwright/lcsc.com/create-bom-file/`

**Note**: This script does NOT use browser automation - it's a pure CSV generator.

**Parameters:**

- `--output` (required): Output CSV file path
- `--input` or `--parts` (required): Parts to include (see formats below)
- `--useLcscCodes` or `--lcscCodes` (optional): Treat input as LCSC codes vs MPNs (default: false)

**Usage:**

```bash
cd playwright/lcsc.com/create-bom-file

# Using LCSC codes (recommended for accuracy)
./run.sh --parts="C137394:100,C1525:50,C106886:25" --output=bom.csv --useLcscCodes=true

# Using MPNs
./run.sh --parts="RC1206FR-070RL:100,RC1206FR-0710KL:50" --output=bom.csv

# From JSON file
./run.sh --input=parts.json --output=bom.csv --useLcscCodes=true
```

**JSON Input Format:**

```json
[
  {
    "lcscCode": "C137394",
    "quantity": 100
  },
  {
    "lcscCode": "C1525",
    "quantity": 50
  }
]
```

**Output CSV:**

```csv
Quantity,Manufacture Part Number,Manufacturer(optional),Description(optional),LCSC Part Number(optional),Package(optional),Customer Part Number(optional),,
100,,,,C137394,,,,
50,,,,C1525,,,,
```

**Features:**

- No browser required (fast generation)
- Supports both LCSC codes and MPNs
- Flexible input (JSON file or command-line)
- LCSC template-compliant format
- Auto-creates output directory

**Use cases:**

- Create order files from search results
- Convert Digikey lists to LCSC format
- Prepare bulk orders for upload to LCSC
- Generate BOMs from project parts lists

**Important**: LCSC codes are more reliable than MPNs because they guarantee exact part matches. Use `--useLcscCodes=true` when possible.

### 🚧 add-to-cart - Add Parts to Cart

**Status**: Not yet implemented
**Purpose**: Add parts to LCSC shopping cart with quantities
**Requirements**: Persistent browser session, authentication

**Planned usage:**

```bash
cd playwright/lcsc.com/add-to-cart
./run.sh --parts="C137394:100,C1525:50"
```

**Implementation notes:**

- Requires browser session persistence
- Must handle LCSC login flow
- Need to maintain cookies across requests
- Should verify items added successfully

### 🚧 list-cart - List Cart Contents

**Status**: Not yet implemented
**Purpose**: Display all items in shopping cart with quantities and pricing
**Requirements**: Persistent browser session, authentication

**Planned usage:**

```bash
cd playwright/lcsc.com/list-cart
./run.sh --format=json
```

**Implementation notes:**

- Requires authenticated session
- Extract cart items, quantities, unit prices, totals
- Support both table and JSON output

## Detailed Action Documentation

Each LCSC Playwright action has comprehensive documentation in its README.md file:

### 📖 Search Action

**File**: [playwright/lcsc.com/search/README.md](../../../playwright/lcsc.com/search/README.md)

Includes:

- Complete parameter reference
- Output format specification
- Usage examples (basic search, limiting results, debugging)
- Implementation details (pagination, deduplication)
- Feature descriptions and error handling

### 📖 Check Pricing Action

**File**: [playwright/lcsc.com/check-pricing/README.md](../../../playwright/lcsc.com/check-pricing/README.md)

Includes:

- Parameter reference with aliases
- Complete data field documentation
- Pricing tier extraction examples
- Batch checking workflows
- Error handling and screenshots

### 📖 Create BOM File Action

**File**: [playwright/lcsc.com/create-bom-file/README.md](../../../playwright/lcsc.com/create-bom-file/README.md)

Includes:

- Input format specifications (JSON and command-line)
- CSV output format (LCSC template-compliant)
- LCSC codes vs MPNs guidance
- Pipeline examples (search → BOM)
- Use cases and best practices

### 📖 LCSC Actions Overview

**File**: [playwright/lcsc.com/README.md](../../../playwright/lcsc.com/README.md)

Includes:

- Complete action status table
- Output format standards
- Quick start guide
- Comparison with deprecated lcsc_tool.py
- Migration path and future enhancements

**IMPORTANT**: Always refer to these README.md files for the most up-to-date and detailed documentation on each action.

## Pricing Rules (CRITICAL)

**ALWAYS** follow these rules when using pricing data from LCSC:

### 1. Match Order Quantity

**ALWAYS** ensure the correct price tier is selected based on the order quantity.

**DO NOT LIST** prices that don't match the quantity being ordered.

Example:

```bash
# For quantity 100, use the correct tier:
# Pricing: 1+ = $0.01, 100+ = $0.005, 500+ = $0.003
# For qty=100, use $0.005 (NOT $0.01 or $0.003)
```

### 2. Check Minimum Order Quantity (MOQ)

**ALWAYS** verify that the MOQ is less than or equal to the requested quantity.

If all quantity levels are greater than the amount being ordered, the item **CANNOT** be ordered.

Example:

```bash
# Pricing: 500+ = $0.003, 1000+ = $0.002
# For qty=100, this item CANNOT be ordered (MOQ=500)
```

### 3. Verify Stock Availability

**ALWAYS** check that the item is actually in stock.

Back-ordered items should be treated as **NOT IN STOCK**.

Example:

```bash
# Stock: "198300" = OK to order
# Stock: "0" or "N/A" = CANNOT order
```

### Summary Checklist

Before recommending an LCSC part:

- ✅ Price tier matches order quantity
- ✅ MOQ ≤ requested quantity
- ✅ Item is in stock (not backordered)
- ✅ All conditions met

## Deprecated: scripts/lcsc_tool.py

**IMPORTANT**: The file `scripts/lcsc_tool.py` is now **DEPRECATED** and should NOT be used.

**Why deprecated:**

- Monolithic 2000+ line script (hard to maintain)
- Required Docker container for MCP server
- Slower startup (~10-15s vs ~2-3s)
- Custom output formats per operation
- Harder to debug (Docker layer indirection)

**Migration path:**

- Use `playwright/lcsc.com/<action>/` scripts instead
- All functionality has been migrated to modular Playwright scripts
- Better performance, easier debugging, standard output format

**Old command → New equivalent:**

```bash
# OLD (deprecated)
uv run python scripts/lcsc_tool.py search -s "1206 resistor 10k"

# NEW (use this)
cd playwright/lcsc.com/search && ./run.sh --keywords="1206 resistor 10k"
```

```bash
# OLD (deprecated)
uv run python scripts/lcsc_tool.py check-pricing input.json output.json

# NEW (use this)
cd playwright/lcsc.com/check-pricing
for code in $(jq -r '.[].lcsc_code' input.json); do
  ./run.sh --lcscCode="$code" 2>/dev/null
done > output.json
```

```bash
# OLD (deprecated)
uv run python scripts/lcsc_tool.py create-bom-file --file codes.txt -o bom.csv

# NEW (use this)
cd playwright/lcsc.com/create-bom-file
./run.sh --input=codes.json --output=bom.csv --useLcscCodes=true
```

## Output Format Standards

All LCSC Playwright scripts follow the Playwright skill output convention:

```json
{
  "success": true|false,
  "data": { /* action-specific data */ },
  "metadata": {
    "url": "https://...",
    "timestamp": "2026-02-14T...",
    "duration": 1234,
    "browser": "chromium",
    "screenshots": []
  },
  "error": { /* only on failure */
    "message": "...",
    "stack": "...",
    "screenshot": "path/to/error-screenshot.png"
  }
}
```

**Key features:**

- JSON to stdout (clean, parseable)
- Progress logs to stderr (human-readable, doesn't pollute JSON)
- Exit code 0 on success, 1 on failure
- Error screenshots automatically saved to `screenshots/`

## Related Documentation

- [LCSC Actions Overview](../../../playwright/lcsc.com/README.md) - Complete status and comparison table
- [Pricing Guidelines](../../../docs/Pricing-Guidelines.md) - MOQ, stock, quantity rules
- [Playwright MCP Server Guidelines](../../../docs/Playwright-MCP-Server-Guidelines.md) - Browser automation best practices
- [Using JMESPath](../../../docs/Using-JMESPath.md) - Filtering JSON output

## Related Skills

- `/playwright` - **ALWAYS invoked first** by this skill for browser automation
- `/digikey` - Primary electronics supplier (Digikey MCP server)
- `/mouser` - Secondary supplier for price comparison
- `/partsbox` - Inventory management integration

## Important Guidelines

- **Always invoke `/playwright` first** - All LCSC operations require Playwright
- **Use LCSC codes over MPNs** - More reliable for exact part matching
- **Follow pricing rules** - MOQ, stock, and quantity tier matching are critical
- **Check existing scripts** - Use `playwright/lcsc.com/<action>/` instead of creating new ones
- **Parse JSON output** - All scripts output clean JSON to stdout
- **Read stderr for progress** - Logs go to stderr, data goes to stdout
- **Handle errors gracefully** - Check `success` field, inspect `error.screenshot` on failure
- **Don't use lcsc_tool.py** - Deprecated in favor of modular Playwright scripts
- **Store BOMs in data/boms/** - Keep BOM files in the gitignored directory
