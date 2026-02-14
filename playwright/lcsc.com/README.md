# LCSC Playwright Actions

Playwright-based automation scripts for LCSC.com electronics catalog.

**Created**: 2026-02-14
**Framework**: Claude Playwright Skill

## Overview

This directory contains parameterized Playwright scripts for automating interactions with LCSC.com. Each action is a standalone Node.js script that outputs structured JSON, making them easy to integrate into larger workflows.

## Available Actions

### ✅ search
**Status**: Working
**Purpose**: Search LCSC catalog by keywords with automatic pagination

```bash
cd search && ./run.sh --keywords="1206 resistor 10k" --maxResults=50
```

**Returns**: Array of products with LCSC codes, MPNs, manufacturers, prices, stock

### ✅ check-pricing
**Status**: Working
**Purpose**: Get detailed pricing tiers and specifications for an LCSC part

```bash
cd check-pricing && ./run.sh --lcscCode="C137394"
```

**Returns**: Complete product data with manufacturer, MPN, description, stock, all pricing tiers

### 🚧 add-to-cart
**Status**: Not yet implemented
**Purpose**: Add parts to LCSC shopping cart
**Requirements**: Persistent browser session, authentication

### 🚧 list-cart
**Status**: Not yet implemented
**Purpose**: List all items in shopping cart
**Requirements**: Persistent browser session, authentication

## Quick Start

### Prerequisites

```bash
# Install Playwright globally (if not already installed)
npm install -g playwright
playwright install chromium
```

### Usage Pattern

Each action has:
- `script.js` - Main Playwright script
- `run.sh` - Wrapper that sets NODE_PATH automatically
- `README.md` - Detailed documentation with examples

```bash
# Using wrapper (recommended)
./run.sh --param=value

# Direct invocation
NODE_PATH=$(npm root -g) node script.js --param=value
```

## Output Format

All scripts follow the Playwright skill convention:

```json
{
  "success": true|false,
  "data": { /* action-specific data */ },
  "metadata": {
    "url": "https://...",
    "timestamp": "2026-02-14T...",
    "duration": 1234,
    "browser": "chromium"
  },
  "error": { /* only on failure */
    "message": "...",
    "stack": "...",
    "screenshot": "path/to/error-screenshot.png"
  }
}
```

**Key features**:
- JSON to stdout (clean, parseable)
- Progress logs to stderr (human-readable)
- Exit code 0 on success, 1 on failure
- Error screenshots automatically saved

## Examples

### Search for parts

```bash
cd search
./run.sh --keywords="capacitor 10uF" --maxResults=20 2>/dev/null | jq '.data.products[0]'
```

### Check pricing for multiple parts

```bash
for code in C137394 C1525 C106886; do
  echo "Checking $code..."
  cd check-pricing && ./run.sh --lcscCode="$code" 2>/dev/null | \
    jq '.data | {lcscCode, mpn, stock, first_price: .pricing[0].unit_price}'
  cd ..
done
```

### Pipe search results to pricing check

```bash
cd search
./run.sh --keywords="1206 100k resistor" --maxResults=5 2>/dev/null | \
  jq -r '.data.products[].lcscCode' | \
  while read code; do
    cd ../check-pricing
    ./run.sh --lcscCode="$code" 2>/dev/null | jq -c '.data | {lcscCode, mpn, stock}'
    cd ../search
  done
```

## Comparison with Original lcsc_tool.py

### Original (MCP-based)
- Single monolithic Python script
- Uses FastMCP Client → Playwright MCP Server (Docker)
- All operations in one file (2000+ lines)
- Custom output format per operation
- Requires Docker container running

### New (Playwright Skill)
- Modular Node.js scripts per action
- Direct Playwright library (no Docker)
- Each action ~300-400 lines
- Standardized JSON output format
- No external dependencies beyond Node/Playwright

### Advantages of New Approach
✅ No Docker required
✅ Faster startup (~2-3s vs ~10-15s)
✅ Easier to debug (direct stack traces)
✅ Modular (use only what you need)
✅ Reusable (can migrate to skill templates)
✅ Standard output format

### When to Use Original
- Need Docker isolation
- Using MCP servers for other tasks
- Already have infrastructure set up

## Implementation Status

| Feature | Original | New (Skill) | Notes |
|---------|----------|-------------|-------|
| Search catalog | ✅ | ✅ | Working, tested |
| Check pricing | ✅ | ✅ | Working, tested |
| Add to cart | ✅ | 🚧 | Requires auth session |
| List cart | ✅ | 🚧 | Requires auth session |
| Create BOM | ✅ | ➖ | Doesn't need browser |
| Concurrency | ✅ | ➖ | Could add context pooling |
| MPN search | ✅ | ➖ | Could add to check-pricing |

## Migration Path

When ready to make these scripts globally available:

```bash
# From project root
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  scripts-temp/playwright/lcsc.com
```

This moves scripts to `~/.claude/templates/skills/playwright/actions/lcsc.com/` where they're accessible across all projects.

## Development Notes

- Uses regular `playwright` instead of `playwright-extra` (dependency issues)
- Browser args include `--disable-blink-features=AutomationControlled` for stealth
- All navigation uses `waitUntil: 'domcontentloaded'` (SPA-friendly)
- Waits 5-6 seconds after navigation for dynamic content
- Pagination implemented with button click + waitForTimeout
- Text extraction uses regex patterns from original implementation

## Troubleshooting

### "Cannot find module 'playwright'"

```bash
npm install -g playwright
playwright install chromium
```

### NODE_PATH not set

Use the `run.sh` wrapper scripts which handle this automatically.

### Browser launch fails

```bash
# Reinstall browser binaries
playwright install --force chromium

# On Linux, install system dependencies
playwright install-deps chromium
```

### Timeout errors

Increase timeout with `--timeout=20000` (milliseconds)

## Related Documentation

- [search/README.md](search/README.md) - Catalog search documentation
- [check-pricing/README.md](check-pricing/README.md) - Pricing check documentation
- Original: `/opt/src/mcp/electronics-assistant/scripts/lcsc_tool.py`

## Future Enhancements

Possible additions:
- [ ] Implement add-to-cart with session persistence
- [ ] Implement list-cart
- [ ] Add MPN search fallback to check-pricing
- [ ] Add browser context pooling for concurrency
- [ ] Create wrapper CLI tool similar to original
- [ ] Add result caching to avoid redundant requests
