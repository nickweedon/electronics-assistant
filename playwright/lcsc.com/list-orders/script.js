#!/usr/bin/env node

/**
 * LCSC List Orders
 * Retrieve all orders from the LCSC account order list.
 *
 * If no valid session is found, automatically launches a headed browser for
 * login, then proceeds once authentication is complete.
 *
 * Parameters:
 * - headless: Run in headless mode (default: true)
 * - timeout:  Timeout in milliseconds (default: 15000)
 */

const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Parse command line arguments
const args = {};
process.argv.slice(2).forEach(arg => {
  const [key, ...rest] = arg.replace(/^--/, '').split('=');
  args[key] = rest.join('=');
});

const headless = args.headless !== 'false';
const timeout = parseInt(args.timeout) || 15000;

const COOKIE_FILE = path.join(os.homedir(), '.cache', 'playwright-profiles', 'lcsc.com', 'cookies.json');
const LOGIN_SCRIPT = path.join(__dirname, '..', 'login', 'script.js');
const ORDERS_URL = 'https://www.lcsc.com/order/list';

const screenshotDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });

function runLogin() {
  console.error('[INFO] Session not found or expired — launching login...');
  execFileSync('node', [LOGIN_SCRIPT], { stdio: 'inherit' });
  console.error('[INFO] Login complete. Continuing...');
}

async function restoreCookies(context) {
  if (!fs.existsSync(COOKIE_FILE)) return false;
  const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE, 'utf-8'));
  await context.addCookies(cookies);
  console.error(`[INFO] Loaded ${cookies.length} cookies`);
  return true;
}

async function fetchOrders() {
  const startTime = Date.now();
  let browser = null;
  let context = null;

  try {
    browser = await chromium.launch({
      headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled'
      ]
    });

    context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      locale: 'en-US',
      timezoneId: 'America/New_York',
      extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' }
    });

    await restoreCookies(context);

    const page = await context.newPage();
    page.setDefaultTimeout(timeout);

    console.error(`[INFO] Navigating to ${ORDERS_URL}...`);
    await page.goto(ORDERS_URL, { waitUntil: 'networkidle', timeout });

    const currentUrl = page.url();
    if (!currentUrl.includes('/order/list')) {
      return null; // signal auth failure
    }

    console.error('[INFO] Waiting for order list to render...');
    await page.waitForTimeout(3000);

    const orders = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('tbody tr'));
      return rows.map(row => {
        const tds = row.querySelectorAll('td');
        if (tds.length < 5) return null;

        const orderLink = tds[0].querySelector('a.v2-a');
        const orderId = orderLink ? orderLink.textContent.trim() : tds[0].textContent.trim();
        const detailHref = orderLink ? orderLink.href : null;

        const poNumber = tds[1] ? tds[1].textContent.trim() : '';
        const orderDate = tds[2] ? tds[2].textContent.trim() : '';

        const statusDiv = tds[3] ? tds[3].querySelector('div') : null;
        const status = statusDiv ? statusDiv.textContent.trim() : (tds[3] ? tds[3].textContent.trim() : '');

        const valueDiv = tds[4] ? tds[4].querySelector('div') : null;
        const totalAmount = valueDiv ? valueDiv.textContent.trim() : (tds[4] ? tds[4].textContent.trim() : '');

        let orderToken = null;
        if (detailHref) {
          const m = detailHref.match(/\/order\/detail\/([A-F0-9]+)/i);
          if (m) orderToken = m[1];
        }

        return { orderId, orderToken, poNumber, orderDate, status, totalAmount, detailUrl: detailHref };
      }).filter(Boolean);
    });

    console.error(`[INFO] Found ${orders.length} order(s)`);
    return { orders, url: currentUrl, duration: Date.now() - startTime };

  } finally {
    if (browser) await browser.close();
  }
}

async function main() {
  const startTime = Date.now();

  try {
    // First attempt
    if (!fs.existsSync(COOKIE_FILE)) {
      runLogin();
    }

    let result = await fetchOrders();

    // If auth failed, login and retry once
    if (result === null) {
      runLogin();
      result = await fetchOrders();
      if (result === null) {
        throw new Error('Authentication failed after login attempt. Please try again.');
      }
    }

    console.log(JSON.stringify({
      success: true,
      data: result.orders,
      metadata: {
        url: result.url,
        timestamp: new Date().toISOString(),
        duration: Date.now() - startTime,
        count: result.orders.length
      }
    }, null, 2));

  } catch (err) {
    console.log(JSON.stringify({
      success: false,
      error: { message: err.message, stack: err.stack },
      metadata: { timestamp: new Date().toISOString(), duration: Date.now() - startTime }
    }, null, 2));
    process.exit(1);
  }
}

main();
