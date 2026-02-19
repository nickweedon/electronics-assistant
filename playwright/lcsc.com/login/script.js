#!/usr/bin/env node

/**
 * LCSC Login
 * Opens a headed browser, navigates to the LCSC homepage, clicks the Login
 * button (which sets up the proper OAuth redirect chain), waits for the user
 * to authenticate, then saves all cookies including the wmsc.lcsc.com session.
 *
 * Exits automatically once login is complete and orders page is accessible.
 *
 * Parameters:
 * - timeout: Login timeout in milliseconds (default: 300000 = 5 min)
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const args = {};
process.argv.slice(2).forEach(arg => {
  const [key, ...rest] = arg.replace(/^--/, '').split('=');
  args[key] = rest.join('=');
});

const timeout = parseInt(args.timeout) || 300000;

const COOKIE_FILE = path.join(os.homedir(), '.cache', 'playwright-profiles', 'lcsc.com', 'cookies.json');
const HOME_URL = 'https://www.lcsc.com';
const ORDERS_URL = 'https://www.lcsc.com/order/list';

const screenshotDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });

async function saveCookies(context) {
  const dir = path.dirname(COOKIE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const cookies = await context.cookies();
  fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
  console.error(`[INFO] Saved ${cookies.length} cookies to ${COOKIE_FILE}`);
}

async function main() {
  const startTime = Date.now();
  let browser = null;

  try {
    browser = await chromium.launch({
      headless: false,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled'
      ]
    });

    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      locale: 'en-US',
      timezoneId: 'America/New_York',
      extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' }
    });

    const page = await context.newPage();

    // Step 1: Navigate to LCSC homepage
    console.error('[INFO] Navigating to LCSC homepage...');
    await page.goto(HOME_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(2000);

    // Step 2: Click the Login button — this sets up the full OAuth chain
    // (passport → wmsc.lcsc.com callback → www.lcsc.com)
    console.error('[INFO] Clicking Login button...');
    await page.locator('div.mt-1.text-center.text-truncate.hidden-down-960:has-text("Login")').click();
    await page.waitForTimeout(2000);

    // Notify user
    try { execSync('xmessage -center "LCSC: Please log in in the browser window." &'); }
    catch (_) {}

    // Step 3: Wait for user to log in and complete the full OAuth chain back to www.lcsc.com
    console.error('[INFO] Waiting for login to complete (up to 5 minutes)...');
    await page.waitForURL(
      url => url.toString().startsWith('https://www.lcsc.com') && !url.toString().includes('passport'),
      { timeout }
    );
    console.error('[INFO] Login and OAuth chain complete.');
    await page.waitForTimeout(3000);

    await saveCookies(context);

    // Step 4: Verify the orders page is now accessible
    console.error('[INFO] Verifying orders page access...');
    try {
      await page.goto(ORDERS_URL, { waitUntil: 'networkidle', timeout: 20000 });
      const finalUrl = page.url();
      if (finalUrl.includes('/order/list')) {
        console.error('[INFO] Orders page confirmed accessible.');
        await page.waitForTimeout(2000);
        await saveCookies(context); // re-save with any extra cookies from orders page
      } else {
        console.error(`[WARN] Orders page redirected to ${finalUrl} — cookies may need re-auth on first use.`);
      }
    } catch (_) {}

    const result = {
      success: true,
      data: { cookieFile: COOKIE_FILE },
      metadata: {
        url: page.url(),
        timestamp: new Date().toISOString(),
        duration: Date.now() - startTime
      }
    };

    console.log(JSON.stringify(result, null, 2));

  } catch (err) {
    const result = {
      success: false,
      error: { message: err.message },
      metadata: { timestamp: new Date().toISOString(), duration: Date.now() - startTime }
    };
    console.log(JSON.stringify(result, null, 2));
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

main();
