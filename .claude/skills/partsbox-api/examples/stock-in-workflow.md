# Stock-In Workflow

When receiving new components (from suppliers like AliExpress, Digikey, Mouser, etc.), follow this workflow to catalog parts and create documentation.

## Overview

The stock-in workflow has two phases:

1. **Catalog Phase** - Create part entries in PartsBox with detailed notes (NO stock added yet)
2. **Documentation Phase** - Generate a stock-in markdown file for tracking physical storage

**IMPORTANT:** Stock is added LATER when physically placing items in storage. The catalog phase only creates part definitions.

## Part Creation Format

When creating parts during stock-in, use the `--notes` parameter to include comprehensive purchase information:

```bash
bash .claude/skills/partsbox-api/scripts/run.sh parts.py create \
  --name "Part Name" \
  --type "local" \
  --description "Short technical description (main specs)" \
  --tags "tag1,tag2,tag3" \
  --notes "Fuller description with context and use cases.

Specifications:
- Key spec 1
- Key spec 2
- Key spec 3

Purchase source: [Supplier Name]
Order #: [Order Number]
Received: YYYY-MM-DD
Quantity: X pcs
Price: $X.XX
[Supplier] Link: https://..."
```

**Notes field structure:**

1. **Fuller technical description** - Expand on the short description, add context and applications
2. **Specifications section** - Detailed specs (voltage, current, dimensions, etc.)
3. **Purchase metadata** - Source, order number, received date, quantity, price
4. **Supplier link** - Direct product URL for reordering

**Example:**

```bash
bash .claude/skills/partsbox-api/scripts/run.sh parts.py create \
  --name "1027 Mini Vibration Motor" \
  --type "local" \
  --description "DC 3V 12000rpm flat coin button-type micro vibrating motor" \
  --tags "motor,vibration,dc-motor,actuator,haptic" \
  --notes "Flat coin button-type mini vibration motor for mobile phone vibration, tactile feedback, and haptic applications.

Specifications:
- Voltage: DC 3V
- Speed: 12000rpm
- Type: Coin/pancake style (1027 size)
- Dimensions: ~10mm diameter x 2.7mm thick
- Application: Mobile phones, pagers, haptic feedback devices

Purchase source: AliExpress
Order #: 8209410078811142
Received: 2026-02-17
Quantity: 6 pcs
Price: \$3.34
AliExpress Link: https://www.aliexpress.com/item/3256810104837770.html"
```

## Stock-In Documentation Template

Use the Handlebars template at `.claude/skills/partsbox-api/templates/stock-in.md.hbs` to generate markdown documentation files.

**Template location:** `.claude/skills/partsbox-api/templates/stock-in.md.hbs`

**Output location:** `data/stock-in/<descriptive-filename>.md`

**Template data structure:**

```json
{
  "orderSource": "AliExpress",
  "orderDescription": "Adapters and Motors",
  "receivedDate": "2026-02-17",
  "orderNumbers": "#8209410078811142, #8209410078791142, ...",
  "parts": [
    {
      "name": "Part Name",
      "storageLocation": "StorageName",
      "quantity": 5,
      "orderNumber": "8209410078791142",
      "price": "1.91",
      "description": "Full description...",
      "specifications": ["Spec 1", "Spec 2"],
      "partsboxId": "abc123...",
      "sourceType": "AliExpress",
      "sourceLink": "https://..."
    }
  ],
  "totalPieces": 84,
  "totalPartTypes": 7,
  "totalCost": "15.09",
  "storageNotes": [
    {
      "location": "CmpntCab1-Drawer",
      "description": "Component Cabinet #1, large drawer (holds all 5 adapter types)"
    }
  ]
}
```

**Render the template:**

```bash
# Using the global template renderer
node /home/vscode/claude-monorepo/claude/lib/template-renderer.js \
  --template .claude/skills/partsbox-api/templates/stock-in.md.hbs \
  --data-json '{"orderSource": "...", ...}' \
  --output data/stock-in/supplier-YYYY-MM-DD-description.md

# Alternative: Write data to JSON file first for complex data
echo '{"orderSource": "...", ...}' > /tmp/stock-in-data.json
node /home/vscode/claude-monorepo/claude/lib/template-renderer.js \
  --template .claude/skills/partsbox-api/templates/stock-in.md.hbs \
  --data /tmp/stock-in-data.json \
  --output data/stock-in/supplier-YYYY-MM-DD-description.md
```

**File naming convention:** `data/stock-in/<supplier>-<YYYY-MM-DD>-<description>.md`

Examples:

- `data/stock-in/aliexpress-2026-02-17-adapters-motors.md`
- `data/stock-in/digikey-2026-02-20-smd-resistors.md`
- `data/stock-in/mouser-2026-02-22-voltage-regulators.md`

## Stock-In Workflow Steps

1. **Create part entries** - Use `parts.py create` with detailed `--notes` for each component
2. **Save part IDs** - Collect the returned `part/id` values from each create command
3. **Determine storage locations** - Use storage guidelines (see `storage-guidelines.md`) to select appropriate locations
4. **Generate documentation** - Use the template to create `data/stock-in/*.md` file with part IDs and storage assignments
5. **Physically store components** - Place items in designated storage locations
6. **Add stock** - Use `stock.py add` to add quantities to PartsBox (AFTER physical storage)

**Key principle:** Create parts first, document storage plan, physically store, THEN add stock entries.
