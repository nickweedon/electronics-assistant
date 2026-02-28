#!/usr/bin/env node

/**
 * bulk-upload-item-image - Upload images to multiple PartsBox parts concurrently
 *
 * Reads a JSON file of {partId, imagePath} pairs and uploads all images using
 * a bounded worker pool of independent browser instances. Login is checked once
 * before the pool starts; all workers then run headless using saved cookies.
 *
 * Parameters:
 *   --items-file        Path to JSON file with upload list (required)
 *   --max-concurrency   Max simultaneous browser instances (default: 10)
 *   --timeout           Per-browser timeout in ms (default: 30000)
 *   --debug             Run workers in headed mode for debugging (optional)
 *
 * Items file format (JSON array):
 *   [
 *     { "partId": "7wxwfbecvjg3xa86bf1tsmy7mj", "imagePath": "/tmp/part1.jpg" },
 *     { "partId": "8abc...",                      "imagePath": "/tmp/part2.jpg" }
 *   ]
 */

const {
  PARTSBOX_BASE_URL,
  restoreCookies,
  isLoginRequired,
  launchBrowser,
  ensureLoggedIn,
  navigateToImagesSection,
  uploadImage,
  ensureDirs
} = require('../lib/session');

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = {};
process.argv.slice(2).forEach(arg => {
  if (arg === '--debug') {
    args.debug = true;
  } else {
    const [key, ...rest] = arg.replace('--', '').split('=');
    args[key] = rest.join('=') || 'true';
  }
});

// Configuration
const config = {
  headless: args.headless !== 'false' && !args.debug,
  timeout: parseInt(args.timeout) || 30000,
  maxConcurrency: parseInt(args['max-concurrency']) || 10,
  screenshotDir: './screenshots'
};

ensureDirs(config.screenshotDir);

// ── Worker pool ───────────────────────────────────────────────────────────────

/**
 * Runs `processItem` over all items with at most `maxConcurrency` concurrent
 * executions. Items are dispatched from a shared queue so fast workers pick up
 * more work rather than each worker getting a pre-assigned slice.
 *
 * @param {Array}    items          - Items to process
 * @param {number}   maxConcurrency - Upper bound on parallel workers
 * @param {Function} processItem    - async (item) => result
 * @returns {Promise<Array>}        - Results in completion order
 */
async function runWithConcurrency(items, maxConcurrency, processItem) {
  const results = [];
  const queue = [...items];
  const workerCount = Math.min(maxConcurrency, items.length);

  const workers = Array.from({ length: workerCount }, async (_, workerId) => {
    while (queue.length > 0) {
      const item = queue.shift();
      if (!item) break;
      results.push(await processItem(item, workerId));
    }
  });

  await Promise.all(workers);
  return results;
}

// ── Single-item upload (one browser instance) ─────────────────────────────────

async function uploadOneItem(item, workerId) {
  const { partId, imagePath } = item;
  const partUrl = `${PARTSBOX_BASE_URL}/${partId}`;
  const tag = `[W${workerId}][${partId.slice(0, 8)}]`;
  const startTime = Date.now();

  console.error(`${tag} Starting upload: ${imagePath}`);

  let browser;
  try {
    const { browser: b, context, page } = await launchBrowser(config.headless);
    browser = b;
    page.setDefaultTimeout(config.timeout);

    await restoreCookies(context);
    await navigateToImagesSection(page, partUrl, config.timeout);

    // Detect if session expired mid-run - report clearly rather than hanging
    if (await isLoginRequired(page)) {
      throw new Error(
        'Session expired during bulk run. Re-run the script to trigger a fresh login.'
      );
    }

    await uploadImage(page, imagePath, config.screenshotDir);

    const duration = Date.now() - startTime;
    console.error(`${tag} ✅ Done in ${duration}ms`);

    return {
      success: true,
      partId,
      imagePath: path.resolve(imagePath),
      partUrl,
      duration
    };
  } catch (err) {
    const duration = Date.now() - startTime;
    console.error(`${tag} ❌ Failed: ${err.message}`);
    return {
      success: false,
      partId,
      imagePath: path.resolve(imagePath),
      partUrl,
      duration,
      error: err.message
    };
  } finally {
    if (browser) {
      try { await browser.close(); } catch (_) {}
    }
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const startTime = Date.now();

  // Validate parameters
  if (!args['items-file']) throw new Error('Missing required parameter: --items-file');

  const itemsFile = args['items-file'];
  if (!fs.existsSync(itemsFile)) throw new Error(`Items file not found: ${itemsFile}`);

  let items;
  try {
    items = JSON.parse(fs.readFileSync(itemsFile, 'utf-8'));
  } catch (e) {
    throw new Error(`Failed to parse items file: ${e.message}`);
  }

  if (!Array.isArray(items) || items.length === 0) {
    throw new Error('Items file must be a non-empty JSON array');
  }

  // Validate each item
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    if (!item.partId) throw new Error(`Item ${i}: missing "partId"`);
    if (!item.imagePath) throw new Error(`Item ${i}: missing "imagePath"`);
    if (!fs.existsSync(item.imagePath)) {
      throw new Error(`Item ${i} (${item.partId}): image not found: ${item.imagePath}`);
    }
  }

  console.error(`[INFO] Items to upload: ${items.length}`);
  console.error(`[INFO] Max concurrency: ${config.maxConcurrency}`);
  console.error(`[INFO] Timeout per browser: ${config.timeout}ms`);
  console.error(`[INFO] Mode: ${config.headless ? 'headless' : 'headed (debug)'}\n`);

  // ── Pre-flight: ensure login before spawning workers ──────────────────────
  // Login is handled interactively in a single browser. Once cookies are saved,
  // all concurrent headless workers reuse them without further login prompts.
  console.error('[INFO] Running pre-flight login check...');
  await ensureLoggedIn({ headless: config.headless, timeout: config.timeout });
  console.error('[INFO] Login check complete. Starting concurrent uploads...\n');

  // ── Run worker pool ───────────────────────────────────────────────────────
  const results = await runWithConcurrency(items, config.maxConcurrency, uploadOneItem);

  // ── Aggregate results ─────────────────────────────────────────────────────
  const succeeded = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  const duration = Date.now() - startTime;
  const output = {
    success: failed.length === 0,
    data: {
      total: items.length,
      succeeded: succeeded.length,
      failed: failed.length,
      results
    },
    metadata: {
      timestamp: new Date().toISOString(),
      duration,
      maxConcurrency: config.maxConcurrency,
      browser: 'chromium'
    }
  };

  if (failed.length > 0) {
    console.error(`\n⚠️  [SUMMARY] ${succeeded.length}/${items.length} succeeded, ${failed.length} failed:`);
    for (const f of failed) {
      console.error(`  ❌ ${f.partId}: ${f.error}`);
    }
  } else {
    console.error(`\n✅ [SUMMARY] All ${succeeded.length} uploads succeeded`);
  }

  console.log(JSON.stringify(output, null, 2));

  if (failed.length > 0) process.exit(1);
}

main().catch(async (error) => {
  console.error(`[ERROR] ${error.message}`);
  const errorResult = {
    success: false,
    data: null,
    metadata: { timestamp: new Date().toISOString(), browser: 'chromium' },
    error: { message: error.message, stack: error.stack }
  };
  console.log(JSON.stringify(errorResult, null, 2));
  process.exit(1);
});
