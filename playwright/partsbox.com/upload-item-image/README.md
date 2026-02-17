# Upload Item Image - PartsBox

Uploads an image file to a PartsBox part with smart login detection. Automatically switches to headed mode when login is needed, waits for manual login, then continues.

## Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `--part-id` | Yes | PartsBox part ID (26-char compact UUID) | - |
| `--image-path` | Yes | Path to image file to upload | - |
| `--debug` | No | Run in headed mode (visible browser) | `false` |
| `--timeout` | No | Timeout in milliseconds | `30000` |

## Usage

### Basic Usage (Headless)

```bash
cd playwright/partsbox.com/upload-item-image

node script.js \
  --part-id=7wxwfbecvjg3xa86bf1tsmy7mj \
  --image-path=/tmp/adapter-board.jpg
```

### Debug Mode (Visible Browser)

```bash
cd playwright/partsbox.com/upload-item-image

node script.js \
  --part-id=7wxwfbecvjg3xa86bf1tsmy7mj \
  --image-path=/tmp/adapter-board.jpg \
  --debug
```

## How It Works

1. **Opens part page** - Navigates to `https://partsbox.com/melkor/parts/{part-id}`
2. **Login detection** - Checks if login is required
3. **Auto relaunch** - If headless and login needed, relaunches in headed mode
4. **Manual login** - Waits up to 2 minutes for you to complete login
5. **Auto continue** - Detects when login completes and continues automatically
6. **Upload image** - Finds file input and uploads the image
7. **Save changes** - Clicks save button if present

## Login Flow

**When login is detected in headless mode:**

1. Script automatically relaunches browser in **headed mode** (visible)
2. Opens PartsBox part page
3. You'll see console messages:

   ```
   🔐 [LOGIN] Login required detected
   ⏳ [WAIT] Waiting for you to complete login...
   🖱️  [WAIT] Please login in the browser window
   ⚠️  [WAIT] Do NOT close the browser - watching for login completion
   ```

4. Complete login in the browser window
5. Script **automatically detects** login completion
6. Script continues and uploads image

**When login is detected in debug mode:**

1. Browser is already visible
2. Waits for manual login
3. Continues automatically after login

**Max wait time:** 2 minutes (120 seconds)

## Output

### Success

```json
{
  "success": true,
  "data": {
    "partId": "7wxwfbecvjg3xa86bf1tsmy7mj",
    "partUrl": "https://partsbox.com/melkor/parts/7wxwfbecvjg3xa86bf1tsmy7mj",
    "imagePath": "/tmp/adapter-board.jpg",
    "uploaded": true
  },
  "metadata": {
    "url": "https://partsbox.com/melkor/parts/7wxwfbecvjg3xa86bf1tsmy7mj",
    "timestamp": "2026-02-17T10:30:00.000Z",
    "duration": 15000,
    "browser": "chromium",
    "screenshots": []
  }
}
```

### Error

```json
{
  "success": false,
  "data": null,
  "metadata": {
    "url": "https://partsbox.com/melkor/parts/7wxwfbecvjg3xa86bf1tsmy7mj",
    "timestamp": "2026-02-17T10:30:00.000Z",
    "duration": 5000,
    "browser": "chromium"
  },
  "error": {
    "message": "Could not find image upload control on PartsBox part page",
    "stack": "Error: ...",
    "screenshot": "./screenshots/error-1234567890.png"
  }
}
```

## Example Integration

Combine with the AliExpress download script:

```bash
#!/bin/bash

PART_ID="7wxwfbecvjg3xa86bf1tsmy7mj"
ALIEXPRESS_URL="https://www.aliexpress.com/item/3256808077896845.html"
TEMP_IMAGE="/tmp/aliexpress-${PART_ID}.jpg"

# Step 1: Download image from AliExpress
echo "📦 Downloading image from AliExpress..."
cd scripts-temp/playwright/aliexpress.com/download-item-image
node script.js \
  --product-url="$ALIEXPRESS_URL" \
  --output="$TEMP_IMAGE"

# Step 2: Upload to PartsBox
echo "📤 Uploading to PartsBox..."
cd ../../../partsbox.com/upload-item-image
node script.js \
  --part-id="$PART_ID" \
  --image-path="$TEMP_IMAGE"

echo "✅ Done!"
```

## Notes

- Uses stealth mode to avoid detection
- Automatically handles login by switching to headed mode
- Monitors browser every second during login wait
- Creates `./screenshots/` directory automatically
- Error screenshots saved with timestamp
- Login session is persisted via cookies at `~/.cache/playwright-profiles/partsbox/cookies.json`
- Session survives container rebuilds (stored on persistent Docker volume)

## Troubleshooting

### Upload control not found

PartsBox UI may have changed. Run with `--debug` and check the error screenshot to see the page structure.

### Login timeout

If login takes longer than 2 minutes, the script will timeout. Complete login faster or adjust `maxAttempts` in the script.

### Image file not found

Ensure the image path is correct and the file exists before running the script.
