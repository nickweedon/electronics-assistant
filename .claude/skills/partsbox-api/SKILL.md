---
name: partsbox-api
description: "Direct PartsBox API access via Python scripts for inventory, stock, projects, and orders."
allowed-tools: Bash, Read, Grep, Glob, Write
---

# PartsBox API Skill

Direct Python script access to the PartsBox REST API for managing electronic
component inventory, stock tracking, projects/BOMs, orders, and storage locations.

## When to Use

Use this skill for ALL PartsBox inventory operations:

- Searching/listing parts, storage locations, projects, orders, lots
- Checking stock levels and part availability
- Managing inventory (add/remove/move stock)
- Working with project BOMs (entries, builds)
- Creating and receiving purchase orders
- Downloading files and images from parts

## Prerequisites

- `PARTSBOX_API_KEY` set in environment or `.env` file
- Python venv with `requests` at `.claude/skills/partsbox-api/scripts/.venv/`
- If venv missing: `uv venv .claude/skills/partsbox-api/scripts/.venv && uv pip install --python .claude/skills/partsbox-api/scripts/.venv/bin/python requests`

## Script Reference

All scripts are in `.claude/skills/partsbox-api/scripts/` and output JSON to stdout.

### Parts (`parts.py`)

| Command | Description |
|---------|-------------|
| `list` | List all parts |
| `get --id ID` | Get part details |
| `create --name NAME [--type TYPE] [--manufacturer M] [--mpn MPN] ...` | Create part |
| `update --id ID [--name N] [--description D] ...` | Update part |
| `delete --id ID` | Delete part |
| `stock --id ID` | Get total stock count |
| `lots --id ID` | List stock sources (per-lot) |
| `storage --id ID` | List stock sources (by location) |
| `add-meta --id ID --member-ids IDS` | Add members to meta-part |
| `remove-meta --id ID --member-ids IDS` | Remove meta-part members |
| `add-substitutes --id ID --substitute-ids IDS` | Add substitutes |
| `remove-substitutes --id ID --substitute-ids IDS` | Remove substitutes |

### Stock (`stock.py`)

| Command | Description |
|---------|-------------|
| `add --part-id ID --storage-id SID --quantity N [--price P] [--currency C]` | Add stock |
| `remove --part-id ID --storage-id SID --quantity N [--lot-id LID]` | Remove stock |
| `move --part-id ID --source-storage-id SID --target-storage-id TID --quantity N` | Move stock |
| `update --part-id ID --timestamp TS [--quantity N] [--price P]` | Update entry |

### Lots (`lots.py`)

| Command | Description |
|---------|-------------|
| `list` | List all lots |
| `get --id ID` | Get lot details |
| `update --id ID [--name N] [--tags T] ...` | Update lot |

### Storage (`storage.py`)

| Command | Description |
|---------|-------------|
| `list [--include-archived]` | List locations |
| `get --id ID` | Get location details |
| `create --name NAME [--description D] [--tags T]` | Create new location |
| `update --id ID [--comments C] [--tags T]` | Update metadata |
| `rename --id ID --name NAME` | Rename location |
| `archive --id ID` | Archive location |
| `restore --id ID` | Restore archived location |
| `settings --id ID [--full true/false] [--single-part true/false]` | Change settings |
| `parts --id ID` | List parts in location |
| `lots --id ID` | List lots in location |

### Projects (`projects.py`)

| Command | Description |
|---------|-------------|
| `list [--include-archived]` | List projects |
| `get --id ID` | Get project details |
| `create --name NAME [--description D] [--entries JSON]` | Create project |
| `update --id ID [--name N] [--description D]` | Update project |
| `delete --id ID` | Delete project |
| `archive --id ID` | Archive project |
| `restore --id ID` | Restore project |

### Project Entries (`project_entries.py`)

| Command | Description |
|---------|-------------|
| `get --project-id PID [--build-id BID]` | Get BOM entries |
| `add --project-id PID --entries JSON` | Add BOM entries |
| `update --project-id PID --entries JSON` | Update BOM entries |
| `delete --project-id PID --entry-ids IDS` | Delete BOM entries |

### Builds (`builds.py`)

| Command | Description |
|---------|-------------|
| `list --project-id PID` | List builds |
| `get --id ID` | Get build details |
| `update --id ID [--comments C]` | Update build |

### Orders (`orders.py`)

| Command | Description |
|---------|-------------|
| `list` | List all orders |
| `get --id ID` | Get order details |
| `create --vendor V [--order-number N] [--entries JSON]` | Create order |

### Order Entries (`order_entries.py`)

| Command | Description |
|---------|-------------|
| `get --order-id OID` | List items in order |
| `add --order-id OID --entries JSON` | Add items to order |
| `delete --order-id OID --stock-id SID` | Delete order entry |

### Order Receive (`order_receive.py`)

| Usage | Description |
|-------|-------------|
| `--order-id OID --storage-id SID [--entries JSON] [--comments C]` | Receive order |

### Files (`files.py`)

| Command | Description |
|---------|-------------|
| `url --file-id FID` | Get download URL |
| `download --file-id FID [-o PATH]` | Download file to disk |

## Running Scripts

Use the `run.sh` wrapper which handles venv activation and API key loading:

```bash
# Base command pattern:
bash .claude/skills/partsbox-api/scripts/run.sh {script}.py {subcommand} {args}

# Examples:
bash .claude/skills/partsbox-api/scripts/run.sh parts.py list
bash .claude/skills/partsbox-api/scripts/run.sh parts.py get --id "abc123"
bash .claude/skills/partsbox-api/scripts/run.sh storage.py create --name "SMD-Box-A1"
bash .claude/skills/partsbox-api/scripts/run.sh stock.py add --part-id "abc" --storage-id "def" --quantity 50
```

## Output Format

All scripts output JSON to stdout:

```json
// Success (single item):
{"success": true, "data": {...}}

// Success (list — all items returned, no pagination):
{"success": true, "total": 150, "data": [...]}

// Error:
{"success": false, "error": "Error message"}
```

**Filtering lists:** Scripts return all items. Use Python inline to filter, search, or transform:

```bash
# Find parts matching an MPN
bash .claude/skills/partsbox-api/scripts/run.sh parts.py list 2>/dev/null \
  | python3 -c "
import sys, json
parts = json.load(sys.stdin)['data']
matches = [p for p in parts if 'RC0805' in (p.get('part/mpn') or '')]
print(json.dumps(matches, indent=2))
"

# Filter storage by tag (storage/tags is a list, not a string)
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list 2>/dev/null \
  | python3 -c "
import sys, json
locs = json.load(sys.stdin)['data']
smd = [p for p in locs if 'type_smd-box' in (p.get('storage/tags') or [])]
print(json.dumps(smd[:10], indent=2))
"
```

## Permission Rules

- **Read-only operations** (list, get, stock): Execute freely
- **Write operations** (create, update, delete, add/remove stock, archive): Always ask
  the user for confirmation before executing
- **Destructive operations** (delete part, delete project): Require explicit user approval

## API Conventions

- **Base URL**: `https://api.partsbox.com/api/1/{operation}`
- **Method**: All operations use HTTP POST
- **Auth**: `Authorization: APIKey {PARTSBOX_API_KEY}`
- **Field naming**: All fields use "/" separator (e.g., `part/name`, `stock/quantity`)
- **IDs**: 26-character compact UUIDs
- **Timestamps**: UNIX UTC milliseconds
- **Part types**: `local`, `linked`, `sub-assembly`, `meta`
- **Files**: Downloaded via GET from `https://partsbox.com/files/{file_id}`
- **Tags**: Stored as Python lists — always use `'tag' in (p.get('field/tags') or [])` to check membership

## Storage Location Recommendations

Storage locations use structured tags (e.g., `type_smd-box`, `esd_yes`) to enable
intelligent component placement. Always fetch all locations and filter in Python —
do NOT attempt JMESPath tag filtering.

**For detailed guidance:** See `examples/storage-recommendations.md` for tag conventions,
Python filtering patterns, workflow steps, and example recommendations.

## Part Creation Notes

**Always check before creating:** Before creating any new part definition, search for
an existing part with the same name or MPN. Creating duplicate parts pollutes inventory
and breaks stock tracking.

**Bulk pre-check (when adding many items):** Fetch all existing parts first and match
the full list before creating anything:

```bash
# 1. Fetch all parts once
bash .claude/skills/partsbox-api/scripts/run.sh parts.py list 2>/dev/null \
  | python3 -c "
import sys, json
parts = json.load(sys.stdin)['data']
# Build lookup maps
by_mpn = {(p.get('part/mpn') or '').upper(): p for p in parts if p.get('part/mpn')}
by_name = {(p.get('part/name') or '').upper(): p for p in parts if p.get('part/name')}
import pickle
with open('/tmp/parts_lookup.pkl', 'wb') as f:
    pickle.dump({'by_mpn': by_mpn, 'by_name': by_name}, f)
print(f'Loaded {len(parts)} parts')
"

# 2. Check a specific MPN
python3 -c "
import pickle, json
d = pickle.load(open('/tmp/parts_lookup.pkl','rb'))
match = d['by_mpn'].get('RC0805FR-071R8L'.upper())
print(json.dumps(match, indent=2) if match else 'NOT FOUND')
"
```

This avoids N individual API calls and prevents partial-run duplicates.

**Tag character restrictions:** Only alphanumeric characters, hyphens, and underscores
are accepted. Special characters like `%` cause a silent `400 Bad Request` with no
useful error message. Use plain equivalents: `1pct` not `1%`, `50v` not `50V`, etc.

**Part notes format:** Always use the `templates/part-notes.hbs` template as the
structure for `--notes` when creating or updating parts.

Template variables:

| Variable | Description |
|----------|-------------|
| `description` | Brief one-line part description |
| `specifications` | Array of spec strings (e.g. `["Resistance: 1.8 Ohm", "Tolerance: 1%"]`) |
| `vendor` | Supplier name (e.g. `Mouser Electronics`) |
| `orderNumber` | Order/invoice number |
| `receivedDate` | Date received (YYYY-MM-DD) |
| `quantity` | Quantity received |
| `unitPrice` | Unit price |
| `vendorLink` | Full URL to the product page |
| `additionalNotes` | Optional extra notes (e.g. sample units, lot info) |

Render with:

```bash
node /home/vscode/claude-monorepo/claude/lib/render-skill.js \
  --template part-notes.hbs \
  --template-dir /workspace/.claude/skills/partsbox-api/templates \
  --data-file /tmp/part-notes-data.json \
  --output /tmp/part-notes.txt
```

Then pass the rendered text as the `--notes` argument to `parts.py create` or
`parts.py update`.

## Stock-In Workflow

When receiving new components from suppliers, use this workflow to catalog parts and create documentation:

**Quick workflow:**

1. **Check for existing parts first** — fetch all parts and match incoming items by
   MPN/name before creating any new parts (see [Part Creation Notes](#part-creation-notes)).
   Reuse existing part IDs where found.
2. Create part entries with `parts.py create` **only for items with no match**, using
   detailed `--notes` rendered from `templates/part-notes.hbs`
3. Save returned part IDs
4. **Upload product images** from supplier pages to PartsBox (see [Image Upload Workflow](#image-upload-workflow) below)
5. Determine storage locations (see `examples/storage-guidelines.md`)
6. Generate documentation using template at `templates/stock-in.md.hbs`
   - **Download images locally before rendering** — the template uses `imageFilename` to embed
     thumbnails from `data/stock-in/images/`. Images must exist locally before rendering.
     (PartsBox upload in step 4 is separate — it populates PartsBox's own image gallery.)
7. Physically store components
8. Add stock with `stock.py add` AFTER physical placement

**Template rendering:**

```bash
node /home/vscode/claude-monorepo/claude/lib/render-skill.js \
  --template stock-in.md.hbs \
  --template-dir /workspace/.claude/skills/partsbox-api/templates \
  --data-file /tmp/stock-in-data.json \
  --output data/stock-in/supplier-YYYY-MM-DD-description.md
```

**For detailed instructions:** See `examples/stock-in-workflow.md` for part creation format, template data structure, and complete workflow steps.

**For storage guidelines:** See `examples/storage-guidelines.md` for SMD box usage rules, ESD-safe box criteria, and decision examples.

## Image Upload Workflow

When creating parts from supplier orders, upload product images to PartsBox so parts
have visual reference. The download method varies by supplier.

### Step 1: Download image from supplier

**Mouser** — Use the Mouser API's `ImagePath` field. Do NOT use Playwright (Mouser
product pages are blocked by DataDome bot protection):

```bash
# 1. Search by MPN to get the ImagePath URL
bash .claude/skills/mouser-api/scripts/run.sh search.py part-number \
  --part-number "<MPN>" 2>/dev/null \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
parts = d.get('data', {}).get('Parts', [])
print(parts[0].get('ImagePath', '') if parts else '')
"

# 2. Download directly from the CDN URL
wget -q "<image-url>" -O /tmp/part-image.jpg \
  --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

**AliExpress** — Use the `Skill` tool with `skill: "playwright"` to run the
`aliexpress.com/download-item-image` action:

- `--product-url` — the AliExpress item URL
- `--output` — `/tmp/part-image.jpg`

**Other suppliers** — Use `wget`/`curl` if the image URL is directly accessible.
Use the `Skill` tool with `skill: "playwright"` only when browser automation is required.

### Step 2: Upload image to PartsBox

Run the committed upload script directly:

```bash
node /workspace/playwright/partsbox.com/upload-item-image/script.js \
  --part-id=<part-id> \
  --image-path=/tmp/part-image.jpg
```

**IMPORTANT:** This script requires `--key=value` format (equals sign, no space).
Using `--key value` (space-separated) will silently set the value to `true` and fail.

The script handles login automatically (switches to headed mode if needed, saves
session cookies for reuse).

**CRITICAL**: When invoking via the `playwright` skill, use the `Skill` tool (NOT
the `Task` tool). There is NO `playwright` agent type — `playwright` is a skill only.

**Bulk uploads (CDN sources like Mouser):** Call the upload script directly for each
part — no need for the Playwright skill when images are available via direct URL:

```bash
# For each part: wget image, then upload
wget -q "<image-url>" -O /tmp/part-image.jpg --user-agent="Mozilla/5.0 ..."
node /workspace/playwright/partsbox.com/upload-item-image/script.js \
  --part-id=<part-id> --image-path=/tmp/part-image.jpg
```

**When to upload images:**

- After creating new parts with `parts.py create` during stock-in
- When a part in PartsBox is missing a product image
- When updating parts with better/higher resolution images

## API Documentation Reference

**Official PartsBox API Documentation**: <https://partsbox.com/api.html>

**IMPORTANT**: Before reporting that an API method does not exist or is not implemented:

1. Check the official API documentation at the URL above
2. Verify the endpoint path, parameters, and response format
3. If the endpoint exists in the API docs but not in this skill's scripts, implement it
4. Do NOT claim a method doesn't exist without checking the official docs first

**When implementing new API methods**:

1. Use WebFetch to retrieve the API documentation for the specific endpoint
2. Add the corresponding command to the appropriate Python script
3. Update the command table in this SKILL.md
4. Test the implementation with a real API call
5. Update the examples if needed
