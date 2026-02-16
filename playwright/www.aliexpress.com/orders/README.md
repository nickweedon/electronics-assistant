# AliExpress Orders - www.aliexpress.com

**Action**: orders
**Site**: www.aliexpress.com
**Template**: navigate-screenshot (customized)
**Created**: 2026-02-15T20:30:49Z
**Updated**: 2026-02-15

## Description

Extract order information from AliExpress orders page. This script navigates to your AliExpress order history and attempts to extract order details including order numbers, dates, status, and prices.

**Note**: This script requires you to be logged in to AliExpress. The browser will open in visible mode by default to allow you to log in if needed.

## Parameters

### Required
- None (uses default URL)

### Optional
- `--url=<url>` - Custom orders page URL (default: https://www.aliexpress.com/p/order/index.html)
- `--headless=true` - Run browser in headless mode (default: false for easier login)
- `--manual=true` - Enable manual login mode - keeps browser open and waits for you to complete login (recommended)
- `--timeout=<ms>` - Set timeout in milliseconds (default: 15000)
- `--screenshot=true` - Take screenshots (always enabled)
- `--output=<path>` - Custom screenshot path

## Usage

### Manual login mode (RECOMMENDED - for first time or when session expired)
```bash
cd /workspace/playwright/www.aliexpress.com/orders
node script.js --manual=true
```
This will:
1. Open a visible browser window
2. Navigate to the orders page (will redirect to login if needed)
3. Wait for you to complete login (up to 5 minutes)
4. Automatically proceed to extract orders after login is detected
5. Close the browser and output results

### Basic usage (visible browser, but won't wait for login)
```bash
cd /workspace/playwright/www.aliexpress.com/orders
node script.js
```

### With custom URL
```bash
node script.js --manual=true --url="https://www.aliexpress.com/p/order/index.html?..."
```

### Headless mode (only if already logged in via cookies)
```bash
node script.js --headless=true
```

## Output Format

Scripts output JSON to stdout:

```json
{
  "success": true,
  "data": {
    "title": "My Orders - AliExpress",
    "url": "https://www.aliexpress.com/p/order/index.html",
    "orderCount": 5,
    "orders": [
      {
        "index": 1,
        "orderNumber": "123456789",
        "date": "2026-02-10",
        "status": "Delivered",
        "price": "$25.99",
        "text": "Order summary text...",
        "html": "<div>Order HTML...</div>"
      }
    ],
    "bodyText": "Full page text for debugging...",
    "headings": [...],
    "screenshotPath": "./screenshots/aliexpress-orders-1234567890.png"
  },
  "metadata": {
    "url": "https://www.aliexpress.com/p/order/index.html",
    "timestamp": "2026-02-15T...",
    "duration": 5432,
    "browser": "chromium",
    "screenshots": ["./screenshots/aliexpress-orders-1234567890.png"]
  }
}
```

## Login Requirements

**Important**: AliExpress requires authentication to view orders. When you run this script:

1. The browser will open in **visible mode** by default
2. If not logged in, you'll see the login page - log in manually
3. The script will wait while the page loads
4. After login, the orders should load automatically

Once you're logged in, browser cookies and sessions are preserved in the Docker volume `playwright-profiles` at `/home/vscode/.cache/playwright-profiles/aliexpress`. This means your login persists across container restarts and you won't need to log in again (unless the session expires on AliExpress's side).

## Troubleshooting

### No orders found
- Check if you need to log in (browser will show login page)
- AliExpress may use different HTML structure - check the screenshot
- Look at the `bodyText` field in output to see what's on the page

### Timeout errors
- Increase timeout: `--timeout=30000` (30 seconds)
- Check your internet connection
- AliExpress might be slow to load

### Can't see the browser
- Make sure you're NOT using `--headless=true`
- Default is visible mode for easier debugging

## Notes

- Screenshots are saved to `./screenshots/` directory
- Error screenshots are saved automatically on failure
- The script tries multiple CSS selectors to find orders
- First run may be slow due to AliExpress SPA loading

## Migration

To migrate to skill templates for reuse:

```bash
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  playwright/www.aliexpress.com
```
