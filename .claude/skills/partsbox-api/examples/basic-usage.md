# PartsBox API Scripts - Basic Usage Examples

## Parts

```bash
# List all parts (first 50)
python3 .claude/skills/partsbox-api/scripts/parts.py list

# List with limit
python3 .claude/skills/partsbox-api/scripts/parts.py list --limit 10

# Get a specific part
python3 .claude/skills/partsbox-api/scripts/parts.py get --id "01HXYZ..."

# Check stock for a part
python3 .claude/skills/partsbox-api/scripts/parts.py stock --id "01HXYZ..."

# Create a new part
python3 .claude/skills/partsbox-api/scripts/parts.py create \
  --name "10k Resistor 0805" \
  --type local \
  --manufacturer "Yageo" \
  --mpn "RC0805FR-0710KL" \
  --footprint "0805" \
  --tags "resistor,SMD,0805"

# Update part description
python3 .claude/skills/partsbox-api/scripts/parts.py update \
  --id "01HXYZ..." \
  --description "10k ohm 1% 0805 chip resistor"

# Delete a part (requires user confirmation)
python3 .claude/skills/partsbox-api/scripts/parts.py delete --id "01HXYZ..."
```

## Stock Management

```bash
# Add 100 resistors to storage
python3 .claude/skills/partsbox-api/scripts/stock.py add \
  --part-id "01HXYZ..." \
  --storage-id "01HABC..." \
  --quantity 100 \
  --price 0.01 \
  --currency usd

# Remove 10 from stock
python3 .claude/skills/partsbox-api/scripts/stock.py remove \
  --part-id "01HXYZ..." \
  --storage-id "01HABC..." \
  --quantity 10 \
  --comments "Used in prototype build"

# Move stock between locations
python3 .claude/skills/partsbox-api/scripts/stock.py move \
  --part-id "01HXYZ..." \
  --source-storage-id "01HABC..." \
  --target-storage-id "01HDEF..." \
  --quantity 50
```

## Storage Locations

```bash
# List active storage locations
python3 .claude/skills/partsbox-api/scripts/storage.py list

# List including archived
python3 .claude/skills/partsbox-api/scripts/storage.py list --include-archived

# See what's in a specific location
python3 .claude/skills/partsbox-api/scripts/storage.py parts --id "01HABC..."

# Rename a location
python3 .claude/skills/partsbox-api/scripts/storage.py rename \
  --id "01HABC..." \
  --name "Drawer A - SMD Resistors"
```

## Projects & BOMs

```bash
# List active projects
python3 .claude/skills/partsbox-api/scripts/projects.py list

# Create a project
python3 .claude/skills/partsbox-api/scripts/projects.py create \
  --name "Sensor Board v2" \
  --description "Temperature/humidity sensor with ESP32"

# Get BOM entries
python3 .claude/skills/partsbox-api/scripts/project_entries.py get \
  --project-id "01HPRJ..."

# Add BOM entries
python3 .claude/skills/partsbox-api/scripts/project_entries.py add \
  --project-id "01HPRJ..." \
  --entries '[{"entry/part-id":"01HXYZ...","entry/quantity":4,"entry/designators":["R1","R2","R3","R4"]}]'
```

## Orders

```bash
# List all orders
python3 .claude/skills/partsbox-api/scripts/orders.py list

# Create a purchase order
python3 .claude/skills/partsbox-api/scripts/orders.py create \
  --vendor "DigiKey" \
  --order-number "DK-2024-001"

# Add items to an order
python3 .claude/skills/partsbox-api/scripts/order_entries.py add \
  --order-id "01HORD..." \
  --entries '[{"entry/part-id":"01HXYZ...","entry/quantity":100,"entry/price":0.01}]'

# Receive order into storage
python3 .claude/skills/partsbox-api/scripts/order_receive.py \
  --order-id "01HORD..." \
  --storage-id "01HABC..." \
  --comments "Received 2024-01-15"
```

## Files

```bash
# Get download URL for a part image
python3 .claude/skills/partsbox-api/scripts/files.py url --file-id "img_abc123"

# Download a datasheet
python3 .claude/skills/partsbox-api/scripts/files.py download \
  --file-id "ds_abc123" \
  -o ./datasheets/resistor-10k.pdf
```
