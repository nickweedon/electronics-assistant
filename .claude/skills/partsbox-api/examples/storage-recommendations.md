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

## Querying Storage by Tags

**Find storage by type:**

```bash
# List all SMD-compatible storage
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
  --query '[?contains("storage/tags", '"'"'type_smd-box'"'"')]'

# Find ESD-safe storage
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
  --query '[?contains("storage/tags", '"'"'esd_yes'"'"')]'

# Find drawer-type storage
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
  --query '[?contains("storage/tags", '"'"'type_drawer-cabinet'"'"')]'
```

**Filter by multiple criteria:**

```bash
# Find ESD-safe SMD storage
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
  --query '[?contains("storage/tags", '"'"'type_smd-box'"'"') && contains("storage/tags", '"'"'esd_yes'"'"')]'
```

## Finding Storage Dimensions

Storage location dimensions and specifications are stored in the **`storage/description`** field.

**Get storage details:**

```bash
# Get full details for a specific storage location
bash .claude/skills/partsbox-api/scripts/run.sh storage.py get --id <storage-id>

# List storage with descriptions
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
  --query '[].{name: "storage/name", tags: "storage/tags", description: "storage/description"}'
```

**Important:** All storage locations of the same type (matching `type_` tag prefix) will have the same physical dimensions. You only need to check one location's description to understand the size constraints for all locations of that type.

## Workflow for Recommending Storage Locations

When asked to suggest storage for a component, follow this workflow:

1. **Identify component characteristics:**
   - Package type (SMD, through-hole, module, etc.)
   - Size/dimensions
   - ESD sensitivity
   - Quantity to store

2. **Query by tags to find candidate storage types:**

   ```bash
   # Example: For SMD components
   bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --limit 700 \
     --query '[?contains("storage/tags", '"'"'type_smd-box'"'"')]'
   ```

3. **Check one location's description for size constraints:**
   - Read the `storage/description` field from any matching location
   - Extract compartment dimensions from the description
   - Verify component will fit

4. **Find available (empty or low-fill) locations:**

   ```bash
   # Check stock levels in matching storage locations
   bash .claude/skills/partsbox-api/scripts/run.sh storage.py parts \
     --id <storage-id> --limit 10
   ```

5. **Recommend specific location(s):**
   - Prefer empty locations or those with related components
   - Consider grouping similar components together
   - Mention the storage type and why it's appropriate

## Example Recommendation Workflow

**User asks:** "Where should I store 100 pcs of 0805 ceramic capacitors?"

**Your workflow:**

1. Component is SMD → look for `type_smd-box`
2. Not ESD-sensitive → `esd_no` is fine (but `esd_yes` also works)
3. Query: Find SMD boxes
4. Check description: "18.3x16.7x10.2mm compartments" → 0805 fits easily
5. Check for empty SMD-Box locations (use `storage.py parts` to check fill status)
6. Recommend: "Store in SMD-Box-C5. This is an AideTek SMD organizer with 18.3x16.7mm compartments, ideal for 0805 SMD components."

**User asks:** "Where should I store a Raspberry Pi 4?"

**Your workflow:**

1. Component is a dev board (large, ~85x56mm)
2. Not suitable for SMD boxes or small drawers
3. Query: Find larger storage like `type_plano-stowaway`
4. Check description: "14x9.13\" footprint, configurable compartments" → RPi4 fits
5. Recommend specific Stowaway location

## Best Practices

- **Always query tags first** to narrow down storage types before checking individual locations
- **Read descriptions to verify size compatibility** - dimensions are in the description field
- **Leverage tag structure** - use `type_`, `esd_`, etc. prefixes for precise filtering
- **Consider component grouping** - suggest storing similar parts together (e.g., all 0805 resistors in adjacent compartments)
- **Check availability** - use `storage.py parts` to see what's already in a location
