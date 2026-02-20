# Storage Location Metadata & Recommendations

Storage locations use structured tags and descriptions to enable intelligent component placement recommendations.

## Tag Naming Convention

Tags follow a **structured `type_value` format** using underscores for consistent filtering:

**Common tag categories:**

- `type_{smd-box|drawer-cabinet|plano-stowaway|...}` - Storage container type
- `material_{plastic|metal|cardboard|...}` - Container material
- `esd_{yes|no}` - ESD-safe status for sensitive components
- `capacity_{value}` - Approximate compartment capacity (e.g., `capacity_300pcs-1206`)
- `size_{tiny|small|medium|large}` - Relative compartment size
- `max_{Nmm}` - Maximum component dimension (e.g., `max_30mm`)

Additional tags may identify specific boxes: `cabinet_{1-5}`, `box_{1-5}`, etc.

**Note:** The underscore delimiter is used because the PartsBox API does not support colons in tags.

**Important:** `storage/tags` is a Python **list**, not a string. Always filter using
Python list membership, not string operations.

## Querying Storage by Tags

Fetch all storage locations and filter in Python:

```bash
# Fetch all storage locations (use high limit to get all)
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list 2>/dev/null \
  | python3 -c "
import sys, json
locs = json.load(sys.stdin)['data']

# Filter by type tag
smd_boxes = [p for p in locs if 'type_smd-box' in (p.get('storage/tags') or [])]
print(f'SMD boxes: {len(smd_boxes)}')
for p in smd_boxes[:10]:
    print(f\"{p['storage/name']} | id={p['storage/id']}\")
"
```

**Filter by multiple tags (AND logic):**

```bash
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list 2>/dev/null \
  | python3 -c "
import sys, json
locs = json.load(sys.stdin)['data']

# ESD-safe SMD boxes only
esd_smd = [p for p in locs
           if 'type_smd-box' in (p.get('storage/tags') or [])
           and 'esd_yes' in (p.get('storage/tags') or [])]
print(f'ESD-safe SMD boxes: {len(esd_smd)}')
for p in esd_smd[:10]:
    print(f\"{p['storage/name']} | id={p['storage/id']}\")
"
```

**Get all unique tags (to discover what tags exist):**

```bash
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list 2>/dev/null \
  | python3 -c "
import sys, json
locs = json.load(sys.stdin)['data']
all_tags = sorted({t for p in locs for t in (p.get('storage/tags') or [])})
print('All unique tags:')
for t in all_tags:
    print(f'  {t}')
"
```

## Finding Storage Dimensions

Storage location dimensions and specifications are stored in the **`storage/description`** field.

```bash
bash .claude/skills/partsbox-api/scripts/run.sh storage.py get --id <storage-id>
```

**Important:** All storage locations of the same type (matching `type_` tag prefix) will have
the same physical dimensions. You only need to check one location's description to understand
the size constraints for all locations of that type.

## Finding Empty Storage Locations

To find empty SMD boxes for assigning to new parts:

```bash
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list 2>/dev/null \
  | python3 -c "
import sys, json
locs = json.load(sys.stdin)['data']

# Get non-ESD SMD boxes, sorted alphabetically
non_esd_smd = [p for p in locs
               if 'type_smd-box' in (p.get('storage/tags') or [])
               and 'esd_no' in (p.get('storage/tags') or [])]
non_esd_smd.sort(key=lambda x: x.get('storage/name',''))

print(f'Non-ESD SMD boxes: {len(non_esd_smd)}')
for p in non_esd_smd[:10]:
    print(f\"{p['storage/name']} | id={p['storage/id']}\")
"
```

**Note on empty box detection:** If no stock has been added yet (`lots.py list` returns 0
results), then all storage locations are empty. In this case, simply pick the first N
boxes alphabetically for your new parts. Once stock is present, use `storage.py parts
--id <id>` to check individual boxes for occupancy.

## Workflow for Recommending Storage Locations

When asked to suggest storage for a component, follow this workflow:

1. **Identify component characteristics:**
   - Package type (SMD, through-hole, module, etc.)
   - Size/dimensions
   - ESD sensitivity
   - Quantity to store

2. **Fetch all storage and filter by type in Python** (see examples above)

3. **Check one location's description for size constraints:**
   - Read the `storage/description` field from any matching location
   - Extract compartment dimensions from the description
   - Verify component will fit

4. **Find available (empty) locations:**
   - If no stock exists yet, take first N locations alphabetically
   - If stock exists, check specific locations with `storage.py parts --id <id>`

5. **Recommend specific location(s):**
   - Prefer empty locations or those with related components
   - Consider grouping similar components together
   - Mention the storage type and why it's appropriate

## Best Practices

- **Fetch all, filter in Python** — load all 700 locations once, filter client-side
- **Read descriptions to verify size compatibility** — dimensions are in the description field
- **Leverage tag structure** — use `type_`, `esd_`, etc. prefixes for precise filtering
- **Consider component grouping** — suggest storing similar parts together
- **Check availability** — use `storage.py parts --id <id>` to see what's in a location
