# LCSC Guidelines

## Overview

LCSC has no API, so all operations use the Playwright MCP server. For most tasks, use the **lcsc_tool.py script** which provides automated workflows for common LCSC operations.

## Using lcsc_tool.py (Recommended)

The `scripts/lcsc_tool.py` tool provides automated commands for LCSC operations. **Always use this tool instead of manual MCP calls** for the following tasks:

### Available Commands

#### 1. Search Catalog

Search for products by keyword or specifications:

```bash
# Single search (output to stdout)
uv run python scripts/lcsc_tool.py search -s "1206 resistor 10k"

# Single search (save to file)
uv run python scripts/lcsc_tool.py search -s "capacitor 10uF" results.json

# Batch search from input file
uv run python scripts/lcsc_tool.py search input.json output.json

# With result limit
uv run python scripts/lcsc_tool.py search input.json output.json --limit 100
```

**Note:** Searches run sequentially (not in parallel) because playwright-mcp-server uses a single shared browser page. Concurrent searches would interfere with each other.

**Input format** (for batch searches):
```json
[
  {"keywords": "1206 1% 1Ω resistor", "value": "1Ω"},
  {"keywords": "capacitor 10uF 50V", "value": "10uF"}
]
```

**Output format**:
```json
[
  {
    "keywords": "1206 1% 1Ω resistor",
    "value": "1Ω",
    "total_found": 150,
    "success": true,
    "products": [
      {
        "mpn": "RC1206FR-071RL",
        "lcscCode": "C137394",
        "manufacturer": "YAGEO",
        "description": "1Ω ±1% 1/4W 1206 Chip Resistor",
        "stock": "45000",
        "price": "$0.0019",
        "productUrl": "https://www.lcsc.com/product-detail/C137394.html"
      }
    ]
  }
]
```

**Parameters**:
- `--limit`: Maximum results per search (default: unlimited, fetches all pages)

**Performance**: Searches execute sequentially due to playwright-mcp-server's single shared browser page.

#### 2. Check Pricing

Fetch detailed pricing and stock information:

```bash
# Check pricing by LCSC codes or MPNs
uv run python scripts/lcsc_tool.py check-pricing input.json output.json
```

**Input format**:
```json
[
  {"lcsc_code": "C137394", "value": "1Ω"},
  {"mpn": "RC1206FR-070RL", "value": "0Ω"}
]
```

**Output format**:
```json
[
  {
    "lcsc_code": "C137394",
    "value": "1Ω",
    "mpn": "RC1206FR-071RL",
    "manufacturer": "YAGEO",
    "description": "1Ω ±1% 1/4W 1206 Chip Resistor",
    "stock": "45000",
    "pricing": [
      {"qty": "1+", "unit_price": "$0.0019", "ext_price": "$0.0019"},
      {"qty": "10+", "unit_price": "$0.0017", "ext_price": "$0.017"},
      {"qty": "100+", "unit_price": "$0.0015", "ext_price": "$0.15"}
    ],
    "success": true
  }
]
```

**Note**: Processing runs sequentially (not in parallel) because playwright-mcp-server uses a single shared browser page. Concurrent requests would cause race conditions where navigations overwrite each other.

#### 3. Add to Cart

Add parts to LCSC shopping cart:

```bash
# Add individual parts (CODE:QUANTITY format)
uv run python scripts/lcsc_tool.py add-to-cart C137394:100 C137181:50

# Add from file
uv run python scripts/lcsc_tool.py add-to-cart --file codes.txt -o results.json

# With logging
uv run python scripts/lcsc_tool.py add-to-cart --file codes.txt -o results.json -l cart.log
```

**File format** (one item per line):
```
C137394:100
C137181:50
C123456
```

**Output format**:
```json
[
  {"code": "C137394", "status": "success"},
  {"code": "C137181", "status": "success"}
]
```

**Parameters**:
- `--file`: Input file with LCSC codes
- `-o, --output`: Output JSON file (default: lcsc_cart_results.json)
- `-l, --log`: Log file path

#### 4. List Cart Contents

Display or export current cart contents:

```bash
# Display as table
uv run python scripts/lcsc_tool.py list-cart

# Export to JSON
uv run python scripts/lcsc_tool.py list-cart -o cart.json --format json

# Both display and save
uv run python scripts/lcsc_tool.py list-cart -o cart.json
```

**Table output**:
```
========================================================================================================================
LCSC Cart Summary - 3 items
========================================================================================================================
LCSC Code    MPN                  Manufacturer    Qty      Unit Price   Ext Price    Description
------------------------------------------------------------------------------------------------------------------------
C137394      RC1206FR-071RL       YAGEO           100      $0.0019      $0.19        1Ω ±1% 1/4W 1206 Chip Res...
C137181      RC1206FR-070RL       YAGEO           50       $0.0019      $0.095       0Ω ±1% 1/4W 1206 Chip Res...
------------------------------------------------------------------------------------------------------------------------
                                                                                 Cart Total: $0.29
========================================================================================================================
```

**Parameters**:
- `--format`: Output format - `table` (default) or `json`
- `-o, --output`: Save cart data to JSON file

#### 5. Open Cart in Browser

Open cart in browser for manual review:

```bash
# Opens browser and keeps it open for manual interaction
uv run python scripts/lcsc_tool.py open-cart
```

This opens the cart page and keeps the browser session active. Press Ctrl+C when done to close.

#### 6. Create BOM File

Create LCSC BOM CSV file from Manufacturer Part Numbers (MPNs) or LCSC codes and quantities:

```bash
# Create BOM from command line using MPNs
uv run python scripts/lcsc_tool.py create-bom-file RC1206FR-071RL:100 RC1206FR-070RL:50 -o bom.csv

# Create BOM from file
uv run python scripts/lcsc_tool.py create-bom-file --file mpns.txt -o bom.csv

# Create BOM using LCSC codes (use --lcsc-codes flag)
uv run python scripts/lcsc_tool.py create-bom-file --file lcsc_codes.txt -o bom.csv --lcsc-codes

# With logging
uv run python scripts/lcsc_tool.py create-bom-file --file mpns.txt -o bom.csv -l bom.log
```

**File format** (one item per line):

*Using MPNs:*
```
RC1206FR-071RL:100
RC1206FR-070RL:50
0805W8F1002T5E:100
```

*Using LCSC codes (with --lcsc-codes flag):*
```
C107107:100
C137394:50
C1790:25
```

**Output format**: CSV file matching LCSC BOM template with headers:

*When using MPNs (default):*
```csv
Quantity,Manufacture Part Number,Manufacturer(optional),Description(optional),LCSC Part Number(optional),Package(optional),Customer Part Number(optional),,
100,RC1206FR-071RL,,,,,,,
50,RC1206FR-070RL,,,,,,,
100,0805W8F1002T5E,,,,,,,
```

*When using LCSC codes (--lcsc-codes):*
```csv
Quantity,Manufacture Part Number,Manufacturer(optional),Description(optional),LCSC Part Number(optional),Package(optional),Customer Part Number(optional),,
100,,,,C107107,,,,
50,,,,C137394,,,,
25,,,,C1790,,,,
```

**Features**:
- Simple and fast - no web scraping required
- Supports both MPNs and LCSC codes
- **LCSC codes are more reliable** - they guarantee exact part matches
- Only populates required columns (Quantity and either MPN or LCSC Part Number)
- Leaves optional columns empty
- CSV format ready for direct upload to LCSC BOM tool
- Accepts part numbers directly from your source data

**Parameters**:
- `--file`: Input file with part numbers (PART:QTY format)
- `-o, --output`: Output CSV file (required)
- `--lcsc-codes`: Treat input as LCSC codes instead of MPNs (populates "LCSC Part Number" column)
- `-l, --log`: Log file path

**When to use LCSC codes vs MPNs**:

✅ **Use LCSC codes (`--lcsc-codes`)** when:
- You have LCSC part codes from price comparison or search results
- You want guaranteed exact part matching (no ambiguity)
- The check-pricing tool returned unreliable MPN data
- You're ordering from a pre-researched parts list with LCSC codes

✅ **Use MPNs (default)** when:
- Your source data only has manufacturer part numbers
- You're working from a schematic or design with standard MPNs
- You don't have LCSC codes yet

**Why LCSC codes are better**: LCSC codes (like C107107) uniquely identify a specific product in LCSC's catalog. MPNs can sometimes match multiple similar parts or fail to match due to variations in formatting. Using LCSC codes eliminates this ambiguity.

## When to Use Manual MCP Calls vs lcsc_tool.py

### Use lcsc_tool.py for:
- ✅ Searching for products (single or batch)
- ✅ Checking pricing and stock (including MPN lookups)
- ✅ Adding items to cart (single or batch)
- ✅ Listing cart contents
- ✅ Creating BOM CSV files
- ✅ Any repetitive LCSC operations

### Use manual MCP calls only for:
- ⚠️ One-off custom workflows not covered by lcsc_tool.py
- ⚠️ Debugging or testing new automation patterns
- ⚠️ Extracting custom data not provided by the tool

## Manual MCP Call Patterns (Advanced)

If you need to create custom workflows not covered by lcsc_tool.py:

### General Best Practices
- Use `browser_execute_bulk` to combine steps into single calls for 5-10x better performance
- Process one product per bulk call (don't combine multiple products)
- Use appropriate wait times after navigation (3-5 seconds)
- Extract data using JavaScript evaluation for complex DOM structures

### Example: Custom Product Data Extraction

```python
# Single product lookup using browser_execute_bulk
commands = [
    {
        "tool": "browser_navigate",
        "args": {"url": f"https://www.lcsc.com/product-detail/{lcsc_code}.html", "silent_mode": True}
    },
    {
        "tool": "browser_wait_for",
        "args": {"time": 3}
    },
    {
        "tool": "browser_evaluate",
        "args": {
            "function": "() => { /* extract custom product data */ }"
        },
        "return_result": True
    }
]

# For multiple products, run separate bulk calls in parallel
```

### Reference Implementation

See [scripts/lcsc_tool.py](../scripts/lcsc_tool.py) for complete implementation examples:
- Product search by MPN or keyword (lines 951-1200)
- Detailed pricing extraction with JMESPath (lines 704-876)
- Cart operations (add, list, open)
- Complete DOM extraction patterns using `browser_evaluate`

## Performance Guidelines

### Concurrency Settings

| Operation | Concurrency | Notes |
|-----------|-------------|-------|
| Search by keyword | Sequential only | playwright-mcp-server uses single shared page |
| Check pricing | Sequential (hardcoded) | Automatically runs sequentially - no configuration needed |
| Add to cart | Sequential | Tool handles this automatically |

**Note**: All LCSC operations run sequentially due to playwright-mcp-server's single shared browser page. Concurrent requests would cause race conditions.

### Result Limits

- Search results are **paginated automatically** by lcsc_tool.py
- Use `--limit` parameter to cap results per search
- Without limit, tool fetches all pages (up to 5000 products per search)

## Related Guidelines

- [Playwright MCP Server Guidelines](Playwright-MCP-Server-Guidelines.md) - General browser automation best practices
- [Pricing Guidelines](Pricing-Guidelines.md) - Price comparison and MOQ rules
- [MCP Scripting Guidelines](MCP-Scripting-Guidelines.md) - Creating custom automation scripts
