# DigiKey API — Basic Usage Examples

## Search for a Component

```bash
# Keyword search for STM32 microcontrollers
bash .claude/skills/digikey-api/scripts/run.sh search.py keyword \
  --keywords "STM32F407VGT6" --limit 5

# Get detailed product info
bash .claude/skills/digikey-api/scripts/run.sh search.py product-details \
  --product-number "497-STM32F407VGT6-ND"

# Search with JMESPath to extract key fields
bash .claude/skills/digikey-api/scripts/run.sh search.py keyword \
  --keywords "100k resistor 0805" --limit 10 \
  --query 'Products[].{MPN: ManufacturerProductNumber, Price: UnitPrice, Stock: QuantityAvailable, Mfr: Manufacturer.Name}'
```

## Check Pricing

```bash
# Get pricing tiers for a product
bash .claude/skills/digikey-api/scripts/run.sh pricing.py product \
  --product-number "497-STM32F407VGT6-ND" --quantity 10

# Extract just the pricing tiers
bash .claude/skills/digikey-api/scripts/run.sh pricing.py product \
  --product-number "497-STM32F407VGT6-ND" --quantity 10 \
  --query '{Part: DigiKeyPartNumber, Tiers: StandardPricing[].{Qty: BreakQuantity, Unit: UnitPrice, Total: TotalPrice}}'

# DigiReel pricing
bash .claude/skills/digikey-api/scripts/run.sh pricing.py digi-reel \
  --product-number "497-STM32F407VGT6CT-ND" --quantity 100
```

## Manage Lists

```bash
# View all lists
bash .claude/skills/digikey-api/scripts/run.sh lists.py get-all

# Filter lists by name
bash .claude/skills/digikey-api/scripts/run.sh lists.py get-all \
  --query 'lists[?contains(ListName, `Project`)].{Id: Id, Name: ListName}'

# Create a new list
bash .claude/skills/digikey-api/scripts/run.sh lists.py create \
  --name "My Project BOM"

# Get list with parts
bash .claude/skills/digikey-api/scripts/run.sh lists.py get \
  --list-id "abc123" --include-parts
```

## Manage Parts in Lists

```bash
# Get all parts from a list
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py get-all \
  --list-id "abc123"

# Get parts with JMESPath filtering
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py get-all \
  --list-id "abc123" \
  --query '{Total: TotalParts, Parts: PartsList[].{PN: DigiKeyPartNumber, MPN: ManufacturerPartNumber, Mfr: Manufacturer, Qty: Quantities[0].QuantityRequested, Price: Quantities[0].PackOptions[0].CalculatedUnitPrice}}'

# Add parts to a list
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py add \
  --list-id "abc123" \
  --parts-json '[{"RequestedPartNumber": "296-8875-1-ND", "Quantities": [{"Quantity": 10}]}, {"RequestedPartNumber": "P5555-ND", "Quantities": [{"Quantity": 5}]}]'

# Add parts from a file
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py add \
  --list-id "abc123" --parts-json @temp/parts-to-add.json

# Update a part's notes
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py update \
  --list-id "abc123" --part-id "unique-id-here" \
  --part-json '{"Notes": "Changed to higher wattage variant"}'

# Delete a part
bash .claude/skills/digikey-api/scripts/run.sh list_parts.py delete \
  --list-id "abc123" --part-id "unique-id-here"
```

## OAuth Token Management

```bash
# Check if tokens are set up
bash .claude/skills/digikey-api/scripts/run.sh auth.py status

# Refresh expired user token
bash .claude/skills/digikey-api/scripts/run.sh auth.py refresh

# Initial setup: copy tokens from MCP server
cp /mnt/c/docker/digikey-tokens/.digikey_tokens \
  .claude/skills/digikey-api/scripts/.digikey_tokens

# Or set tokens manually
bash .claude/skills/digikey-api/scripts/run.sh auth.py set-tokens \
  --user-token "eyJ..." --refresh-token "abc..."
```

## Common JMESPath Patterns

```bash
# Filter in-stock products only
--query 'Products[?QuantityAvailable > `0`]'

# Get just part numbers and prices
--query 'Products[].{MPN: ManufacturerProductNumber, Price: UnitPrice}'

# Find products from specific manufacturer
--query 'Products[?Manufacturer.Name == `STMicroelectronics`]'

# Sort by price ascending
--query 'sort_by(Products, &UnitPrice)'

# Get first pricing tier
--query 'Products[].{MPN: ManufacturerProductNumber, MinPrice: ProductVariations[0].StandardPricing[0].UnitPrice}'

# Count results
--query '{Total: ProductsCount, InStock: length(Products[?QuantityAvailable > `0`])}'

# Filter list parts by category
--query 'PartsList[?contains(Category, `Resistor`)]'

# Get total extended price for list
--query '{Total: sum(PartsList[].Quantities[0].PackOptions[0].ExtendedPrice)}'
```
