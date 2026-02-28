#!/usr/bin/env node

/**
 * upload-item-image - Upload image to PartsBox part
 *
 * Uploads an image file to a PartsBox part with smart login detection.
 * Switches to headed mode when login is needed, waits for manual login,
 * then saves session cookies for reuse across runs.
 *
 * Parameters:
 *   --part-id      PartsBox part ID (required)
 *   --image-path   Path to image file to upload (required)
 *   --debug        Run in headed mode for debugging (optional)
 *   --timeout      Timeout in ms (default: 30000)
 */

const {
  PARTSBOX_BASE_URL,
  saveCookies,
  restoreCookies,
  isLoginRequired,
  waitForLoginCompletion,
  launchBrowser,
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
  screenshotDir: './screenshots'
};

// Ensure directories exist
ensureDirs(config.screenshotDir);

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const startTime = Date.now();

  // Validate parameters
  if (!args['part-id']) throw new Error('Missing required parameter: --part-id');
  if (!args['image-path']) throw new Error('Missing required parameter: --image-path');

  const partId = args['part-id'];
  const imagePath = args['image-path'];
  if (!fs.existsSync(imagePath)) throw new Error(`Image file not found: ${imagePath}`);

  const partUrl = `${PARTSBOX_BASE_URL}/${partId}`;
  console.error(`[INFO] Part ID: ${partId}`);
  console.error(`[INFO] Image: ${imagePath}`);

  // --- Attempt 1: headless with saved session ---
  let { browser, context, page } = await launchBrowser(config.headless);
  console.error(`[INFO] Browser launched (${config.headless ? 'headless' : 'headed'})`);

  await restoreCookies(context);
  await page.goto(partUrl, { waitUntil: 'domcontentloaded', timeout: config.timeout });
  await page.waitForTimeout(2000);

  // --- Login handling ---
  if (await isLoginRequired(page)) {
    console.error('🔐 [LOGIN] Login required');

    if (config.headless) {
      console.error('🔄 [LOGIN] Relaunching in headed mode for manual login...\n');
      await browser.close();
      ({ browser, context, page } = await launchBrowser(false));
      await restoreCookies(context);
      await page.goto(partUrl, { waitUntil: 'domcontentloaded', timeout: config.timeout });
      await page.waitForTimeout(2000);
    }

    if (await isLoginRequired(page)) {
      await waitForLoginCompletion(page);
      // Save session immediately after login
      await saveCookies(context);

      // Navigate to part page after login
      console.error('🔄 [INFO] Returning to part page...');
      await page.goto(partUrl, { waitUntil: 'domcontentloaded', timeout: config.timeout });
      await page.waitForTimeout(2000);
    }
  } else {
    console.error('✅ [LOGIN] Already logged in (session restored)');
  }

  // --- Navigate to Images & Files section ---
  await navigateToImagesSection(page, partUrl, config.timeout);

  // --- Upload image ---
  await uploadImage(page, imagePath, config.screenshotDir);

  // Save cookies after successful operation
  await saveCookies(context);

  const duration = Date.now() - startTime;
  const result = {
    success: true,
    data: { partId, partUrl, imagePath: path.resolve(imagePath), uploaded: true },
    metadata: {
      url: page.url(),
      timestamp: new Date().toISOString(),
      duration,
      browser: 'chromium',
      screenshots: []
    }
  };

  console.log(JSON.stringify(result, null, 2));
  await browser.close();
  console.error('[INFO] Browser closed (session saved)');
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
