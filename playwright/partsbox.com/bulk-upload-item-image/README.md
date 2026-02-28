# Bulk Upload Item Images - PartsBox

Uploads images to multiple PartsBox parts concurrently using a bounded worker pool.
Login is handled interactively once before the pool starts; all workers then run
headless using the saved session cookies.

## Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `--items-file` | Yes | Path to JSON file with upload list | - |
| `--max-concurrency` | No | Maximum simultaneous browser instances | `10` |
| `--timeout` | No | Per-browser timeout in milliseconds | `30000` |
| `--debug` | No | Run workers in headed mode (visible browser) | `false` |

## Items File Format

A JSON array of objects with `partId` and `imagePath` fields:

```json
[
  {
    "partId": "7wxwfbecvjg3xa86bf1tsmy7mj",
    "imagePath": "/tmp/images/part1.jpg"
  },
  {
    "partId": "8abcdefghijklmnopqrstuvwxy",
    "imagePath": "/tmp/images/part2.jpg"
  }
]
```

## Usage

### Basic Usage

```bash
cd playwright/partsbox.com/bulk-upload-item-image

node script.js \
  --items-file=/tmp/upload-list.json
```

### Custom Concurrency

```bash
node script.js \
  --items-file=/tmp/upload-list.json \
  --max-concurrency=5
```

### Debug Mode (Visible Browsers)

```bash
node script.js \
  --items-file=/tmp/upload-list.json \
  --max-concurrency=2 \
  --debug
```

## How It Works

1. **Validates** all items and image paths before starting
2. **Pre-flight login check** — opens one browser, verifies session, handles
   interactive login in headed mode if needed, then saves cookies and closes
3. **Worker pool** — spawns up to `--max-concurrency` browser instances in parallel;
   each worker pulls items from a shared queue so faster workers pick up more work
4. **Each worker** restores cookies from disk, navigates to the part's Images section,
   and uploads the image — then closes its browser
5. **Aggregates results** — reports success/failure counts and exits with code 1 if
   any uploads failed

## Login Flow

Login is handled **once** before the pool starts:

- If cookies are valid → workers start immediately in headless mode
- If login is needed → a headed browser opens, you log in manually, cookies are saved,
  then all workers start headless

Workers do **not** attempt re-login. If a session expires mid-run, affected workers
fail with a clear error message; re-run the script to trigger a fresh login.

## Output

### Success (all uploads completed)

```json
{
  "success": true,
  "data": {
    "total": 3,
    "succeeded": 3,
    "failed": 0,
    "results": [
      {
        "success": true,
        "partId": "7wxwfbecvjg3xa86bf1tsmy7mj",
        "imagePath": "/tmp/images/part1.jpg",
        "partUrl": "https://partsbox.com/melkor/parts/7wxwfbecvjg3xa86bf1tsmy7mj",
        "duration": 12345
      }
    ]
  },
  "metadata": {
    "timestamp": "2026-02-20T10:30:00.000Z",
    "duration": 25000,
    "maxConcurrency": 10,
    "browser": "chromium"
  }
}
```

### Partial failure

```json
{
  "success": false,
  "data": {
    "total": 3,
    "succeeded": 2,
    "failed": 1,
    "results": [
      { "success": true,  "partId": "...", "duration": 12345 },
      { "success": false, "partId": "...", "error": "Could not find image upload control", "duration": 8000 }
    ]
  }
}
```

Exit code is `1` when any uploads fail, `0` when all succeed.

## Notes

- Shared code lives in `../lib/session.js` — both this script and `upload-item-image`
  use the same login detection, cookie management, and upload logic
- Each browser instance is fully independent — no shared state between workers
- Error screenshots saved to `./screenshots/` with timestamps
- Session cookies persisted at `~/.cache/playwright-profiles/partsbox/cookies.json`
  (persistent Docker volume — survives container rebuilds)

## Troubleshooting

### Session expired during run

Re-run the script. The pre-flight check will detect the expired session and open
a headed browser for you to log in again.

### Upload control not found

Run with `--debug --max-concurrency=1` and check the error screenshot in `./screenshots/`.
PartsBox UI may have changed — inspect the page to find the correct selectors.

### High failure rate

Reduce `--max-concurrency` to avoid overwhelming the PartsBox server or hitting
rate limits.
