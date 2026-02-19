# list-orders - lcsc.com

**Action**: list-orders
**Site**: lcsc.com
**Created**: 2026-02-19

## Description

Retrieve all orders from the LCSC account order list page. Requires saved cookies
from a prior login session (see Authentication below).

## Authentication

Cookies must be saved at:

```
~/.cache/playwright-profiles/lcsc.com/cookies.json
```

If cookies are missing or expired, navigate to `https://www.lcsc.com/user/order` in
the pw-server headed browser, log in manually, then save cookies via exec.js.

## Parameters

| Parameter  | Required | Default | Description                        |
|------------|----------|---------|------------------------------------|
| `headless` | No       | `true`  | Run browser in headless mode       |
| `timeout`  | No       | `15000` | Timeout in milliseconds            |

## Usage

```bash
cd ./playwright/lcsc.com/list-orders

# Basic usage
node script.js

# Headed mode (for debugging)
node script.js --headless=false
```

## Output Format

```json
{
  "success": true,
  "data": [
    {
      "orderId": "25011503YXXXXXXX",
      "orderToken": "B5A239BAC5A96F0F8AF86807A40667EC",
      "poNumber": "",
      "orderDate": "2026-01-15",
      "status": "Delivered",
      "totalAmount": "$ 268",
      "detailUrl": "https://www.lcsc.com/order/detail/B5A239BAC5A96F0F8AF86807A40667EC"
    }
  ],
  "metadata": {
    "url": "https://www.lcsc.com/order/list",
    "timestamp": "2026-02-19T04:00:00.000Z",
    "duration": 8500,
    "count": 1
  }
}
```

The `orderToken` field is the hex ID needed to pass to `list-order-items`.

## Notes

- LCSC is a Vue SPA — uses `networkidle` + 3s extra wait for table to render
- Navigating to `/user/order` redirects to home without cookies; the script uses `/order/list` directly
- Screenshots on error are saved to `./screenshots/`
