# list-order-items - lcsc.com

**Action**: list-order-items
**Site**: lcsc.com
**Created**: 2026-02-19

## Description

Retrieve all line items within a specific LCSC order. Accepts an order token (hex ID)
or a full detail URL. Requires saved cookies from a prior login session.

## Authentication

Cookies must be saved at:

```
~/.cache/playwright-profiles/lcsc.com/cookies.json
```

## Parameters

| Parameter  | Required | Default | Description                                                         |
|------------|----------|---------|---------------------------------------------------------------------|
| `orderId`  | Yes      | —       | Order hex token or full detail URL (from `list-orders` output)      |
| `headless` | No       | `true`  | Run browser in headless mode                                        |
| `timeout`  | No       | `20000` | Timeout in milliseconds (large orders with 298+ items need more time)|

## Usage

```bash
cd ./playwright/lcsc.com/list-order-items

# Using the hex token (from list-orders orderToken field)
node script.js --orderId=B5A239BAC5A96F0F8AF86807A40667EC

# Using the full detail URL
node script.js --orderId=https://www.lcsc.com/order/detail/B5A239BAC5A96F0F8AF86807A40667EC

# Headed mode (for debugging)
node script.js --orderId=B5A239BAC5A96F0F8AF86807A40667EC --headless=false
```

## Composing with list-orders

```bash
# Get orders, then fetch items for the first one
ORDERS=$(node ./playwright/lcsc.com/list-orders/script.js)
TOKEN=$(echo "$ORDERS" | jq -r '.data[0].orderToken')
node ./playwright/lcsc.com/list-order-items/script.js --orderId="$TOKEN"
```

## Output Format

```json
{
  "success": true,
  "data": {
    "order": {
      "order_no": "25011503YXXXXXXX",
      "order_status": "Delivered",
      "order_date": "2026-01-15",
      "order_total": "$ 268"
    },
    "items": [
      {
        "lcscCode": "C137394",
        "lcscUrl": "https://www.lcsc.com/product-detail/C137394.html",
        "mpn": "RC1206FR-070RL",
        "manufacturer": "YAGEO",
        "description": "1206 70Ω ±1% 1/4W Thick Film Resistors",
        "quantityOrdered": "100",
        "quantityShipped": "100",
        "unitPrice": "$0.0041",
        "extPrice": "$0.41"
      }
    ]
  },
  "metadata": {
    "url": "https://www.lcsc.com/order/detail/B5A239BAC5A96F0F8AF86807A40667EC",
    "timestamp": "2026-02-19T04:00:00.000Z",
    "duration": 12000,
    "itemCount": 298
  }
}
```

## Notes

- LCSC is a Vue SPA — uses `networkidle` + 3s extra wait for all product items to render
- Large orders (200+ items) may need `--timeout=30000`
- Screenshots on error are saved to `./screenshots/`
