# login - lcsc.com

**Action**: login
**Site**: lcsc.com (lcsc.com)
**Template**: base-script
**Created**: 2026-02-19T04:26:16.915Z

## Description

Playwright automation for lcsc.com

## Parameters


## Usage

### Basic Usage

```bash
node script.js 
```

### With All Parameters

```bash
node script.js \

```

### Additional Options

- `--headless=false` - Run browser in non-headless mode (visible)
- `--timeout=10000` - Set custom timeout in milliseconds (default: 5000)
- `--screenshot=true` - Take screenshot during execution
- `--screenshotBefore=true` - Take screenshot before form submission
- `--screenshotAfter=true` - Take screenshot after form submission

## Output Format

The script outputs JSON to stdout with the following structure:

```json
{
  "success": true,
  "data": {
    // Action-specific data
  },
  "metadata": {
    "url": "final-url-after-execution",
    "timestamp": "ISO-8601-timestamp",
    "duration": 1234,
    "browser": "chromium",
    "screenshots": ["path/to/screenshot.png"]
  }
}
```

On error:

```json
{
  "success": false,
  "data": null,
  "metadata": {
    "url": "url-where-error-occurred",
    "timestamp": "ISO-8601-timestamp",
    "duration": 1234,
    "browser": "chromium"
  },
  "error": {
    "message": "error-message",
    "stack": "full-stack-trace",
    "screenshot": "path/to/error-screenshot.png"
  }
}
```

## Examples


## Notes

- This script uses Playwright with stealth plugins to avoid detection
- Screenshots are automatically saved on error to `./screenshots/`
- All selectors are based on the site's current structure and may need updating if the site changes
- Consider running with `--headless=false` first to debug selector issues

## Maintenance

- **Last Updated**: 2026-02-19T04:26:16.915Z
- **Site Version**: Check if selectors still work with current site version
- **Dependencies**: playwright, playwright-extra, puppeteer-extra-plugin-stealth

## Migration

To migrate this script to the skill's permanent template directory:

```bash
bash ~/.claude/skills/playwright/scripts/migrate-to-templates.sh \
  scripts-temp/playwright/lcsc.com
```

This will copy all actions for lcsc.com to `~/.claude/templates/skills/playwright/actions/lcsc.com/` for reuse across sessions.
