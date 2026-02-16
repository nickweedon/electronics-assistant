# orders - amazon.com

**Action**: orders
**Site**: amazon.com (<www.amazon.com>)
**Template**: base-script
**Created**: 2026-02-16

## Description

Retrieves your Amazon order history with automatic login session persistence. On first run, you'll need to log in manually in the browser window. The session is saved and reused for future runs, so you only need to log in once.

## Parameters

### Required Parameters

None - the script works without parameters using defaults.

### Optional Parameters

- `--maxOrders=N` - Maximum number of orders to retrieve (default: 10)
- `--year=YYYY` - Filter by year (default: current year 2026)
- `--manualLogin` - Force manual login even if a saved session exists
- `--headless=false` - Run with visible browser window (REQUIRED for first-time login)
- `--timeout=N` - Custom timeout in milliseconds (default: 15000)
- `--debug=true` - Save screenshots and HTML for debugging

## Usage

### First-Time Setup (Manual Login)

**IMPORTANT**: On first run, you MUST use `--headless=false` to log in manually:

```bash
cd /workspace/playwright/www.amazon.com/orders
node script.js --headless=false
```

The browser window will open. You'll see a message in the terminal:

```text
[INFO] ⚠️  NOT LOGGED IN - Manual login required
[INFO] 👉 Please log in to Amazon in the browser window
[INFO] 🕐 Waiting 2 minutes for manual login...
```

**Steps:**

1. Log in to your Amazon account in the browser window
2. Complete any 2FA/verification if prompted
3. Wait for the orders page to load
4. The script will automatically continue after detecting your login
5. Your session is saved in `~/.cache/playwright-profiles/amazon/`

### Subsequent Runs (Automatic)

After the first login, you can run headlessly:

```bash
node script.js
```

The script will reuse your saved session automatically.

### Retrieve Specific Number of Orders

```bash
# Get latest 5 orders
node script.js --maxOrders=5

# Get latest 20 orders
node script.js --maxOrders=20
```

### Filter by Year

```bash
# Get 2025 orders
node script.js --year=2025

# Get 2024 orders with max 15 results
node script.js --year=2024 --maxOrders=15
```

### Force Re-login

If your session expires or you need to switch accounts:

```bash
node script.js --headless=false --manualLogin
```

### Debug Mode

If you need to troubleshoot selector issues:

```bash
node script.js --headless=false --debug=true
```

This will save screenshots and HTML to `./screenshots/` for inspection.

## Output Format

The script outputs JSON to stdout with the following structure:

```json
{
  "success": true,
  "data": {
    "orders": [...],
    "count": 10,
    "filters": {
      "maxOrders": 10,
      "year": "2026"
    }
  },
  "metadata": {
    "url": "final-url-after-execution",
    "timestamp": "ISO-8601-timestamp",
    "duration": 1234,
    "browser": "chromium",
    "screenshots": [],
    "sessionPersisted": true
  }
}
```

On error:

```json
{
  "success": false,
  "data": null,
  "metadata": {
    "url": "url-where-error-occurred",
    "timestamp": "ISO-8601-timestamp",
    "duration": 1234,
    "browser": "chromium"
  },
  "error": {
    "message": "error-message",
    "stack": "full-stack-trace",
    "screenshot": "path/to/error-screenshot.png"
  }
}
```

## Output Example

### Raw JSON Output

The script outputs structured JSON to stdout:

```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "orderNumber": "123-4567890-1234567",
        "orderDate": "February 10, 2026",
        "orderStatus": "Delivered Feb 12",
        "orderTotal": "$45.99",
        "products": [
          {
            "title": "USB-C Cable 3-Pack, 6ft Fast Charging",
            "price": "N/A",
            "imageUrl": "https://m.media-amazon.com/images/I/61ABC123._SS142_.jpg",
            "productUrl": "https://www.amazon.com/dp/B08XYZ123"
          }
        ]
      }
    ],
    "count": 1,
    "filters": {
      "maxOrders": 10,
      "year": "2026"
    }
  },
  "metadata": {
    "url": "https://www.amazon.com/gp/your-account/order-history?orderFilter=year-2026",
    "timestamp": "2026-02-16T18:45:30.123Z",
    "duration": 8234,
    "browser": "chromium",
    "screenshots": [],
    "sessionPersisted": true
  }
}
```

### Recommended Presentation Format

When presenting orders to users, format them as follows:

---

**Order #123-4567890-1234567** • Feb 10, 2026 • **$45.99**

- ✅ Delivered Feb 12
- USB-C Cable 3-Pack, 6ft Fast Charging
  - [View on Amazon](https://www.amazon.com/dp/B08XYZ123)

**Order #114-9876543-7654321** • Feb 8, 2026 • **$32.49**

- ✅ Delivered Feb 10
- Product Name Here
  - [View on Amazon](https://www.amazon.com/dp/PRODUCT_ID)
- Another Product in Same Order
  - [View on Amazon](https://www.amazon.com/dp/PRODUCT_ID2)

---

**Key formatting elements:**

- Order number, date, and total on first line in bold
- Delivery status with checkmark emoji (✅)
- Product name as plain text on one line
- Product link indented on the next line as "View on Amazon"
- Multiple products listed as separate bullet points with their own indented links
- Clean, scannable layout for easy reading - product names are easy to scan,
  links are easy to locate

## Notes

### Session Persistence

- Login session is saved in `~/.cache/playwright-profiles/amazon/`
- This is a Docker volume that persists across container rebuilds
- Session includes cookies, localStorage, and authentication state
- You only need to log in manually once

### Amazon 2FA

- If Amazon requires two-factor authentication, you'll need to complete it during the manual login step
- The script will wait 2 minutes for you to complete any verification
- 2FA tokens and trusted device status are saved in the persistent session

### Product Data Notes

- **Individual product prices show "N/A"**: This is expected! Amazon's orders page doesn't display per-item prices (prices can change after purchase). Only the order total is shown.
- **Product images**: Extracted as thumbnail URLs (e.g., `https://m.media-amazon.com/images/I/...._SS142_.jpg`)
- **Product links**: Direct links to product pages for easy re-ordering or reference

### Debugging

- If orders don't load properly, run with `--headless=false` to see what's happening
- Use `--debug=true` to save screenshots and HTML for inspection
- Check the `./screenshots/` directory for error screenshots
- Amazon's page structure may change - selectors may need updating

### Selector Maintenance

- Amazon occasionally updates their UI
- If the script stops working, the CSS selectors may need updating
- Common selectors to check in `extractOrders()` function:
  - `.order-card` or `.order` - Main order container
  - `[data-order-id]` - Order ID attribute
  - `.order-date-invoice-item` - Order date
  - `.order-total .value` - Order total amount
  - `.yohtmlc-product-title` - Product names

### Timeout Policy

- Default timeout is 15 seconds (longer than default 5s due to Amazon page complexity)
- Increase with `--timeout=30000` if you have slow internet or the page is loading slowly

## Maintenance

- **Last Updated**: 2026-02-16
- **Site Version**: Works with Amazon.com as of Feb 2026
- **Dependencies**: playwright-extra, puppeteer-extra-plugin-stealth

## Migration

To migrate this script to the skill's permanent template directory:

```bash
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  /workspace/playwright/www.amazon.com
```

This will copy all actions for amazon.com to `~/.claude/templates/skills/playwright/actions/www.amazon.com/` for reuse across sessions.

---

## Migration Info

- **Migrated On**: 2026-02-16T19:04:05Z
- **Original Path**: /workspace/playwright/www.amazon.com/orders
- **Template Path**: /home/vscode/.claude/templates/skills/playwright/actions/www.amazon.com/orders

This action has been migrated to skill templates and is now reusable across sessions.
