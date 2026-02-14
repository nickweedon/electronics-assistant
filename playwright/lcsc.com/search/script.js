#!/usr/bin/env node

/**
 * LCSC Catalog Search
 * Search LCSC catalog by keywords with pagination support
 *
 * Parameters:
 * - keywords: Search query term (required)
 * - maxResults: Maximum number of results to return (default: 100)
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

const keywords = args.keywords || '';
const maxResults = parseInt(args.maxResults) || 100;
const headless = args.headless !== 'false';
const timeout = parseInt(args.timeout) || 10000;

if (!keywords) {
  console.error('[ERROR] keywords parameter is required');
  console.error('Usage: node script.js --keywords="1206 resistor 10k" [--maxResults=100] [--headless=true]');
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
 * Extract products from current page
 */
async function extractCurrentPage(page) {
  return await page.evaluate(() => {
    const productLinks = document.querySelectorAll('a[href*="/product-detail/C"]');
    let pageProducts = [];

    productLinks.forEach((link) => {
      const productUrl = link.href;
      const productCode = productUrl.match(/C\d+/)?.[0];
      if (!productCode) return;

      let mpn = link.textContent?.trim();
      const row = link.closest('tr');
      let manufacturer = '';
      let description = '';
      let stock = '';
      let price = '';

      if (row) {
        const mfgLink = row.querySelector('a[href*="/brand-detail/"]');
        if (mfgLink) manufacturer = mfgLink.textContent?.trim();

        const stockButtons = row.querySelectorAll('button');
        for (const btn of stockButtons) {
          const text = btn.textContent?.trim();
          if (text && text.match(/^[\d,]+$/)) {
            stock = text.replace(/,/g, '');
            break;
          }
        }

        const cells = row.querySelectorAll('td');
        for (const cell of cells) {
          const text = cell.textContent?.trim();
          if (text && text.length > 30 && (text.includes('Ω') || text.includes('Resistor') || text.includes('Capacitor'))) {
            description = text;
            break;
          }
        }

        const priceRows = row.querySelectorAll('table tr');
        for (const priceRow of priceRows) {
          const priceCells = priceRow.querySelectorAll('td');
          if (priceCells.length >= 2) {
            const priceText = priceCells[1].textContent?.trim();
            if (priceText && priceText.startsWith('$')) {
              price = priceText;
              break;
            }
          }
        }
      }

      pageProducts.push({
        mpn,
        lcscCode: productCode,
        manufacturer,
        description,
        stock,
        price,
        productUrl
      });
    });

    return pageProducts;
  });
}

/**
 * Click next page button and wait
 */
async function goToNextPage(page) {
  try {
    const hasNext = await page.evaluate(() => {
      const currentActive = document.querySelector('button.v-pagination__item--active');
      if (!currentActive) return false;
      const currentPage = parseInt(currentActive.textContent.trim());

      const nextButtons = Array.from(document.querySelectorAll('button.v-pagination__item')).filter(btn => {
        const btnPage = parseInt(btn.textContent.trim());
        return btnPage === currentPage + 1;
      });

      if (nextButtons.length > 0) {
        nextButtons[0].click();
        return true;
      }
      return false;
    });

    if (hasNext) {
      await page.waitForTimeout(3000);
      return true;
    }
    return false;
  } catch (e) {
    return false;
  }
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
    console.error(`[INFO] Searching LCSC for "${keywords}"...`);

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

    // Navigate to search page
    const searchUrl = `https://www.lcsc.com/search?q=${encodeURIComponent(keywords)}`;
    console.error(`[INFO] Navigating to ${searchUrl}...`);
    await page.goto(searchUrl, {
      waitUntil: 'domcontentloaded',
      timeout: config.timeout
    });

    // Wait for page to load
    await page.waitForTimeout(5000);

    // Extract products with pagination
    console.error(`[INFO] Extracting products (max: ${maxResults})...`);
    const allProducts = [];
    const seen = new Set();

    // Extract first page
    let pageProducts = await extractCurrentPage(page);

    // Deduplicate
    for (const product of pageProducts) {
      if (!seen.has(product.lcscCode)) {
        seen.add(product.lcscCode);
        allProducts.push(product);
      }
    }

    console.error(`[INFO] Page 1: Found ${pageProducts.length} products (total: ${allProducts.length})`);

    // Keep paginating while we have products and haven't hit limit
    let pageCount = 1;
    while (allProducts.length < maxResults && pageCount < 200) {
      const hasNext = await goToNextPage(page);
      if (!hasNext) break;

      pageProducts = await extractCurrentPage(page);
      if (pageProducts.length === 0) break;

      // Deduplicate
      for (const product of pageProducts) {
        if (!seen.has(product.lcscCode)) {
          seen.add(product.lcscCode);
          allProducts.push(product);
          if (allProducts.length >= maxResults) break;
        }
      }

      pageCount++;
      console.error(`[INFO] Page ${pageCount}: Found ${pageProducts.length} products (total: ${allProducts.length})`);
    }

    // Trim to limit
    const results = allProducts.slice(0, maxResults);
    console.error(`[INFO] Search complete: ${results.length} products`)

    // Optional: Take screenshot of results
    if (args.screenshot === 'true') {
      const screenshotPath = path.join(
        config.screenshotDir,
        `results-${Date.now()}.png`
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
        keywords: keywords,
        total_found: results.length,
        products: results
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
          `error-${Date.now()}.png`
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
        url: page ? page.url() : `https://www.lcsc.com/search?q=${encodeURIComponent(keywords)}`,
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
