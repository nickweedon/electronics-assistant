# LCSC Check Pricing

Get detailed pricing, stock levels, and product specifications for an LCSC part.

**Action**: check-pricing
**Site**: lcsc.com
**Created**: 2026-02-14

## Description

Fetches complete product information for a specific LCSC part code including manufacturer, MPN, description, stock levels, and all pricing tiers. Returns structured data suitable for automated price checking and inventory management.

## Parameters

### Required

- `--lcscCode`: LCSC part code (e.g., "C137394")
  *Alternative:* `--code` (shorter alias)

### Optional

- `--timeout`: Operation timeout in milliseconds (default: 10000)
- `--headless`: Run browser in headless mode (default: true, set to false for debugging)
- `--screenshot`: Take screenshot of product page (default: false, set to true to capture)

## Usage

```bash
# Basic usage
./run.sh --lcscCode="C137394"

# Using shorter alias
./run.sh --code="C137394"

# Run with visible browser (for debugging)
./run.sh --lcscCode="C137394" --headless=false

# Increase timeout for slow connections
./run.sh --lcscCode="C137394" --timeout=20000

# Take screenshot
./run.sh --lcscCode="C137394" --screenshot=true

# Direct invocation (without wrapper)
NODE_PATH=$(npm root -g) node script.js --lcscCode="C137394"
```

## Output Format

The script outputs JSON to stdout:

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
    "browser": "chromium",
    "screenshots": []
  }
}
```

On error:

```json
{
  "success": false,
  "data": null,
  "metadata": {
    "url": "https://www.lcsc.com/product-detail/C137394.html",
    "timestamp": "2026-02-14T18:30:00.000Z",
    "duration": 5678,
    "browser": "chromium"
  },
  "error": {
    "message": "Error description",
    "stack": "Stack trace...",
    "screenshot": "./screenshots/error-C137394-1234567890.png"
  }
}
```

## Data Fields

### Product Information
- `lcscCode`: LCSC part number (e.g., "C137394")
- `mpn`: Manufacturer Part Number (e.g., "RC1206FR-070RL")
- `manufacturer`: Manufacturer name (e.g., "YAGEO")
- `description`: Product description
- `stock`: Available stock quantity (numeric string)

### Pricing Array
Each pricing tier contains:
- `qty`: Quantity break (e.g., "100+", "500+")
- `unit_price`: Price per unit (e.g., "$ 0.0043")
- `ext_price`: Extended price for quantity (e.g., "$ 0.43")

## Features

- **Complete Product Data**: Extracts manufacturer, MPN, description, stock
- **All Pricing Tiers**: Captures complete MOQ price breaks
- **Robust Extraction**: Multiple regex patterns for reliable data extraction
- **Error Screenshots**: Automatically captures screenshots on failure
- **Flexible Input**: Accepts `--lcscCode` or `--code` parameter
- **Clean Output**: JSON to stdout, logs to stderr

## Implementation Notes

- Navigates to `https://www.lcsc.com/product-detail/{lcscCode}.html`
- Waits 6 seconds for SPA to fully load and render pricing table
- Uses regex patterns to extract data from page text
- Finds pricing table by looking for "Unit Price" or "Qty" + "$" indicators
- Converts stock "N/A" to "0" for consistency

## Error Handling

- Takes full-page screenshot on error with filename: `error-{lcscCode}-{timestamp}.png`
- Outputs structured error JSON to stdout
- Returns exit code 1 on failure
- Logs progress/errors to stderr (doesn't pollute JSON output)

## Related Actions

- `search`: Find parts by keyword search
- `add-to-cart`: Add parts to shopping cart (TODO)
- `list-cart`: View cart contents (TODO)

## Examples

```bash
# Check pricing for 0Ω resistor
./run.sh --lcscCode="C137394"

# Check pricing for capacitor
./run.sh --code="C1525"

# Check multiple parts (using loop)
for code in C137394 C1525 C106886; do
  echo "Checking $code..."
  ./run.sh --lcscCode="$code" 2>/dev/null | jq '.data | {lcscCode, mpn, stock}'
done
```

## Migration

To migrate to skill templates:

```bash
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  scripts-temp/playwright/lcsc.com
```
