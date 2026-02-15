# JMESPath Query Reference for PartsBox API

## Critical Syntax Rules

### Field Names Use "/" Separator

All PartsBox fields use "/" in their names. In JMESPath, you **MUST** use double
quotes to reference these fields:

```text
CORRECT: "part/name"         (double quotes = field reference)
WRONG:   `part/name`         (backticks = literal string "part/name")
```

### Use nvl() for Safe Filtering

Many fields can be null. Use `nvl()` to provide defaults and prevent errors:

```text
CORRECT: [?contains(nvl("part/name", ''), 'resistor')]
WRONG:   [?contains("part/name", 'resistor')]    -- fails if null
```

### Literal Syntax

```text
Empty string:  ''          (single quotes)
Empty array:   `[]`        (backticks required!)
Zero:          `0`         (backticks)
False:         `false`     (backticks)
```

## Parts Queries

```bash
# Search by name
--query '[?contains(nvl("part/name", '"'"''"'"'), '"'"'resistor'"'"')]'

# Filter by manufacturer
--query '[?nvl("part/manufacturer", '"'"''"'"') == '"'"'Yageo'"'"']'

# Parts with SMD tag
--query '[?contains(nvl("part/tags", `[]`), '"'"'SMD'"'"')]'

# Sort by name
--query 'sort_by(@, &"part/name")'

# Get specific fields only (projection)
--query '[].{id: "part/id", name: "part/name", mpn: "part/mpn"}'

# Parts with low stock warning set
--query '[?"part/low-stock" != null]'

# Count parts by type (meta-parts)
--query '[?"part/type" == '"'"'meta'"'"']'
```

## Storage Queries

```bash
# Find storage by name
--query '[?contains(nvl("storage/name", '"'"''"'"'), '"'"'Drawer'"'"')]'

# Non-archived with tags
--query '[?"storage/archived" == `false`]'

# Storage locations that are full
--query '[?"storage/full?" == `true`]'
```

## Stock Source Queries

```bash
# Sources with positive quantity
--query '[?"source/quantity" > `0`]'

# Sort by quantity descending (negate trick)
--query 'reverse(sort_by(@, &"source/quantity"))'

# Filter by status (e.g., on-hand stock only)
--query '[?"source/status" == null]'
```

## Project Queries

```bash
# Active projects only
--query '[?"project/archived" == `false`]'

# Sort by last update
--query 'sort_by(@, &"project/updated")'

# Projects with entries
--query '[?"project/entry-count" > `0`]'
```

## BOM Entry Queries

```bash
# Entries with quantity > 10
--query '[?"entry/quantity" > `10`]'

# Sort by BOM order
--query 'sort_by(@, &"entry/order")'

# Entries with specific designator prefix
--query '[?contains(nvl(str("entry/designators"), '"'"''"'"'), '"'"'R'"'"')]'
```

## Order Queries

```bash
# Orders from a specific vendor
--query '[?nvl("order/vendor-name", '"'"''"'"') == '"'"'DigiKey'"'"']'

# Recent orders (sort by date descending)
--query 'reverse(sort_by(@, &"order/created"))'
```

## Advanced Patterns

### Numeric Extraction with regex_replace + int

```bash
# Extract numeric value from description like "100 ohm"
--query '[?int(regex_replace('"'"' ohm$'"'"', '"'"''"'"', nvl("part/description", '"'"''"'"'))) >= `100`]'
```

### Chaining nvl with int for Safe Numeric Comparison

```bash
# Parts with low stock threshold > 10
--query '[?nvl(int(nvl("part/low-stock", `{}`).report), `0`) > `10`]'
```

### Projection with Computed Fields

```bash
# Get name and stock info together
--query '[].{name: "part/name", type: "part/type", manufacturer: "part/manufacturer"}'
```

## Shell Escaping Tips

JMESPath queries with single quotes inside bash commands need careful escaping.
The pattern `'"'"'` breaks out of bash single quotes and inserts a literal `'`:

```bash
# This query: [?contains(nvl("part/name", ''), 'resistor')]
# Becomes in bash:
--query '[?contains(nvl("part/name", '"'"''"'"'), '"'"'resistor'"'"')]'
```

Alternatively, use double-quoted strings with escaped inner quotes:

```bash
--query "[?contains(nvl(\"part/name\", ''), 'resistor')]"
```
