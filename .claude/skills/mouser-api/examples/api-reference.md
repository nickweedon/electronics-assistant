# Mouser API Quick Reference

## Script Invocation Pattern

```bash
bash .claude/skills/mouser-api/scripts/run.sh <script>.py <subcommand> [args]
```

## Search Operations (uses MOUSER_PART_API_KEY)

### Keyword Search

```bash
bash .claude/skills/mouser-api/scripts/run.sh search.py keyword \
  --keyword "LM7805" \
  --records 10 \
  --start 0
```

- `--keyword` (required): Search term
- `--records` (1-50, default 50): Max results per request
- `--start` (default 0): Pagination offset

### Part Number Search

```bash
bash .claude/skills/mouser-api/scripts/run.sh search.py part-number \
  --part-number "LM7805CT"
```

- `--part-number` (required): Exact Mouser or manufacturer part number

### Search Response Fields

Key fields in each part from `SearchResults.Parts[]`:

| Field | Description |
|---|---|
| `MouserPartNumber` | Mouser's part number |
| `ManufacturerPartNumber` | Manufacturer's part number |
| `Manufacturer` | Manufacturer name |
| `Description` | Part description |
| `DataSheetUrl` | Link to datasheet PDF |
| `ImagePath` | Product image URL |
| `ProductDetailUrl` | Mouser product page |
| `Category` | Product category |
| `LifecycleStatus` | e.g., "Active" |
| `ROHSStatus` | e.g., "RoHS Compliant" |
| `Availability` | Stock status text |
| `Min` | Minimum order quantity |
| `Mult` | Order multiple |
| `LeadTime` | Lead time string |
| `PriceBreaks` | Array of `{Quantity, Price, Currency}` |

## Cart Operations (uses MOUSER_ORDER_API_KEY)

### Get Cart

```bash
bash .claude/skills/mouser-api/scripts/run.sh cart.py get \
  --cart-key "your-uuid-here"
```

### Add to Cart

```bash
bash .claude/skills/mouser-api/scripts/run.sh cart.py add \
  --cart-key "your-uuid-here" \
  --part-number "595-LM7805CT" \
  --quantity 10 \
  --customer-part-number "MY-REF-001"
```

- `--customer-part-number` is optional

### Update Cart Item

```bash
bash .claude/skills/mouser-api/scripts/run.sh cart.py update \
  --cart-key "your-uuid-here" \
  --part-number "595-LM7805CT" \
  --quantity 5
```

- Set `--quantity 0` to remove the item

## Order Operations (uses MOUSER_ORDER_API_KEY)

### Get Order Details

```bash
bash .claude/skills/mouser-api/scripts/run.sh order.py get \
  --order-number "12345678"
```

### Get Order Options

```bash
bash .claude/skills/mouser-api/scripts/run.sh order.py options \
  --cart-key "your-uuid-here"
```

Returns: billing/shipping addresses, shipping methods, payment methods, currency.

## Order History (uses MOUSER_ORDER_API_KEY)

### List Past Orders

```bash
bash .claude/skills/mouser-api/scripts/run.sh order_history.py list \
  --days 30
```

- `--days` (default 30, min 1): Number of days to look back

## API Configuration

### Dual API Key System

Mouser requires two separate API keys:

| Variable | Used For | Get From |
|---|---|---|
| `MOUSER_PART_API_KEY` | Search endpoints | <https://www.mouser.com/api-hub/> |
| `MOUSER_ORDER_API_KEY` | Cart, order, history | My Mouser > APIs |

### Other Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MOUSER_API_BASE_URL` | `https://api.mouser.com/api/v1` | API base URL |
| `MOUSER_API_TIMEOUT` | `30` | Request timeout in seconds |

### Rate Limits

- Max 50 results per search request
- 30 requests per minute
- 1,000 requests per day

## Output Format

All scripts return JSON to stdout:

```json
{"success": true, "data": { ... }}
```

On error:

```json
{"success": false, "error": "Error message"}
```
