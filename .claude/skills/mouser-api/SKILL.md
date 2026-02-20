---
name: mouser-api
description: Mouser Electronics API for part search, pricing, cart management, and order history via Python scripts. Use for Mouser price checks and component lookups.
allowed-tools: Bash, Read, Grep, Glob, Write
---

# Mouser API Skill

Direct access to the Mouser Electronics REST API via parameterized Python scripts.
Does NOT use the Mouser MCP server — scripts call the API directly.

## Prerequisites

- Python venv at `.claude/skills/mouser-api/scripts/.venv/`
- API keys sourced from `/workspace/.env` (automatic via `run.sh`)

If venv is missing, create it:

```bash
uv venv .claude/skills/mouser-api/scripts/.venv
uv pip install --python .claude/skills/mouser-api/scripts/.venv/bin/python requests
```

## Script Invocation

All scripts are run through the wrapper:

```bash
bash .claude/skills/mouser-api/scripts/run.sh <script>.py <subcommand> [args]
```

## Available Scripts

| Script | Subcommands | API Key Used |
|---|---|---|
| `search.py` | `keyword`, `part-number` | Part API key |
| `cart.py` | `get`, `add`, `update` | Order API key |
| `order.py` | `get`, `options` | Order API key |
| `order_history.py` | `list` | Order API key |

## Mandatory Start Procedure

**Before executing any workflow:**

1. Classify the task into ONE workflow below
2. If no workflow matches: "Unable to classify task. No matching workflow found."
3. State: "Task identified: [workflow name]"
4. Execute the matching workflow immediately

## Workflow 1: Part Search (DEFAULT)

Use when: searching for components, looking up part numbers, checking pricing/availability.

### Step 1 — Determine search type

- If the user provides an exact part number → use `part-number` subcommand
- Otherwise → use `keyword` subcommand

**IMPORTANT:** `part-number` search takes the **manufacturer part number (MPN)**, not
Mouser's catalog number. If you have a Mouser catalog number like `603-RC1206FR-07180RL`,
strip the prefix to get the MPN: `RC1206FR-07180RL`.

### Step 2 — Execute search

**Keyword search:**

```bash
bash .claude/skills/mouser-api/scripts/run.sh search.py keyword \
  --keyword "<search terms>" --records <1-50>
```

**Part number search:**

```bash
bash .claude/skills/mouser-api/scripts/run.sh search.py part-number \
  --part-number "<exact part number>"
```

### Step 3 — Apply pricing rules

When presenting pricing, follow the rules from `docs/Pricing-Guidelines.md`:

- **Price tier**: Match the price break to the order quantity
- **MOQ**: First tier indicates minimum order quantity — verify MOQ <= requested qty
- **Stock**: Verify `Availability` shows in stock (not backordered)

Checklist: Price tier matched, MOQ checked, Stock verified.

### Step 4 — Save raw data

Save the raw JSON response before formatting:

```bash
OUTFILE="temp/mouser-search-$(date +%Y%m%d-%H%M%S).json"
```

Include the file path in your response.

**Do NOT continue to other workflows.**

---

## Workflow 2: Cart Management

Use when: managing shopping cart items (viewing, adding, updating quantities).

### Get cart contents

```bash
bash .claude/skills/mouser-api/scripts/run.sh cart.py get --cart-key "<uuid>"
```

### Add item to cart

```bash
bash .claude/skills/mouser-api/scripts/run.sh cart.py add \
  --cart-key "<uuid>" --part-number "<mouser-pn>" --quantity <n>
```

Optional: `--customer-part-number "<ref>"`

### Update item quantity (0 to remove)

```bash
bash .claude/skills/mouser-api/scripts/run.sh cart.py update \
  --cart-key "<uuid>" --part-number "<mouser-pn>" --quantity <n>
```

**Do NOT continue to other workflows.**

---

## Workflow 3: Orders & History

Use when: checking order status, viewing order options, or listing past orders.

### Get order details

```bash
bash .claude/skills/mouser-api/scripts/run.sh order.py get --order-number "<number>"
```

### Get order options for a cart

```bash
bash .claude/skills/mouser-api/scripts/run.sh order.py options --cart-key "<uuid>"
```

### List order history

```bash
bash .claude/skills/mouser-api/scripts/run.sh order_history.py list --days <n>
```

Default: 30 days.

**Do NOT continue to other workflows.**

---

## Workflow 4: Bulk Order Item Extraction

Use when: extracting all items from multiple recent orders (e.g. for stock-in sheet creation).

### Step 1 — List order history

```bash
bash .claude/skills/mouser-api/scripts/run.sh order_history.py list --days 60 2>/dev/null
```

Returns `OrderHistoryItems[]` with `SalesOrderNumber` for each order.

### Step 2 — Fetch each order and aggregate items

```bash
for ORDER_NUM in <order1> <order2>; do
  bash .claude/skills/mouser-api/scripts/run.sh order.py get \
    --order-number "$ORDER_NUM" 2>/dev/null \
    | python3 -c "
import sys, json
data = json.load(sys.stdin)['data']
for line in data.get('OrderLines', []):
    info = line['ProductInfo']
    print(json.dumps({
      'order': '$ORDER_NUM',
      'mpn': info['ManufacturerPartNumber'],
      'mouser_pn': info['MouserPartNumber'],
      'manufacturer': info['ManufacturerName'],
      'description': info['PartDescription'],
      'quantity': line['Quantity'],
      'unit_price': line['UnitPrice'],
    }))
"
done
```

### Step 3 — Deduplicate by MPN (aggregate quantities across orders)

When the same MPN appears in multiple orders, sum the quantities. The `SalesOrderNumber`
field from `order_history.py list` is what you pass to `order.py get --order-number`.

**Do NOT continue to other workflows.**

---

## Output Format

All scripts return JSON to stdout:

```json
{"success": true, "data": { ... }}
```

On error:

```json
{"success": false, "error": "Error message"}
```

## Rate Limits

- Max 50 results per search
- 30 requests per minute
- 1,000 requests per day

## Reference

See `examples/api-reference.md` for complete API field reference and example commands.
