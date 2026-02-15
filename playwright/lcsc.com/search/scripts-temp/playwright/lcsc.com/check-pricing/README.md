# check-pricing - lcsc.com

**Action**: check-pricing
**Site**: lcsc.com
**Template**: base-script
**Created**: 2026-02-14T18:23:30Z

## Description

Playwright automation for lcsc.com.

## Parameters

Add your parameters here based on the template and your needs.

## Usage

```bash
node script.js --param1=value1 --param2=value2
```

### Additional Options

- `--headless=false` - Run browser in visible mode
- `--timeout=10000` - Set timeout in milliseconds (default: 5000)
- `--screenshot=true` - Take screenshots

## Output Format

Scripts output JSON to stdout:

```json
{
  "success": true,
  "data": {},
  "metadata": {
    "url": "...",
    "timestamp": "...",
    "duration": 1234
  }
}
```

## Notes

- Customize the script.js selectors for your specific use case
- Run with `--headless=false` first to debug
- Screenshots are saved to ./screenshots/ on error

## Migration

To migrate to skill templates:

```bash
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  scripts-temp/playwright/lcsc.com
```
