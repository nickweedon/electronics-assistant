# Get Order URL - Mouser Electronics

Extracts the order detail page URL for a given Mouser sales order number.
Handles DataDome bot-protection and login automatically — switches to headed
mode when a challenge or login is required, then saves session cookies for
future headless runs.

## Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `--order-number` | Yes | Mouser sales order number (e.g. `278499916`) | - |
| `--debug` | No | Run in headed mode for visual debugging | `false` |
| `--timeout` | No | Per-navigation timeout in milliseconds | `30000` |

## Usage

```bash
node /workspace/playwright/mouser.com/get-order-url/script.js \
  --order-number=278499916
```

## Output

```json
{
  "success": true,
  "data": {
    "orderNumber": "278499916",
    "orderUrl": "https://www.mouser.com/account/orders/detail?qs=..."
  },
  "metadata": {
    "timestamp": "2026-02-20T14:00:00.000Z",
    "duration": 8500,
    "browser": "chromium"
  }
}
```

## Session / Login Flow

1. Loads saved cookies from `~/.cache/playwright-profiles/mouser/cookies.json`
2. Navigates to `https://www.mouser.com/account/orders` headlessly
3. If DataDome challenge OR login page detected → relaunches headed, shows
   `xmessage` desktop alert, waits up to 5 min for user to complete
4. Saves refreshed cookies, then extracts the order link

## Notes

- Session cookies are stored in a persistent Docker volume — they survive
  container rebuilds and are shared with other Mouser playwright actions
- Mouser's DataDome protection may trigger on first run or after cookie
  expiry; subsequent runs with valid cookies are typically headless
- The `qs` token in the order URL is an opaque server-side value — it cannot
  be reconstructed from the order number; this script is the only reliable
  way to obtain it
