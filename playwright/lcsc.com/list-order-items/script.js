#!/usr/bin/env node

/**
 * LCSC List Order Items
 * Retrieve all line items within a specific LCSC order.
 *
 * If no valid session is found, automatically launches a headed browser for
 * login, then proceeds once authentication is complete.
 *
 * Parameters:
 * - orderId:  Order hex token OR full detail URL (required)
 *             e.g. --orderId=B5A239BAC5A96F0F8AF86807A40667EC
 *             or   --orderId=https://www.lcsc.com/order/detail/B5A239BAC5A96F0F8AF86807A40667EC
 * - headless: Run in headless mode (default: true)
 * - timeout:  Timeout in milliseconds (default: 20000)
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

const orderIdArg = args.orderId || args.orderToken || args.id || '';
const headless = args.headless !== 'false';
const timeout = parseInt(args.timeout) || 20000;

if (!orderIdArg) {
  console.error('[ERROR] orderId parameter is required');
  console.error('Usage: node script.js --orderId=B5A239BAC5A96F0F8AF86807A40667EC [--headless=true] [--timeout=20000]');
  process.exit(1);
}

function resolveDetailUrl(input) {
  if (input.startsWith('http')) return input;
  return `https://www.lcsc.com/order/detail/${input}`;
}

const detailUrl = resolveDetailUrl(orderIdArg);

const COOKIE_FILE = path.join(os.homedir(), '.cache', 'playwright-profiles', 'lcsc.com', 'cookies.json');
const LOGIN_SCRIPT = path.join(__dirname, '..', 'login', 'script.js');

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

async function fetchOrderItems() {
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

    console.error(`[INFO] Navigating to ${detailUrl}...`);
    await page.goto(detailUrl, { waitUntil: 'networkidle', timeout });

    const currentUrl = page.url();
    if (!currentUrl.includes('/order/detail/')) {
      return null; // signal auth failure
    }

    console.error('[INFO] Waiting for order items to render...');
    await page.waitForTimeout(3000);

    const orderMeta = await page.evaluate(() => {
      const meta = {};
      document.querySelectorAll('.row-item').forEach(item => {
        const label = item.querySelector('.major4--text');
        const value = item.querySelector('.major2--text.font-Bold-600');
        if (label && value) {
          const key = label.textContent.trim().replace(/:$/, '').trim().toLowerCase().replace(/\s+/g, '_');
          meta[key] = value.textContent.trim();
        }
      });
      return meta;
    });

    const items = await page.evaluate(() => {
      const productItems = Array.from(document.querySelectorAll('.productItem'));
      return productItems.map(item => {
        const lcscLink = item.querySelector('.productDetails-col a.v2-a');
        const lcscCode = lcscLink ? lcscLink.textContent.trim() : '';
        const lcscUrl = lcscLink ? lcscLink.href : '';

        const boldDivs = Array.from(item.querySelectorAll('.productDetails-col .font-Bold-600'));
        let mpn = '';
        for (const div of boldDivs) {
          if (!div.querySelector('a') && div.textContent.trim()) {
            mpn = div.textContent.trim();
            break;
          }
        }

        const brandLink = item.querySelector('.productDetails-col a[href*="brand-detail"]');
        const manufacturer = brandLink ? brandLink.textContent.trim() : '';

        const descEl = item.querySelector('.productDetails-col .fz-12.major4--text');
        const description = descEl ? descEl.textContent.trim() : '';

        const qtySpans = Array.from(item.querySelectorAll('.quantity-col span'));
        let quantityOrdered = '';
        let quantityShipped = '';
        for (let i = 0; i < qtySpans.length - 1; i++) {
          const labelText = qtySpans[i].textContent.trim();
          if (labelText === 'Ordered:') quantityOrdered = qtySpans[i + 1].textContent.trim();
          if (labelText === 'Shipped:') quantityShipped = qtySpans[i + 1].textContent.trim();
        }

        const priceSpans = Array.from(item.querySelectorAll('.price-col span'));
        let unitPrice = '';
        let extPrice = '';
        for (let i = 0; i < priceSpans.length - 1; i++) {
          const labelText = priceSpans[i].textContent.trim();
          if (labelText === 'Unit Price:') unitPrice = priceSpans[i + 1].textContent.trim();
          if (labelText === 'Ext.Price:') extPrice = priceSpans[i + 1].textContent.trim();
        }

        return { lcscCode, lcscUrl, mpn, manufacturer, description, quantityOrdered, quantityShipped, unitPrice, extPrice };
      });
    });

    console.error(`[INFO] Found ${items.length} line item(s)`);
    return { orderMeta, items, url: currentUrl, duration: Date.now() - startTime };

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

    let result = await fetchOrderItems();

    // If auth failed, login and retry once
    if (result === null) {
      runLogin();
      result = await fetchOrderItems();
      if (result === null) {
        throw new Error('Authentication failed after login attempt. Please try again.');
      }
    }

    console.log(JSON.stringify({
      success: true,
      data: { order: result.orderMeta, items: result.items },
      metadata: {
        url: result.url,
        timestamp: new Date().toISOString(),
        duration: Date.now() - startTime,
        itemCount: result.items.length
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
