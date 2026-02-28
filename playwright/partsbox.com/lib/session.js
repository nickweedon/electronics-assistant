'use strict';

/**
 * lib/session.js - Shared PartsBox browser session utilities
 *
 * Provides cookie-based session persistence, login detection/handling,
 * browser launch helpers, and image upload logic for all partsbox.com scripts.
 *
 * NOTE: playwright-extra stealth breaks launchPersistentContext(), so we use
 * launch() + newContext() with manual cookie save/restore instead.
 */

const playwright = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Apply stealth plugin once (module is cached by Node.js - safe to call once)
playwright.chromium.use(StealthPlugin());

// ── Constants ────────────────────────────────────────────────────────────────

const PARTSBOX_BASE_URL = 'https://partsbox.com/melkor/parts';
const COOKIE_FILE = path.join(os.homedir(), '.cache', 'playwright-profiles', 'partsbox', 'cookies.json');
const COOKIE_DIR = path.dirname(COOKIE_FILE);

const LAUNCH_ARGS = [
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--disable-dev-shm-usage',
  '--disable-blink-features=AutomationControlled',
  '--disable-session-crashed-bubble',
  '--hide-crash-restore-bubble'
];

const CONTEXT_OPTIONS = {
  viewport: { width: 1920, height: 1080 },
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  locale: 'en-US',
  timezoneId: 'America/New_York',
  permissions: [],
  extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' }
};

// ── Filesystem helpers ───────────────────────────────────────────────────────

function ensureDirs(...dirs) {
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  }
}

// ── Cookie-based session persistence ────────────────────────────────────────

async function saveCookies(context) {
  ensureDirs(COOKIE_DIR);
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

// ── Login helpers ────────────────────────────────────────────────────────────

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

// ── Browser launch helper ────────────────────────────────────────────────────

async function launchBrowser(headless) {
  const browser = await playwright.chromium.launch({ headless, args: LAUNCH_ARGS });
  const context = await browser.newContext(CONTEXT_OPTIONS);
  const page = await context.newPage();
  return { browser, context, page };
}

// ── Pre-flight login check ───────────────────────────────────────────────────

/**
 * Ensures the user is logged into PartsBox before bulk operations begin.
 * Opens a single browser, checks authentication, handles interactive login
 * in headed mode if needed, saves cookies, then closes the browser.
 *
 * All subsequent headless workers can then read the saved cookies directly.
 *
 * @param {object} opts
 * @param {boolean} opts.headless  - Start headless (relaunches headed if login needed)
 * @param {number}  opts.timeout   - Navigation timeout in ms
 */
async function ensureLoggedIn({ headless = true, timeout = 30000 } = {}) {
  let { browser, context, page } = await launchBrowser(headless);
  page.setDefaultTimeout(timeout);

  await restoreCookies(context);
  await page.goto(PARTSBOX_BASE_URL, { waitUntil: 'domcontentloaded', timeout });
  await page.waitForTimeout(2000);

  if (await isLoginRequired(page)) {
    console.error('🔐 [LOGIN] Login required');

    if (headless) {
      console.error('🔄 [LOGIN] Relaunching in headed mode for manual login...\n');
      await browser.close();
      ({ browser, context, page } = await launchBrowser(false));
      page.setDefaultTimeout(timeout);
      await restoreCookies(context);
      await page.goto(PARTSBOX_BASE_URL, { waitUntil: 'domcontentloaded', timeout });
      await page.waitForTimeout(2000);
    }

    if (await isLoginRequired(page)) {
      await waitForLoginCompletion(page);
      await saveCookies(context);
    }
  } else {
    console.error('✅ [LOGIN] Already logged in (session restored)');
  }

  await browser.close();
}

// ── Upload helpers ───────────────────────────────────────────────────────────

async function navigateToImagesSection(page, partUrl, timeout) {
  console.error(`[INFO] Opening part page: ${partUrl}`);
  await page.goto(partUrl, { waitUntil: 'domcontentloaded', timeout });
  await page.waitForTimeout(2000);

  const sidebarLink = page.locator('a:has-text("Images"), a:has-text("Images & Files")').first();
  if (await sidebarLink.count() > 0) {
    await sidebarLink.click();
    await page.waitForTimeout(2000);
    console.error('[UPLOAD] Navigated to Images & Files section');
  } else {
    console.error('[WARN] Could not find "Images & Files" link - staying on main page');
  }
}

async function uploadImage(page, imagePath, screenshotDir) {
  console.error('[UPLOAD] Looking for upload controls...');

  // Strategy 1: File input already present
  let fileInputs = await page.$$('input[type="file"]');
  if (fileInputs.length > 0) {
    console.error(`📤 [UPLOAD] Found existing file input, uploading: ${imagePath}`);
    await fileInputs[fileInputs.length - 1].setInputFiles(imagePath);
    await page.waitForTimeout(3000);
    console.error('✅ [UPLOAD] Image uploaded!');
    return;
  }

  // Strategy 2: Click "Upload (or drop files)" button - PartsBox React SPA creates
  // a hidden <input type="file"> dynamically on click
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
  const errShot = path.join(screenshotDir, `no-upload-${Date.now()}.png`);
  await page.screenshot({ path: errShot, fullPage: true });
  console.error(`📸 [ERROR] Screenshot: ${errShot}`);
  throw new Error('Could not find image upload control on PartsBox page');
}

// ── Exports ──────────────────────────────────────────────────────────────────

module.exports = {
  PARTSBOX_BASE_URL,
  COOKIE_FILE,
  LAUNCH_ARGS,
  CONTEXT_OPTIONS,
  ensureDirs,
  saveCookies,
  restoreCookies,
  isLoginRequired,
  waitForLoginCompletion,
  launchBrowser,
  ensureLoggedIn,
  navigateToImagesSection,
  uploadImage
};
