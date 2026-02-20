# PartsBox API Scripts - Basic Usage Examples

## Parts

```bash
# List all parts
bash .claude/skills/partsbox-api/scripts/run.sh parts.py list

# Get a specific part
bash .claude/skills/partsbox-api/scripts/run.sh parts.py get --id "01HXYZ..."

# Check stock for a part
bash .claude/skills/partsbox-api/scripts/run.sh parts.py stock --id "01HXYZ..."

# Create a new part
bash .claude/skills/partsbox-api/scripts/run.sh parts.py create \
  --name "10k Resistor 0805" \
  --type local \
  --manufacturer "Yageo" \
  --mpn "RC0805FR-0710KL" \
  --footprint "0805" \
  --tags "resistor,SMD,0805"

# Update part description
bash .claude/skills/partsbox-api/scripts/run.sh parts.py update \
  --id "01HXYZ..." \
  --description "10k ohm 1% 0805 chip resistor"

# Delete a part (requires user confirmation)
bash .claude/skills/partsbox-api/scripts/run.sh parts.py delete --id "01HXYZ..."
```

## Stock Management

```bash
# Add 100 resistors to storage
bash .claude/skills/partsbox-api/scripts/run.sh stock.py add \
  --part-id "01HXYZ..." \
  --storage-id "01HABC..." \
  --quantity 100 \
  --price 0.01 \
  --currency usd

# Remove 10 from stock
bash .claude/skills/partsbox-api/scripts/run.sh stock.py remove \
  --part-id "01HXYZ..." \
  --storage-id "01HABC..." \
  --quantity 10

# Move stock between locations
bash .claude/skills/partsbox-api/scripts/run.sh stock.py move \
  --part-id "01HXYZ..." \
  --source-storage-id "01HABC..." \
  --target-storage-id "01HDEF..." \
  --quantity 50
```

## Storage Locations

```bash
# List all active storage locations
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list

# List including archived
bash .claude/skills/partsbox-api/scripts/run.sh storage.py list --include-archived

# Create a new storage location
bash .claude/skills/partsbox-api/scripts/run.sh storage.py create \
  --name "SMD-Box-A1"

# Create with description and tags
bash .claude/skills/partsbox-api/scripts/run.sh storage.py create \
  --name "Drawer-B-Capacitors" \
  --description "Ceramic capacitors 0805/0603" \
  --tags "SMD,capacitors"

# Get details for a specific location
bash .claude/skills/partsbox-api/scripts/run.sh storage.py get --id "01HABC..."

# See what's in a specific location
bash .claude/skills/partsbox-api/scripts/run.sh storage.py parts --id "01HABC..."

# Rename a location
bash .claude/skills/partsbox-api/scripts/run.sh storage.py rename \
  --id "01HABC..." \
  --name "Drawer A - SMD Resistors"
```

## Projects & BOMs

```bash
# List active projects
bash .claude/skills/partsbox-api/scripts/run.sh projects.py list

# Create a project
bash .claude/skills/partsbox-api/scripts/run.sh projects.py create \
  --name "Sensor Board v2" \
  --description "Temperature/humidity sensor with ESP32"

# Get BOM entries
bash .claude/skills/partsbox-api/scripts/run.sh project_entries.py get \
  --project-id "01HPRJ..."

# Add BOM entries
bash .claude/skills/partsbox-api/scripts/run.sh project_entries.py add \
  --project-id "01HPRJ..." \
  --entries '[{"entry/part-id":"01HXYZ...","entry/quantity":4,"entry/designators":["R1","R2","R3","R4"]}]'
```

## Orders

```bash
# List all orders
bash .claude/skills/partsbox-api/scripts/run.sh orders.py list

# Create a purchase order
bash .claude/skills/partsbox-api/scripts/run.sh orders.py create \
  --vendor "DigiKey" \
  --order-number "DK-2024-001"

# Add items to an order
bash .claude/skills/partsbox-api/scripts/run.sh order_entries.py add \
  --order-id "01HORD..." \
  --entries '[{"entry/part-id":"01HXYZ...","entry/quantity":100,"entry/price":0.01}]'

# Receive order into storage
bash .claude/skills/partsbox-api/scripts/run.sh order_receive.py \
  --order-id "01HORD..." \
  --storage-id "01HABC..." \
  --comments "Received 2024-01-15"
```

## Files

```bash
# Get download URL for a part image
bash .claude/skills/partsbox-api/scripts/run.sh files.py url --file-id "img_abc123"

# Download a datasheet
bash .claude/skills/partsbox-api/scripts/run.sh files.py download \
  --file-id "ds_abc123" \
  -o ./datasheets/resistor-10k.pdf
```
