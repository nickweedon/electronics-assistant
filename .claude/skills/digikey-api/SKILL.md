---
name: digikey-api
description: "Digikey Electronics API for product search, pricing, MyLists management via Python scripts. Use for Digikey part lookups, price checks, and list operations."
user-invokable: false
---

# DigiKey API Skill

Direct access to the DigiKey REST API via parameterized Python scripts.
Does NOT use the DigiKey MCP server — scripts call the API directly.

## Prerequisites

- Python venv at `.claude/skills/digikey-api/scripts/.venv/`
- API keys sourced from `/opt/src/mcp/digikey_mcp/.env` (automatic via `run.sh`)
- User OAuth tokens at `.claude/skills/digikey-api/scripts/.digikey_tokens` (for MyLists)

If venv is missing, create it:

```bash
uv venv .claude/skills/digikey-api/scripts/.venv
uv pip install --python .claude/skills/digikey-api/scripts/.venv/bin/python -r .claude/skills/digikey-api/scripts/requirements.txt
```

If user tokens are missing (needed for MyLists only):

```bash
cp /mnt/c/docker/digikey-tokens/.digikey_tokens .claude/skills/digikey-api/scripts/
```

## Script Invocation

All scripts are run through the wrapper:

```bash
bash .claude/skills/digikey-api/scripts/run.sh <script>.py <subcommand> [args]
```

## Available Scripts

| Script | Subcommands | Auth Type |
|---|---|---|
| `search.py` | `keyword`, `product-details`, `substitutions`, `media`, `manufacturers`, `categories` | Client credentials |
| `pricing.py` | `product`, `digi-reel` | Client credentials |
| `lists.py` | `get-all`, `create`, `get`, `rename`, `delete` | User OAuth |
| `list_parts.py` | `get-all`, `add`, `get`, `update`, `delete` | User OAuth |
| `auth.py` | `status`, `refresh`, `login-url`, `set-tokens` | N/A |

## Mandatory Start Procedure

**Before executing any workflow:**

1. Classify the task into ONE workflow below
2. If no workflow matches: "Unable to classify task. No matching workflow found."
3. State: "Task identified: [workflow name]"
4. Execute the matching workflow immediately

## Workflow 1: Part Search (DEFAULT)

Use when: searching for components, looking up part numbers, checking availability.

### Step 1 — Determine search type

- Exact DigiKey/manufacturer part number → use `product-details` subcommand
- General search terms → use `keyword` subcommand

### Step 2 — Execute search

**Keyword search:**

```bash
bash .claude/skills/digikey-api/scripts/run.sh search.py keyword \
  --keywords "<search terms>" --limit <1-50>
```

**Product details:**

```bash
bash .claude/skills/digikey-api/scripts/run.sh search.py product-details \
  --product-number "<part number>"
```

### Step 3 — Apply pricing rules

When presenting pricing, follow the rules from `docs/Pricing-Guidelines.md`:

- **Price tier**: Match the price break to the order quantity
- **MOQ**: First tier indicates minimum order quantity — verify MOQ <= requested qty
- **Stock**: Verify QuantityAvailable shows in stock

Checklist: Price tier matched, MOQ checked, Stock verified.

### Step 4 — Save raw data

Save the raw JSON response before formatting:

```bash
OUTFILE="temp/digikey-search-$(date +%Y%m%d-%H%M%S).json"
```

Include the file path in your response.

**Do NOT continue to other workflows.**

---

## Workflow 2: Pricing Check

Use when: checking pricing tiers, comparing quantities, DigiReel pricing.

### Get product pricing

```bash
bash .claude/skills/digikey-api/scripts/run.sh pricing.py product \
  --product-number "<part number>" --quantity <n>
```

### Get DigiReel pricing

```bash
bash .claude/skills/digikey-api/scripts/run.sh pricing.py digi-reel \
  --product-number "<part number>" --quantity <n>
```

Apply pricing rules from `docs/Pricing-Guidelines.md`.

**Do NOT continue to other workflows.**

---

## Workflow 3: MyLists Management

Use when: managing DigiKey lists and parts within lists.

### List operations

```bash
# Get all lists
bash .claude/skills/digikey-api/scripts/run.sh lists.py get-all

# Create list
bash .claude/skills/digikey-api/scripts/run.sh lists.py create --name "<name>"

# Get list details
bash .claude/skills/digikey-api/scripts/run.sh lists.py get --list-id "<id>" --include-parts

# Rename list
bash .claude/skills/digikey-api/scripts/run.sh lists.py rename --list-id "<id>" --name "<new name>"

# Delete list (ask user first)
bash .claude/skills/digikey-api/scripts/run.sh lists.py delete --list-id "<id>"
```

### Part operations

```bash
# Get all parts from a list
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py get-all --list-id "<id>"

# Add parts to a list
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py add \
  --list-id "<id>" --parts-json '[{"RequestedPartNumber": "296-8875-1-ND"}]'

# Get single part
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py get \
  --list-id "<id>" --part-id "<unique-id>"

# Update part
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py update \
  --list-id "<id>" --part-id "<unique-id>" --part-json '{"Notes": "Updated"}'

# Delete part (ask user first)
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py delete \
  --list-id "<id>" --part-id "<unique-id>"
```

**Permission rules:**

- Read operations (get-all, get): Execute freely
- Write operations (create, add, update, rename): Ask user for confirmation
- Destructive operations (delete): Require explicit user approval

**Do NOT continue to other workflows.**

---

## Workflow 4: OAuth Management

Use when: checking token status, refreshing tokens, initial setup.

```bash
# Check token status
bash .claude/skills/digikey-api/scripts/run.sh auth.py status

# Force-refresh user token
bash .claude/skills/digikey-api/scripts/run.sh auth.py refresh

# Generate OAuth login URL
bash .claude/skills/digikey-api/scripts/run.sh auth.py login-url

# Manually set tokens
bash .claude/skills/digikey-api/scripts/run.sh auth.py set-tokens \
  --user-token "<token>" --refresh-token "<token>"
```

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

## JMESPath Queries

Search, lists, and parts scripts support `--query` for filtering and projection.

### Custom Functions

| Function | Description | Example |
|----------|-------------|---------|
| `nvl(val, default)` | Return default if null | `nvl(Field, 'N/A')` |
| `int(val)` | Convert to integer | `int('100')` |
| `str(val)` | Convert to string | `str(100)` |
| `regex_replace(pat, repl, val)` | Regex substitution | `regex_replace(' ohm$', '', '100 ohm')` |

## Rate Limits

- Max 50 results per keyword search page
- Client credentials tokens expire after ~30 minutes
- User tokens auto-refresh on 401

## Reference

See `examples/api-reference.md` for complete API field reference.
See `examples/basic-usage.md` for practical usage examples.
