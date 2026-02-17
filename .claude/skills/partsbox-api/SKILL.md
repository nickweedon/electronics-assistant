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

- `PARTSBOX_API_KEY` set in environment or `/mnt/c/docker/partsbox-mcp-env`
- Python venv with `requests` and `jmespath` at `.claude/skills/partsbox-api/scripts/.venv/`
- If venv missing: `uv venv .claude/skills/partsbox-api/scripts/.venv && uv pip install --python .claude/skills/partsbox-api/scripts/.venv/bin/python requests jmespath`

## Script Reference

All scripts are in `.claude/skills/partsbox-api/scripts/` and output JSON to stdout.

### Parts (`parts.py`)

| Command | Description |
|---------|-------------|
| `list [--query Q] [--limit N] [--offset N]` | List all parts |
| `get --id ID` | Get part details |
| `create --name NAME [--type TYPE] [--manufacturer M] [--mpn MPN] ...` | Create part |
| `update --id ID [--name N] [--description D] ...` | Update part |
| `delete --id ID` | Delete part |
| `stock --id ID` | Get total stock count |
| `lots --id ID [--query Q] [--limit N]` | List stock sources (per-lot) |
| `storage --id ID [--query Q] [--limit N]` | List stock sources (by location) |
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
| `list [--query Q] [--limit N]` | List all lots |
| `get --id ID` | Get lot details |
| `update --id ID [--name N] [--tags T] ...` | Update lot |

### Storage (`storage.py`)

| Command | Description |
|---------|-------------|
| `list [--query Q] [--limit N] [--include-archived]` | List locations |
| `get --id ID` | Get location details |
| `create --name NAME [--description D] [--tags T]` | Create new location |
| `update --id ID [--comments C] [--tags T]` | Update metadata |
| `rename --id ID --name NAME` | Rename location |
| `archive --id ID` | Archive location |
| `restore --id ID` | Restore archived location |
| `settings --id ID [--full true/false] [--single-part true/false]` | Change settings |
| `parts --id ID [--query Q] [--limit N]` | List parts in location |
| `lots --id ID [--query Q] [--limit N]` | List lots in location |

### Projects (`projects.py`)

| Command | Description |
|---------|-------------|
| `list [--query Q] [--limit N] [--include-archived]` | List projects |
| `get --id ID` | Get project details |
| `create --name NAME [--description D] [--entries JSON]` | Create project |
| `update --id ID [--name N] [--description D]` | Update project |
| `delete --id ID` | Delete project |
| `archive --id ID` | Archive project |
| `restore --id ID` | Restore project |

### Project Entries (`project_entries.py`)

| Command | Description |
|---------|-------------|
| `get --project-id PID [--build-id BID] [--query Q]` | Get BOM entries |
| `add --project-id PID --entries JSON` | Add BOM entries |
| `update --project-id PID --entries JSON` | Update BOM entries |
| `delete --project-id PID --entry-ids IDS` | Delete BOM entries |

### Builds (`builds.py`)

| Command | Description |
|---------|-------------|
| `list --project-id PID [--query Q]` | List builds |
| `get --id ID` | Get build details |
| `update --id ID [--comments C]` | Update build |

### Orders (`orders.py`)

| Command | Description |
|---------|-------------|
| `list [--query Q] [--limit N]` | List all orders |
| `get --id ID` | Get order details |
| `create --vendor V [--order-number N] [--entries JSON]` | Create order |

### Order Entries (`order_entries.py`)

| Command | Description |
|---------|-------------|
| `get --order-id OID [--query Q]` | List items in order |
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
bash .claude/skills/partsbox-api/scripts/run.sh parts.py list --limit 10
bash .claude/skills/partsbox-api/scripts/run.sh parts.py get --id "abc123"
bash .claude/skills/partsbox-api/scripts/run.sh storage.py create --name "SMD-Box-A1"
bash .claude/skills/partsbox-api/scripts/run.sh stock.py add --part-id "abc" --storage-id "def" --quantity 50
```

## Output Format

All scripts output JSON to stdout:

```json
// Success (single item):
{"success": true, "data": {...}}

// Success (paginated list):
{"success": true, "total": 150, "offset": 0, "limit": 50,
 "has_more": true, "data": [...], "query_applied": null}

// Error:
{"success": false, "error": "Error message"}
```

## JMESPath Queries

All list operations support `--query` for filtering and projection.

### Critical Syntax Rules

1. **Field names use "/" separator** - Always use double quotes: `"part/name"`, NOT backticks
2. **Use nvl() for nullable fields** - Prevents null errors in contains/comparisons
3. **Backticks for literals** - `\`[]\`` for empty array, `\`0\`` for zero

### Custom Functions

| Function | Description | Example |
|----------|-------------|---------|
| `nvl(val, default)` | Return default if null | `nvl("part/name", '')` |
| `int(val)` | Convert to integer | `int('100')` -> 100 |
| `str(val)` | Convert to string | `str(100)` -> '100' |
| `regex_replace(pat, repl, val)` | Regex substitution | `regex_replace(' ohm$', '', '100 ohm')` |

### Example Queries

```bash
# Search parts by name (safe with nvl)
--query '[?contains(nvl("part/name", '"'"''"'"'), '"'"'resistor'"'"')]'

# Filter by tag
--query '[?contains(nvl("part/tags", `[]`), '"'"'SMD'"'"')]'

# Sort by name
--query 'sort_by(@, &"part/name")'

# Get specific fields only
--query '[].{id: "part/id", name: "part/name"}'
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

## Storage Location Recommendations

Storage locations use structured tags (e.g., `type_smd-box`, `esd_yes`) to enable intelligent component placement. Query by tags to find appropriate storage, check descriptions for dimensions, and verify availability.

**Quick tag queries:**

```bash
# Find SMD boxes
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
  --query '[?contains("storage/tags", '"'"'type_smd-box'"'"')]'

# Find ESD-safe storage
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
  --query '[?contains("storage/tags", '"'"'esd_yes'"'"')]'
```

**For detailed guidance:** See `examples/storage-recommendations.md` for tag conventions, querying patterns, workflow steps, and example recommendations.

## Stock-In Workflow

When receiving new components from suppliers, use this workflow to catalog parts and create documentation:

**Quick workflow:**

1. Create part entries with `parts.py create` using detailed `--notes` (purchase info, specs, supplier links)
2. Save returned part IDs
3. Determine storage locations (see `examples/storage-guidelines.md`)
4. Generate documentation using template at `templates/stock-in.md.hbs`
5. Physically store components
6. Add stock with `stock.py add` AFTER physical placement

**Template rendering:**

```bash
node /home/vscode/claude-monorepo/claude/lib/template-renderer.js \
  --template .claude/skills/partsbox-api/templates/stock-in.md.hbs \
  --data /tmp/stock-in-data.json \
  --output data/stock-in/supplier-YYYY-MM-DD-description.md
```

**For detailed instructions:** See `examples/stock-in-workflow.md` for part creation format, template data structure, and complete workflow steps.

**For storage guidelines:** See `examples/storage-guidelines.md` for SMD box usage rules, ESD-safe box criteria, and decision examples.

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
