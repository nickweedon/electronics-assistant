#!/usr/bin/env node

/**
 * get-order-url - Get Mouser order detail page URL by sales order number
 *
 * Navigates to the Mouser account orders page and extracts the detail link
 * for the given sales order number. Handles DataDome bot-protection and login
 * by switching to headed mode when needed, then saving session cookies.
 *
 * Parameters:
 *   --order-number   Mouser sales order number, e.g. 278499916 (required)
 *   --debug          Run in headed mode for debugging (optional)
 *   --timeout        Per-navigation timeout in ms (default: 30000)
 */

'use strict';

const playwright = require('playwright-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
playwright.chromium.use(StealthPlugin());

const fs   = require('fs');
const path = require('path');
const os   = require('os');
const { execSync } = require('child_process');

// ── Config ───────────────────────────────────────────────────────────────────

const COOKIE_FILE = path.join(os.homedir(), '.cache', 'playwright-profiles', 'mouser', 'cookies.json');
const ORDERS_URL  = 'https://www.mouser.com/account/orders';

const LAUNCH_ARGS = [
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--disable-dev-shm-usage',
  '--disable-blink-features=AutomationControlled',
  '--disable-session-crashed-bubble',
  '--hide-crash-restore-bubble',
  '--disable-infobars',
  '--window-size=1920,1080',
  '--lang=en-US,en'
];

const CONTEXT_OPTIONS = {
  viewport: { width: 1920, height: 1080 },
  // Must match the actual Playwright Chromium version to avoid UA/version mismatch detection
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
  locale: 'en-US',
  timezoneId: 'America/New_York',
  colorScheme: 'light',
  deviceScaleFactor: 1,
  hasTouch: false,
  isMobile: false,
  extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' }
};

// ── Arg parsing ──────────────────────────────────────────────────────────────

const args = {};
process.argv.slice(2).forEach(arg => {
  if (arg === '--debug') {
    args.debug = true;
  } else {
    const [key, ...rest] = arg.replace('--', '').split('=');
    args[key] = rest.join('=') || 'true';
  }
});

// ── Session helpers ──────────────────────────────────────────────────────────

async function saveCookies(context) {
  const dir = path.dirname(COOKIE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const cookies = await context.cookies();
  fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
  console.error(`[SESSION] Saved ${cookies.length} cookies`);
}

async function restoreCookies(context) {
  if (!fs.existsSync(COOKIE_FILE)) {
    console.error('[SESSION] No saved cookies found');
    return false;
  }
  const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE, 'utf-8'));
  await context.addCookies(cookies);
  console.error(`[SESSION] Restored ${cookies.length} cookies`);
  return true;
}

async function launchBrowser(headless) {
  const browser = await playwright.chromium.launch({ headless, args: LAUNCH_ARGS });
  const context = await browser.newContext(CONTEXT_OPTIONS);
  const page    = await context.newPage();
  return { browser, context, page };
}

// ── Auth/challenge detection ─────────────────────────────────────────────────

async function isDataDomeBlocked(page) {
  const url = page.url();
  if (url.includes('datadome') || url.includes('captcha')) return true;
  // DataDome serves its challenge as an inline iframe at the ORIGINAL URL —
  // the URL never changes, so we must check page content too.
  try {
    return await page.evaluate(() => {
      // DataDome injects window.dd with rt:'c' when blocking
      if (typeof window.dd !== 'undefined') return true;
      // Look for captcha-delivery.com iframes
      const iframes = document.querySelectorAll(
        'iframe[src*="captcha-delivery.com"], iframe[src*="datadome"]'
      );
      if (iframes.length > 0) return true;
      // Inline script containing DataDome fingerprint token
      for (const s of document.querySelectorAll('script:not([src])')) {
        if (s.textContent.includes("'rt':'c'") || s.textContent.includes('"rt":"c"')) return true;
      }
      return false;
    });
  } catch (_) { return false; }
}

async function isLoginRequired(page) {
  const url = page.url();
  if (url.includes('/signin') || url.includes('/Login') || url.includes('/login')) return true;
  try {
    if (await page.locator('input[type="password"]').count() > 0) return true;
  } catch (_) {}
  return false;
}

async function needsInteraction(page) {
  return await isDataDomeBlocked(page) || await isLoginRequired(page);
}

async function waitForOrdersPage(page, timeout = 300000) {
  console.error('\n⏳ [WAIT] Waiting for you to complete login or CAPTCHA challenge...');
  console.error('🖱️  [WAIT] Please complete any challenge or login in the browser window');
  console.error('⚠️  [WAIT] Do NOT close the browser\n');
  try { execSync('xmessage -center "Claude: Please log in / complete CAPTCHA in the Mouser browser window." &'); }
  catch (_) {}

  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    await page.waitForTimeout(2000);
    const url = page.url();
    if (url.includes('/account/orders') && !await isDataDomeBlocked(page) && !await isLoginRequired(page)) {
      console.error('✅ [AUTH] Successfully on orders page\n');
      return;
    }
  }
  throw new Error('Timeout waiting for Mouser orders page — login/challenge not completed in time');
}

// ── Order URL extraction ─────────────────────────────────────────────────────

async function extractOrderUrl(page, orderNumber) {
  console.error(`[INFO] Looking for order ${orderNumber} on orders page...`);
  await page.waitForTimeout(3000);

  // Strategy 1: find an <a> whose text or href contains the order number
  const links = await page.$$eval('a', els =>
    els.map(a => ({ text: a.textContent.trim(), href: a.href }))
  );

  const match = links.find(l =>
    l.text.includes(orderNumber) || l.href.includes(orderNumber)
  );
  if (match && match.href) {
    console.error(`[INFO] Found order link: ${match.href}`);
    return match.href;
  }

  // Strategy 2: click on the row containing the order number, capture nav
  const rowText = page.locator(`text=${orderNumber}`).first();
  if (await rowText.count() > 0) {
    // Look for a nearby link
    const nearLink = page.locator(`a:near(:text("${orderNumber}"), 100)`).first();
    if (await nearLink.count() > 0) {
      const href = await nearLink.getAttribute('href');
      if (href) {
        const full = href.startsWith('http') ? href : `https://www.mouser.com${href}`;
        console.error(`[INFO] Found nearby link: ${full}`);
        return full;
      }
    }
    // Click the row itself and capture resulting URL
    await rowText.click();
    await page.waitForTimeout(2000);
    const url = page.url();
    if (url.includes('detail') || url.includes('order')) {
      console.error(`[INFO] Navigated to: ${url}`);
      return url;
    }
  }

  return null;
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const startTime   = Date.now();
  const orderNumber = args['order-number'];
  if (!orderNumber) throw new Error('Missing required parameter: --order-number');

  const timeout  = parseInt(args.timeout) || 30000;
  let   headless = !args.debug;

  let browser, context, page;

  try {
    ({ browser, context, page } = await launchBrowser(headless));
    page.setDefaultTimeout(timeout);

    await restoreCookies(context);
    await page.goto(ORDERS_URL, { waitUntil: 'domcontentloaded', timeout });
    await page.waitForTimeout(3000);

    if (await needsInteraction(page)) {
      console.error('🔐 [AUTH] Login or DataDome challenge detected');
      if (headless) {
        console.error('🔄 [AUTH] Relaunching in headed mode for manual interaction...');
        await browser.close();
        ({ browser, context, page } = await launchBrowser(false));
        page.setDefaultTimeout(300000);
        await restoreCookies(context);
        await page.goto(ORDERS_URL, { waitUntil: 'domcontentloaded', timeout });
        await page.waitForTimeout(3000);
      }
      await waitForOrdersPage(page, 300000);
      await saveCookies(context);
    } else {
      console.error('✅ [AUTH] Already authenticated');
    }

    const orderUrl = await extractOrderUrl(page, orderNumber);
    await saveCookies(context);
    await browser.close();

    console.log(JSON.stringify({
      success: !!orderUrl,
      data: { orderNumber, orderUrl: orderUrl || null },
      metadata: {
        timestamp: new Date().toISOString(),
        duration: Date.now() - startTime,
        browser: 'chromium'
      }
    }, null, 2));

    if (!orderUrl) {
      console.error(`[WARN] Could not find detail link for order ${orderNumber}`);
      process.exit(1);
    }

  } catch (err) {
    if (browser) await browser.close().catch(() => {});
    console.log(JSON.stringify({ success: false, error: { message: err.message } }, null, 2));
    process.exit(1);
  }
}

main();
