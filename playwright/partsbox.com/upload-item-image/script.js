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

const playwright = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Apply stealth plugin to avoid detection
playwright.chromium.use(StealthPlugin());

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
  screenshotOnError: true,
  screenshotDir: './screenshots',
  cookieDir: path.join(os.homedir(), '.cache', 'playwright-profiles', 'partsbox'),
  viewport: { width: 1920, height: 1080 },
  partsBoxBaseUrl: 'https://partsbox.com/melkor/parts'
};

const COOKIE_FILE = path.join(config.cookieDir, 'cookies.json');
const LAUNCH_ARGS = [
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--disable-dev-shm-usage',
  '--disable-blink-features=AutomationControlled',
  '--disable-session-crashed-bubble',
  '--hide-crash-restore-bubble'
];
const CONTEXT_OPTIONS = {
  viewport: config.viewport,
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  locale: 'en-US',
  timezoneId: 'America/New_York',
  permissions: [],
  extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' }
};

// Ensure directories exist
for (const dir of [config.screenshotDir, config.cookieDir]) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

// ============================================================
// Cookie-based session persistence
// (playwright-extra stealth breaks launchPersistentContext)
// ============================================================

async function saveCookies(context) {
  const cookies = await context.cookies();
  fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
  console.error(`[SESSION] Saved ${cookies.length} cookies to ${COOKIE_FILE}`);
}

async function restoreCookies(context) {
  if (!fs.existsSync(COOKIE_FILE)) {
    console.error('[SESSION] No saved cookies found');
    return false;
  }
  try {
    const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE, 'utf-8'));
    await context.addCookies(cookies);
    console.error(`[SESSION] Restored ${cookies.length} cookies`);
    return true;
  } catch (e) {
    console.error(`[SESSION] Failed to restore cookies: ${e.message}`);
    return false;
  }
}

// ============================================================
// Login helpers
// ============================================================

async function isLoginRequired(page) {
  const url = page.url();
  if (url.includes('/login') || url.includes('/signin')) return true;

  try {
    if (await page.locator('text=/Log in to your PartsBox/i').count() > 0) return true;

    const hasEmail = await page.locator('input[type="email"], input[name="email"]').count();
    const hasPassword = await page.locator('input[type="password"], input[name="password"]').count();
    if (hasEmail > 0 && hasPassword > 0) return true;

    if (await page.locator('button:has-text("Login"), button:has-text("Log in")').count() > 0) return true;
  } catch (e) {
    console.error('[WARN] Error checking login status:', e.message);
  }
  return false;
}

async function waitForLoginCompletion(page) {
  console.error('\n⏳ [WAIT] Waiting for you to complete login...');
  console.error('🖱️  [WAIT] Please login in the browser window');
  console.error('⚠️  [WAIT] Do NOT close the browser\n');

  for (let i = 1; i <= 120; i++) {
    await page.waitForTimeout(1000);
    if (!await isLoginRequired(page)) {
      console.error('✅ [LOGIN] Login detected as complete!\n');
      return;
    }
    if (i % 10 === 0) console.error(`⏳ [WAIT] Still waiting... (${i}s)`);
  }
  throw new Error('Login timeout - 2 minutes elapsed');
}

// ============================================================
// Browser launch helper
// ============================================================

async function launchBrowser(headless) {
  const browser = await playwright.chromium.launch({ headless, args: LAUNCH_ARGS });
  const context = await browser.newContext(CONTEXT_OPTIONS);
  const page = await context.newPage();
  page.setDefaultTimeout(config.timeout);
  return { browser, context, page };
}

// ============================================================
// Upload logic
// ============================================================

async function navigateToImagesSection(page, partUrl) {
  console.error(`[INFO] Opening part page: ${partUrl}`);
  await page.goto(partUrl, { waitUntil: 'domcontentloaded', timeout: config.timeout });
  await page.waitForTimeout(2000);

  // Click "Images & Files" in the left sidebar
  console.error('[UPLOAD] Clicking "Images & Files" sidebar link...');
  const sidebarLink = page.locator('a:has-text("Images"), a:has-text("Images & Files")').first();
  if (await sidebarLink.count() > 0) {
    await sidebarLink.click();
    await page.waitForTimeout(2000);
    console.error('[UPLOAD] Navigated to Images & Files section');
  } else {
    console.error('[WARN] Could not find "Images & Files" link - staying on main page');
  }
}

async function uploadImage(page, imagePath) {
  console.error('[UPLOAD] Looking for upload controls...');

  // Strategy 1: Check if file input already exists (e.g. from previous interaction)
  let fileInputs = await page.$$('input[type="file"]');
  if (fileInputs.length > 0) {
    console.error(`📤 [UPLOAD] Found existing file input, uploading: ${imagePath}`);
    await fileInputs[fileInputs.length - 1].setInputFiles(imagePath);
    await page.waitForTimeout(3000);
    console.error('✅ [UPLOAD] Image uploaded!');
    return;
  }

  // Strategy 2: Click "Upload (or drop files)" button which dynamically creates a file input
  // PartsBox uses a React/Reagent SPA - the button creates a hidden <input type="file"> on click
  const uploadBtnSelectors = [
    'div.ui.tiny.button:has-text("Upload")',
    'div.ui.button:has-text("Upload")',
    'text=/Upload.*drop.*files/i'
  ];

  for (const sel of uploadBtnSelectors) {
    try {
      const btn = page.locator(sel).first();
      if (await btn.count() > 0) {
        console.error(`[UPLOAD] Clicking upload button: ${sel}`);
        await btn.click();
        await page.waitForTimeout(1000);

        // The click creates a hidden file input - find and use it
        fileInputs = await page.$$('input[type="file"]');
        if (fileInputs.length > 0) {
          console.error(`📤 [UPLOAD] File input appeared after click, uploading: ${imagePath}`);
          await fileInputs[fileInputs.length - 1].setInputFiles(imagePath);
          await page.waitForTimeout(3000);
          console.error('✅ [UPLOAD] Image uploaded!');
          return;
        }
      }
    } catch (e) { /* try next selector */ }
  }

  // Failed - take diagnostic screenshot
  const errShot = path.join(config.screenshotDir, `no-upload-${Date.now()}.png`);
  await page.screenshot({ path: errShot, fullPage: true });
  console.error(`📸 [ERROR] Screenshot: ${errShot}`);
  throw new Error('Could not find image upload control on PartsBox page');
}

// ============================================================
// Main
// ============================================================

async function main() {
  const startTime = Date.now();

  // Validate parameters
  if (!args['part-id']) throw new Error('Missing required parameter: --part-id');
  if (!args['image-path']) throw new Error('Missing required parameter: --image-path');

  const partId = args['part-id'];
  const imagePath = args['image-path'];
  if (!fs.existsSync(imagePath)) throw new Error(`Image file not found: ${imagePath}`);

  const partUrl = `${config.partsBoxBaseUrl}/${partId}`;
  console.error(`[INFO] Part ID: ${partId}`);
  console.error(`[INFO] Image: ${imagePath}`);
  console.error(`[INFO] Cookie file: ${COOKIE_FILE}\n`);

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
  await navigateToImagesSection(page, partUrl);

  // --- Upload image ---
  await uploadImage(page, imagePath);

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
