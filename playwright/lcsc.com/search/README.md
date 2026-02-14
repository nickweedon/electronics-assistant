# LCSC Catalog Search

Search the LCSC catalog by keywords with automatic pagination support.

**Action**: search
**Site**: lcsc.com
**Created**: 2026-02-14

## Description

Searches the LCSC electronics catalog for components matching keywords. Automatically handles pagination to retrieve all results up to the specified limit. Returns structured product data including LCSC codes, MPNs, manufacturers, stock levels, and pricing.

## Parameters

### Required

- `--keywords`: Search query term (e.g., "1206 resistor 10k", "capacitor 10uF")

### Optional

- `--maxResults`: Maximum number of products to return (default: 100)
- `--timeout`: Operation timeout in milliseconds (default: 10000)
- `--headless`: Run browser in headless mode (default: true, set to false for debugging)
- `--screenshot`: Take screenshot of results (default: false, set to true to capture)

## Usage

```bash
# Basic search
node script.js --keywords="1206 resistor 10k"

# Limit results
node script.js --keywords="capacitor 10uF" --maxResults=50

# Run with visible browser (for debugging)
node script.js --keywords="inductors" --headless=false

# Increase timeout for slow connections
node script.js --keywords="transistors" --timeout=20000

# Take screenshot of results
node script.js --keywords="LEDs" --screenshot=true
```

## Output Format

The script outputs JSON to stdout with the following structure:

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
    "url": "https://www.lcsc.com/search?q=...",
    "timestamp": "2026-02-14T10:30:00.000Z",
    "duration": 5678,
    "browser": "chromium"
  },
  "error": {
    "message": "Error description",
    "stack": "Stack trace...",
    "screenshot": "./screenshots/error-1234567890.png"
  }
}
```

## Features

- **Automatic Pagination**: Searches all pages until `maxResults` is reached or no more results
- **Deduplication**: Removes duplicate LCSC codes from results
- **Stealth Mode**: Uses stealth plugins to avoid bot detection
- **Error Screenshots**: Automatically captures screenshots on failure
- **Progress Logging**: Stderr output shows progress (stdout is clean JSON)

## Implementation Notes

- Navigates to `https://www.lcsc.com/search?q=<keywords>`
- Waits 5 seconds for initial page load (SPA requires time to render)
- Extracts product data from table rows containing product links
- Clicks pagination buttons to load subsequent pages
- Waits 3 seconds between page navigations
- Stops when hitting `maxResults` or page 200 (whichever comes first)

## Product Data Fields

Each product object contains:
- `mpn`: Manufacturer Part Number
- `lcscCode`: LCSC part code (e.g., "C137394")
- `manufacturer`: Manufacturer name (e.g., "YAGEO")
- `description`: Product description
- `stock`: Available stock quantity
- `price`: Unit price (first tier)
- `productUrl`: Full URL to product details page

## Error Handling

- Takes full-page screenshot on error
- Outputs structured error JSON to stdout
- Returns exit code 1 on failure
- Logs progress/errors to stderr (doesn't pollute JSON output)

## Related Actions

- `check-pricing`: Get detailed pricing tiers for specific LCSC codes
- `add-to-cart`: Add products to shopping cart
- `list-cart`: View cart contents

## Migration

To migrate to skill templates:

```bash
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  scripts-temp/playwright/lcsc.com
```
