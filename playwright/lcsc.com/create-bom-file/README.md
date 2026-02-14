# LCSC Create BOM File

Generate LCSC BOM CSV files from part codes and quantities.

**Action**: create-bom-file
**Site**: lcsc.com
**Created**: 2026-02-14

## Description

Creates LCSC-compatible BOM (Bill of Materials) CSV files from part numbers and quantities. Supports both LCSC part codes (e.g., "C137394") and manufacturer part numbers (MPNs). The generated CSV can be uploaded directly to LCSC for batch ordering.

**Note**: This script does NOT use browser automation - it's a simple CSV generator.

## Parameters

### Required

- `--output`: Output CSV file path (e.g., "bom.csv")

AND one of:
- `--input`: JSON file containing parts array
- `--parts`: Comma-separated list of PART:QTY (e.g., "C137394:100,C1525:50")

### Optional

- `--useLcscCodes`: If true, treat input as LCSC codes; if false, treat as MPNs (default: false)
  *Aliases:* `--lcscCodes`

## Usage

### From Command Line (Inline Parts)

```bash
# Using LCSC codes
./run.sh --parts="C137394:100,C1525:50,C106886:25" --output=bom.csv --useLcscCodes=true

# Using MPNs
./run.sh --parts="RC1206FR-070RL:100,RC1206FR-0710KL:50" --output=bom.csv
```

### From JSON File

Create an input file `parts.json`:

```json
[
  {
    "lcscCode": "C137394",
    "quantity": 100
  },
  {
    "lcscCode": "C1525",
    "quantity": 50
  }
]
```

Then run:

```bash
./run.sh --input=parts.json --output=bom.csv --useLcscCodes=true
```

Alternative JSON format (flexible field names):

```json
[
  {
    "partNumber": "RC1206FR-070RL",
    "qty": 100
  },
  {
    "mpn": "RC1206FR-0710KL",
    "quantity": 50
  }
]
```

```bash
./run.sh --input=parts.json --output=bom.csv
```

## Output Format

### Script Output (JSON to stdout)

```json
{
  "success": true,
  "data": {
    "outputFile": "/full/path/to/bom.csv",
    "partCount": 3,
    "useLcscCodes": true,
    "parts": [
      {
        "partNumber": "C137394",
        "quantity": 100
      }
    ]
  },
  "metadata": {
    "timestamp": "2026-02-14T19:30:00.000Z",
    "duration": 2
  }
}
```

### Generated CSV File

The CSV follows LCSC's BOM template format:

```csv
Quantity,Manufacture Part Number,Manufacturer(optional),Description(optional),LCSC Part Number(optional),Package(optional),Customer Part Number(optional),,
100,,,,C137394,,,,
50,,,,C1525,,,,
```

**Column Mapping:**
- When `useLcscCodes=true`: Part numbers go in "LCSC Part Number(optional)" column
- When `useLcscCodes=false`: Part numbers go in "Manufacture Part Number" column

## JSON Input Field Names

The script accepts flexible field names in JSON input:

| For Part Number | For Quantity |
|-----------------|--------------|
| `partNumber` | `quantity` |
| `lcscCode` | `qty` |
| `code` | |
| `mpn` | |

## Features

- **No Browser Required**: Pure Node.js script, no Playwright needed
- **Flexible Input**: JSON file or command-line arguments
- **Dual Mode**: Supports both LCSC codes and MPNs
- **Auto-Directory Creation**: Creates output directory if needed
- **Standard Format**: Matches LCSC BOM template exactly
- **Fast**: Generates CSV in milliseconds

## Use Cases

### 1. Quick BOM from LCSC Codes

```bash
./run.sh --parts="C137394:100,C1525:200,C106886:50" \
  --output=data/boms/kit_2026.csv \
  --useLcscCodes=true
```

### 2. BOM from Search Results

After searching with the search action, pipe results:

```bash
# Search returns JSON with lcscCode fields
cd ../search
./run.sh --keywords="1206 resistor 10k" --maxResults=5 2>/dev/null | \
  jq '[.data.products[] | {lcscCode, quantity: 100}]' > /tmp/parts.json

cd ../create-bom-file
./run.sh --input=/tmp/parts.json --output=resistors_bom.csv --useLcscCodes=true
```

### 3. BOM from MPNs

```bash
./run.sh --parts="RC1206FR-070RL:1000,RC1206FR-0710KL:500" \
  --output=yageo_resistors.csv
```

## Error Handling

- Validates required parameters (output + input/parts)
- Checks JSON parsing errors
- Verifies non-empty parts list
- Creates output directory if missing
- Returns exit code 1 on failure with error JSON

## Notes

- Default quantity is 100 if not specified (e.g., "C137394" → quantity=100)
- Quantities are parsed from PART:QTY format (e.g., "C137394:250")
- Empty optional fields are left blank in the CSV
- CSV has 9 columns (last 2 are always empty per LCSC template)

## Related Actions

- `search`: Find parts to add to BOM
- `check-pricing`: Verify pricing before creating BOM

## Migration

To migrate to skill templates:

```bash
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  scripts-temp/playwright/lcsc.com
```
