#!/usr/bin/env python3
"""
Extract LCSC product codes by searching for MPNs on LCSC.com
"""

import asyncio
import re
from playwright.async_api import async_playwright

# Test with first 5 MPNs from the document
TEST_MPNS = [
    "CC0805JRNPO9BN100",  # 10pF - known to be C107107
    "C0805C100J5GACTU",   # 10pF KEMET
    "CC0805JRNPO9BN120",  # 12pF
    "CC0805JRNPO9BN150",  # 15pF
    "CC0805JRNPO9BN180",  # 18pF
]

async def extract_lcsc_product_code(page, mpn):
    """
    Search LCSC for an MPN and extract the product code from the URL

    Args:
        page: Playwright page object
        mpn: Manufacturer Part Number to search for

    Returns:
        Product code (e.g., "C107107") or None if not found
    """
    try:
        # Navigate to LCSC search
        search_url = f"https://www.lcsc.com/search?q={mpn}"
        print(f"\nSearching for: {mpn}")
        print(f"URL: {search_url}")

        await page.goto(search_url, wait_until="networkidle", timeout=30000)

        # Wait a bit for dynamic content to load
        await page.wait_for_timeout(2000)

        # Look for product links - LCSC uses various formats
        # Try to find the first product result link
        # Pattern: /product-detail/.*_C\d+\.html

        # Method 1: Look for product detail links
        product_links = await page.locator('a[href*="/product-detail/"]').all()

        for link in product_links[:3]:  # Check first 3 results
            href = await link.get_attribute('href')
            if href:
                # Extract product code from URL
                # Format: /product-detail/DESCRIPTION_C123456.html
                match = re.search(r'_(C\d+)\.html', href)
                if match:
                    product_code = match.group(1)
                    print(f"  Found: {product_code}")
                    print(f"  URL: https://www.lcsc.com{href}")
                    return product_code

        # Method 2: Try alternative link format
        product_links = await page.locator('a[href*="_C"]').all()
        for link in product_links[:3]:
            href = await link.get_attribute('href')
            if href:
                match = re.search(r'_(C\d+)', href)
                if match:
                    product_code = match.group(1)
                    print(f"  Found (alt): {product_code}")
                    return product_code

        print(f"  ❌ No product code found for {mpn}")
        return None

    except Exception as e:
        print(f"  ❌ Error searching for {mpn}: {str(e)}")
        return None

async def main():
    """Main function to test LCSC product code extraction"""

    print("=" * 60)
    print("LCSC Product Code Extraction Test")
    print("=" * 60)

    results = {}

    async with async_playwright() as p:
        # Launch browser (headless for efficiency)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Process each test MPN
        for mpn in TEST_MPNS:
            product_code = await extract_lcsc_product_code(page, mpn)
            results[mpn] = product_code

            # Be nice to the server
            await page.wait_for_timeout(1000)

        await browser.close()

    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for mpn, code in results.items():
        if code:
            url = f"https://www.lcsc.com/product-detail/{code}.html"
            print(f"✅ {mpn:30s} -> {code:10s} -> {url}")
        else:
            print(f"❌ {mpn:30s} -> NOT FOUND")

    print("\n" + "=" * 60)
    success_rate = len([c for c in results.values() if c]) / len(results) * 100
    print(f"Success Rate: {success_rate:.0f}% ({len([c for c in results.values() if c])}/{len(results)})")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
