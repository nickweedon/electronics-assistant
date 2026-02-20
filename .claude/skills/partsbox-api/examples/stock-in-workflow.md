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

**Tag naming rules:**

- Use only alphanumeric characters, hyphens, and underscores
- **`%` and other special characters are rejected by the API with a silent 400 error**
- For tolerance values use `1pct` not `1%`, for ratios use `50v` not `50V`, etc.

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

## Thumbnail Image Column

Each part in the Inventory Summary table should have a thumbnail image as the first column. Images are downloaded from PartsBox using the `part/img-id` field returned by `parts.py get`.

**Workflow:**

1. For each part, fetch it to get its image ID:

   ```bash
   bash .claude/skills/partsbox-api/scripts/run.sh parts.py get --id "<part-id>" \
     | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; print(d.get('part/img-id','NONE'))"
   ```

2. Download all images to `data/stock-in/images/` (run in parallel for speed):

   ```bash
   mkdir -p data/stock-in/images
   bash .claude/skills/partsbox-api/scripts/run.sh files.py download \
     --file-id "<img-id>" \
     -o data/stock-in/images/<kebab-part-name>.jpg
   ```

3. Reference images in the table using `<img>` tags with:
   - `height="48"` — roughly double a typical 24px line height, keeps rows compact
   - `alt="..."` — required by markdownlint (MD045); use a short descriptive name
   - `src` relative to the markdown file (i.e. `images/<filename>.jpg`)

**Example table row:**

```markdown
| <img src="images/1027-vibration-motor.jpg" alt="1027 Mini Vibration Motor" height="48"> | [1027 Mini Vibration Motor](#1027-mini-vibration-motor) | Stowaway3-B1 | 6 | ... |
```

**Image file naming:** Use kebab-case derived from the part name, e.g. `sot23-sip3-adapter.jpg`, `1027-vibration-motor.jpg`.

**Note:** `part/img-id` is only present if an image was previously uploaded to PartsBox. If missing, omit the image cell or use an empty cell for that row.

## Page Break After Summary Table

Add a `<div style="break-after: page;"></div>` immediately after the summary table rows and before the **Total** lines. This ensures the summary table prints on its own page when the markdown is exported to PDF:

```markdown
| <img ...> | [Part Name](#anchor) | ... | ☐ |

<div style="break-after: page;"></div>

**Total:** 84 pieces across 7 part types
**Total Cost:** $15.09
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
      "storageId": "abc123...",
      "quantity": 5,
      "orderNumber": "8209410078791142",
      "price": "1.91",
      "description": "Full description...",
      "specifications": ["Spec 1", "Spec 2"],
      "partsboxId": "abc123...",
      "imageFilename": "part-name.jpg",
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
# Write data to JSON file first (recommended for complex data), then render
echo '{"orderSource": "...", ...}' > /tmp/stock-in-data.json
node /home/vscode/claude-monorepo/claude/lib/render-skill.js \
  --template stock-in.md.hbs \
  --template-dir /workspace/.claude/skills/partsbox-api/templates \
  --data-file /tmp/stock-in-data.json \
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
3. **Download thumbnail images** - Fetch `part/img-id` for each part (via `parts.py get`) and download to `data/stock-in/images/` (see [Thumbnail Image Column](#thumbnail-image-column) above)
4. **Determine storage locations** - Use storage guidelines (see `storage-guidelines.md`) to select appropriate locations
5. **Generate documentation** - Use the template to create `data/stock-in/*.md` file, including `imageFilename` in each part's data
6. **Physically store components** - Place items in designated storage locations
7. **Add stock** - Use `stock.py add` to add quantities to PartsBox (AFTER physical storage)

**Key principle:** Create parts first, document storage plan, physically store, THEN add stock entries.
