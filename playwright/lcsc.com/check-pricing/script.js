#!/usr/bin/env node

/**
 * LCSC Check Pricing
 * Get detailed pricing, stock, and specifications for an LCSC part
 *
 * Parameters:
 * - lcscCode: LCSC part code (e.g., "C137394") - required
 * - timeout: Timeout in milliseconds (default: 10000)
 * - headless: Run in headless mode (default: true)
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = {};
process.argv.slice(2).forEach(arg => {
  const [key, value] = arg.replace('--', '').split('=');
  args[key] = value;
});

const lcscCode = args.lcscCode || args.code || '';
const headless = args.headless !== 'false';
const timeout = parseInt(args.timeout) || 10000;

if (!lcscCode) {
  console.error('[ERROR] lcscCode parameter is required');
  console.error('Usage: node script.js --lcscCode="C137394" [--headless=true] [--timeout=10000]');
  process.exit(1);
}

// Configuration
const config = {
  headless,
  timeout,
  screenshotOnError: true,
  screenshotDir: './screenshots',
  viewport: { width: 1920, height: 1080 }
};

// Ensure screenshot directory exists
if (!fs.existsSync(config.screenshotDir)) {
  fs.mkdirSync(config.screenshotDir, { recursive: true });
}

/**
 * Main execution function
 */
async function main() {
  const startTime = Date.now();
  let browser = null;
  let context = null;
  let page = null;

  try {
    console.error(`[INFO] Checking pricing for LCSC ${lcscCode}...`);

    // Launch browser
    browser = await chromium.launch({
      headless: config.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled'
      ]
    });

    // Create context with realistic settings
    context = await browser.newContext({
      viewport: config.viewport,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      locale: 'en-US',
      timezoneId: 'America/New_York',
      permissions: [],
      extraHTTPHeaders: {
        'Accept-Language': 'en-US,en;q=0.9'
      }
    });

    page = await context.newPage();
    page.setDefaultTimeout(config.timeout);

    // Navigate to product page
    const productUrl = `https://www.lcsc.com/product-detail/${lcscCode}.html`;
    console.error(`[INFO] Navigating to ${productUrl}...`);
    await page.goto(productUrl, {
      waitUntil: 'domcontentloaded',
      timeout: config.timeout
    });

    // Wait for page to fully load (SPA needs time)
    await page.waitForTimeout(6000);

    console.error('[INFO] Extracting product data...');

    // Extract all product information
    const productData = await page.evaluate(() => {
      const bodyText = document.body.innerText || document.body.textContent || '';

      // Extract manufacturer
      let manufacturer = 'N/A';
      const mfgPatterns = [
        /Manufacturer[\t\s]*\n+([A-Za-z][A-Za-z0-9\s&\-,.'()]+?)(?:\n|Asian Brands|$)/i,
        /Manufacturer[:\t\s]+([A-Za-z][A-Za-z0-9\s&\-,.'()]+?)(?:\t|\n|$)/i
      ];

      for (const pattern of mfgPatterns) {
        const match = bodyText.match(pattern);
        if (match) {
          manufacturer = match[1].trim();
          manufacturer = manufacturer.replace(/\s+(Asian|European|American)\s+Brands.*$/i, '').trim();
          break;
        }
      }

      // Extract MPN
      let mpn = '';
      const mpnPatterns = [
        /Mfr\.?\s*Part\s*#[:\t\s]*\n*([A-Z0-9][A-Z0-9\-_./+]+)/i,
        /Part\s*Number[:\t\s]*\n*([A-Z0-9][A-Z0-9\-_./+]+)/i,
        /MPN[:\t\s]*\n*([A-Z0-9][A-Z0-9\-_./+]+)/i
      ];

      for (const pattern of mpnPatterns) {
        const match = bodyText.match(pattern);
        if (match) {
          mpn = match[1].trim();
          break;
        }
      }

      // Extract description
      let description = 'N/A';
      const descMatch = bodyText.match(/Description[:\t\s]*\n*([^\n]{20,200})/i);
      if (descMatch) {
        description = descMatch[1].trim();
      }

      if (description === 'N/A') {
        const keyAttrMatch = bodyText.match(/Key Attributes[:\t\s]*\n*([^\n]{20,200})/i);
        if (keyAttrMatch) {
          description = keyAttrMatch[1].trim();
        }
      }

      if (description === 'N/A') {
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc && metaDesc.content) {
          description = metaDesc.content.trim();
        }
      }

      if (description === 'N/A') {
        const h1 = document.querySelector('h1');
        if (h1) {
          description = h1.textContent.trim();
        }
      }

      // Extract stock
      let stock = 'N/A';
      const stockPatterns = [
        /In[- ]?Stock:?[\t\s]*([0-9,]+)/i,
        /Stock:?[\t\s]*([0-9,]+)/i,
        /([0-9,]+)\s*(?:pcs|pieces|units)\s*(?:in|available)/i,
        /Stock\s*Qty[.:]?[\t\s]*([0-9,]+)/i,
        /Available[:\t\s]+([0-9,]+)/i
      ];

      for (const pattern of stockPatterns) {
        const match = bodyText.match(pattern);
        if (match) {
          stock = match[1].replace(/,/g, '');
          break;
        }
      }

      if (stock === 'N/A') {
        const outOfStockPatterns = [
          /out\s*of\s*stock/i,
          /sold\s*out/i,
          /unavailable/i,
          /no\s*stock/i,
          /stock:\s*0\b/i,
          /in-stock:\s*0\b/i
        ];
        for (const pattern of outOfStockPatterns) {
          if (bodyText.match(pattern)) {
            stock = '0';
            break;
          }
        }
      }

      // Extract pricing table
      const pricingRows = [];
      const priceTables = document.querySelectorAll('table');

      for (const table of priceTables) {
        const tableText = table.innerText;
        if (tableText.includes('Unit Price') || (tableText.includes('Qty') && tableText.includes('$'))) {
          const rows = table.querySelectorAll('tr');
          for (const row of rows) {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
              const qty = cells[0].textContent.trim();
              const price = cells[1].textContent.trim();

              if (qty.match(/^\d+/) && price.includes('$')) {
                pricingRows.push({
                  qty: qty,
                  unit_price: price,
                  ext_price: cells.length >= 3 ? cells[2].textContent.trim() : ''
                });
              }
            }
          }
          if (pricingRows.length > 0) break;
        }
      }

      return {
        manufacturer: manufacturer,
        mpn: mpn,
        description: description,
        stock: stock,
        pricing: pricingRows
      };
    });

    // Convert stock "N/A" to "0"
    if (productData.stock === 'N/A') {
      productData.stock = '0';
    }

    console.error(`[INFO] Found: ${productData.mpn} by ${productData.manufacturer}`);
    console.error(`[INFO] Stock: ${productData.stock}, Pricing tiers: ${productData.pricing.length}`);

    // Optional: Take screenshot
    if (args.screenshot === 'true') {
      const screenshotPath = path.join(
        config.screenshotDir,
        `${lcscCode}-${Date.now()}.png`
      );
      await page.screenshot({
        path: screenshotPath,
        fullPage: false
      });
      console.error(`[INFO] Screenshot saved: ${screenshotPath}`);
    }

    const duration = Date.now() - startTime;

    // Output structured JSON result
    const result = {
      success: true,
      data: {
        lcscCode: lcscCode,
        mpn: productData.mpn,
        manufacturer: productData.manufacturer,
        description: productData.description,
        stock: productData.stock,
        pricing: productData.pricing
      },
      metadata: {
        url: page.url(),
        timestamp: new Date().toISOString(),
        duration: duration,
        browser: 'chromium',
        screenshots: []
      }
    };

    console.log(JSON.stringify(result, null, 2));

  } catch (error) {
    console.error(`[ERROR] ${error.message}`);

    let screenshotPath = null;

    // Take screenshot on error
    if (config.screenshotOnError && page) {
      try {
        screenshotPath = path.join(
          config.screenshotDir,
          `error-${lcscCode}-${Date.now()}.png`
        );
        await page.screenshot({
          path: screenshotPath,
          fullPage: true
        });
        console.error(`[INFO] Error screenshot saved: ${screenshotPath}`);
      } catch (screenshotError) {
        console.error(`[WARN] Failed to capture screenshot: ${screenshotError.message}`);
      }
    }

    const duration = Date.now() - startTime;

    // Output error as JSON
    const errorResult = {
      success: false,
      data: null,
      metadata: {
        url: page ? page.url() : `https://www.lcsc.com/product-detail/${lcscCode}.html`,
        timestamp: new Date().toISOString(),
        duration: duration,
        browser: 'chromium'
      },
      error: {
        message: error.message,
        stack: error.stack,
        screenshot: screenshotPath
      }
    };

    console.log(JSON.stringify(errorResult, null, 2));
    process.exit(1);

  } finally {
    // Cleanup
    if (context) {
      await context.close();
    }
    if (browser) {
      await browser.close();
    }
    console.error('[INFO] Browser closed');
  }
}

// Run main function
main().catch(error => {
  console.error(`[FATAL] ${error.message}`);
  process.exit(1);
});
