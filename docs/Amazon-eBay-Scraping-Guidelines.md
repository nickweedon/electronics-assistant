# Amazon and eBay Web Scraping Guidelines

## Overview

This document provides specific guidance for extracting product information from Amazon and eBay using Playwright MCP Server. Both sites have specific DOM structures that require precise selectors.

## CRITICAL: Use Standard Playwright MCP Server

**IMPORTANT**: Always use `mcp__playwright-mcp-server__*` tools for Amazon and eBay scraping, NOT `mcp__playwright-real-session-mcp-server__*` tools.

The real-session server is designed for interactive browser sessions and does not work reliably for automated scraping workflows. Use the standard sessionless Playwright server which is optimized for automation.

**Correct tool prefix**: `mcp__playwright-mcp-server__browser_execute_bulk`
**Wrong tool prefix**: `mcp__playwright-real-session-mcp-server__browser_execute_bulk`

## When to Use This Guide

**MANDATORY**: Read this document whenever you need to:

- Search for products on Amazon or eBay
- Extract pricing information from these sites
- Generate product links for users
- Compare prices across these platforms

## CRITICAL: Wait Times and Dynamic Content Loading

### Why Wait Times Are Essential

**MOST IMPORTANT RULE**: Both Amazon and eBay load search results dynamically via JavaScript/AJAX **after** the initial page load completes. Even when `document.readyState === "complete"`, the search results may not yet be in the DOM.

**Consequence of insufficient waits**: Your extraction will return empty arrays (`[]`) even though the selectors are correct and the page appears loaded.

### Required Wait Strategy

Use **both** time-based delays AND text-based waits for maximum reliability:

1. **Add a safety margin** with `browser_wait_for` time delay (3-4 seconds)
2. **Wait for specific text** that always appears in search results (e.g., "results")

This dual approach handles both slow page loads and ensures the dynamic content has rendered.

**IMPORTANT**: The `browser_wait_for` API supports:

- `time`: Seconds to wait
- `text`: Text string to wait for
- `textGone`: Text to wait for to disappear

It does **NOT** support `element` or `selector` parameters.

### Wait Times by Site

Based on extensive testing under various network conditions:

- **Amazon**: 4-5 second time delay + wait for search results container
- **eBay**: 3-4 second time delay + wait for search results container

### Incorrect vs Correct Patterns

❌ **WRONG - Insufficient waits**:

```javascript
// No wait - returns [] empty array
browser_execute_bulk([
  {"tool": "browser_navigate", "args": {"url": "...", "silent_mode": true}},
  {"tool": "browser_evaluate", ...}
])

// Time-only wait - fragile, may return [] under slow connections
browser_execute_bulk([
  {"tool": "browser_navigate", "args": {"url": "...", "silent_mode": true}},
  {"tool": "browser_wait_for", "args": {"time": 2}},
  {"tool": "browser_evaluate", ...}
])
```

✅ **CORRECT - Combined time + text wait**:

```javascript
browser_execute_bulk([
  {"tool": "browser_navigate", "args": {"url": "...", "silent_mode": true}},
  {"tool": "browser_wait_for", "args": {"time": 4}},        // Time margin (4s Amazon, 3s eBay)
  {"tool": "browser_wait_for", "args": {"text": "results"}}, // Wait for content
  {"tool": "browser_evaluate", ...}
])
```

This combined approach provides a time baseline plus guarantees content is visible.

## MANDATORY: Two-Phase Extraction Approach

**NEVER** write extraction code without first verifying the page structure. This two-phase approach is **REQUIRED**, not optional.

### Phase 1: Navigate, Wait, and Verify Structure

Before attempting any data extraction, verify that:

1. The page loaded successfully
2. The wait strategy was sufficient
3. Results are present in the DOM

**Amazon verification**:

```javascript
browser_execute_bulk([
  {"tool": "browser_navigate", "args": {"url": "https://www.amazon.com/s?k=YOUR_SEARCH", "silent_mode": true}},
  {"tool": "browser_wait_for", "args": {"time": 4}},  // Time margin
  {"tool": "browser_wait_for", "args": {"text": "results"}},  // Text wait
  {"tool": "browser_evaluate", "args": {
    "function": "() => { return { resultCount: document.querySelectorAll('[data-component-type=\"s-search-result\"]').length, readyState: document.readyState, sampleHTML: document.querySelector('[data-component-type=\"s-search-result\"]')?.outerHTML.substring(0, 500) }; }"
  }, "return_result": true}
])
```

**Expected**: `resultCount` should be > 0 (typically 20-60). If 0, the text wait would have failed first.

**eBay verification**:

```javascript
browser_execute_bulk([
  {"tool": "browser_navigate", "args": {"url": "https://www.ebay.com/sch/i.html?_nkw=YOUR_SEARCH&_sop=15", "silent_mode": true}},
  {"tool": "browser_wait_for", "args": {"time": 3}},  // Time margin
  {"tool": "browser_wait_for", "args": {"text": "results"}},  // Text wait
  {"tool": "browser_evaluate", "args": {
    "function": "() => { return { resultCount: document.querySelectorAll('ul.srp-results > li.s-card').length, readyState: document.readyState, sampleHTML: document.querySelector('.s-card')?.outerHTML.substring(0, 500) }; }"
  }, "return_result": true}
])
```

**Expected**: `resultCount` should be > 0 (typically 20-60). If 0, the text wait would have failed first.

### Phase 2: Extract Data (Only After Verification)

Only after confirming results are present should you proceed with full data extraction using the patterns documented below.

## Amazon Scraping

### DOM Structure

Amazon search results use the following structure:

```html
<div data-component-type="s-search-result" data-asin="B0787166LX">
  <h2>
    <a href="/dp/B0787166LX/...">
      <span>Product Title</span>
    </a>
  </h2>
  <span class="a-price">
    <span class="a-offscreen">$32.99</span>
  </span>
</div>
```

### Correct Selectors

#### Product Items

```javascript
document.querySelectorAll('[data-component-type="s-search-result"]')
```

#### Product Title

```javascript
item.querySelector('h2 span')?.textContent
```

#### Product Price

```javascript
item.querySelector('.a-price .a-offscreen')?.textContent
```

**Note**: Always use `.a-offscreen` for price, not the visible price element, as it contains the clean formatted price.

#### Product ASIN

```javascript
item.getAttribute('data-asin')
```

### Creating Amazon Links

**CRITICAL**: Do NOT use the full href from anchor tags. These contain tracking parameters and session tokens that expire.

#### ✅ CORRECT - Clean Link Format

```javascript
const asin = item.getAttribute('data-asin');
const cleanLink = `https://www.amazon.com/dp/${asin}`;
```

#### ❌ INCORRECT - Using Full href

```javascript
// This creates garbage links with expired session tokens
const badLink = item.querySelector('a')?.href;
```

### Complete Amazon Extraction Example

```javascript
() => {
  const products = [];
  const items = document.querySelectorAll('[data-component-type="s-search-result"]');

  items.forEach((item, i) => {
    if (i < 15) {  // Limit results
      const titleEl = item.querySelector('h2 span');
      const priceEl = item.querySelector('.a-price .a-offscreen');
      const asin = item.getAttribute('data-asin');

      if (titleEl && priceEl && asin) {
        products.push({
          title: titleEl.textContent.trim(),
          price: priceEl.textContent.trim(),
          link: `https://www.amazon.com/dp/${asin}`
        });
      }
    }
  });

  return products;
}
```

## eBay Scraping

### DOM Structure Changes (2026)

**IMPORTANT**: eBay updated their HTML structure. The old `.s-item` class no longer works.

**New Structure** (as of 2026):

```html
<ul class="srp-results">
  <li class="s-card s-card--horizontal s-card--dark-solt-links-blue">
    <div class="s-card__title">Product Title</div>
    <span class="su-styled-text s-card__price">$7.99</span>
    <a class="s-card__link" href="https://www.ebay.com/itm/224679543111">
  </li>
</ul>
```

### Correct Selectors

#### Product Items

```javascript
document.querySelectorAll('ul.srp-results > li.s-card')
```

**OLD (broken)**: `document.querySelectorAll('.s-item')` - DO NOT USE

#### Product Title

```javascript
item.querySelector('.s-card__title')?.textContent
```

#### Product Price

eBay displays prices using multiple spans for price ranges:

```javascript
const priceEls = item.querySelectorAll('.s-card__price');
let priceText = '';
priceEls.forEach(p => {
  priceText += p.textContent.trim() + ' ';
});
```

This handles both single prices ("$7.99") and ranges ("$2.35 to $6.51").

#### Product Link

```javascript
const linkEl = item.querySelector('.s-card__link');
const cleanLink = linkEl ? linkEl.href.split('?')[0] : '';
```

**Note**: Split on `?` to remove tracking parameters.

#### Shipping Information

```javascript
const shippingEl = item.querySelector('[class*="shipping"]');
const shipping = shippingEl ? shippingEl.textContent.trim() : 'Not listed';
```

### Complete eBay Extraction Example

```javascript
() => {
  const products = [];
  const items = document.querySelectorAll('ul.srp-results > li.s-card');

  items.forEach((item, i) => {
    if (i < 20) {  // Limit results
      const titleEl = item.querySelector('.s-card__title');
      const priceEls = item.querySelectorAll('.s-card__price');
      const linkEl = item.querySelector('.s-card__link');
      const shippingEl = item.querySelector('[class*="shipping"]');

      if (titleEl && priceEls.length > 0) {
        let priceText = '';
        priceEls.forEach(p => {
          priceText += p.textContent.trim() + ' ';
        });

        products.push({
          title: titleEl.textContent.trim(),
          price: priceText.trim(),
          shipping: shippingEl ? shippingEl.textContent.trim() : 'Not listed',
          link: linkEl ? linkEl.href.split('?')[0] : ''
        });
      }
    }
  });

  return products;
}
```

## Common Mistakes and Solutions

1. **Insufficient Wait Times** ⚠️ MOST COMMON: Returns empty arrays. Use combined time + text waits (see patterns above).

2. **Using Old eBay Selectors**: `.s-item` no longer works. Use `ul.srp-results > li.s-card` (2026 structure).

3. **Skipping Two-Phase Verification**: Verify structure exists before extraction to distinguish selector issues from wait time problems.

4. **Including Tracking Parameters**: Amazon links expire. Use clean `/dp/{ASIN}` format. Strip eBay query params with `.split('?')[0]`.

5. **Not Handling eBay Price Ranges**: Iterate all `.s-card__price` elements: `priceEls.forEach(p => { priceText += p.textContent.trim() + ' '; })`.

6. **Parallel Search Instance Confusion**: When running parallel searches, specify different `browser_instance` values to prevent navigation/evaluation mismatches.

## URL Construction for Searches

### Amazon Search URL

```
https://www.amazon.com/s?k={search_terms}
```

Example:

```
https://www.amazon.com/s?k=SMD+storage+box+anti-static
```

### eBay Search URL

```
https://www.ebay.com/sch/i.html?_nkw={search_terms}&_sop=15
```

- `_nkw`: Search keywords (use `+` for spaces)
- `_sop=15`: Sort by "Price + Shipping: lowest first"

Example:

```
https://www.ebay.com/sch/i.html?_nkw=SMD+storage+box+anti-static&_sop=15
```

## Debugging Empty Results

If extraction returns `[]`:

1. **Check wait times**: Test with longer waits (5+ seconds). If `count` increases, wait time was insufficient.
2. **Verify selectors**: Check `itemCount` and `sampleHTML`:
   - `itemCount: 0` + `readyState: "complete"` → Increase wait time or add text wait
   - `itemCount: 0` + no HTML sample → Wrong selector or page structure changed
   - `itemCount: 20+` → Selectors work, issue is in extraction logic
3. **Validate links**: Clean format required (no tracking params):
   - ✅ Amazon: `https://www.amazon.com/dp/{ASIN}`
   - ✅ eBay: `https://www.ebay.com/itm/{ID}`

## Parallel Searches

For simultaneous Amazon + eBay searches, specify different browser instances to prevent confusion:

```javascript
browser_execute_bulk(commands=[...amazon...], browser_instance="0")
browser_execute_bulk(commands=[...ebay...], browser_instance="1")
```

Without explicit instances, navigation/evaluation may target wrong pages.

## Summary Checklist

Before extracting from Amazon or eBay:

- [ ] **CRITICAL**: Include time-based wait (3-4 seconds) after navigation
- [ ] **CRITICAL**: Include text-based wait for "results" to appear
- [ ] **CRITICAL**: When running parallel searches, specify explicit `browser_instance` values
- [ ] Follow two-phase approach: verify structure first, then extract
- [ ] Use correct selectors (`.s-card` for eBay, `[data-component-type="s-search-result"]` for Amazon)
- [ ] Extract ASIN from Amazon items
- [ ] Build clean links without tracking parameters (no session tokens, no query params)
- [ ] Handle eBay price ranges (multiple `.s-card__price` spans)
- [ ] Strip query parameters from eBay links (`.split('?')[0]`)
- [ ] Use `silent_mode: true` for navigation
- [ ] Limit results to 15-20 items to avoid overwhelming context
- [ ] Validate links before presenting to user

**Priority order**: Wait strategy (#1-2) is most important. Incorrect waits cause empty results even with perfect selectors.

## Version History

- **2026-01-25 (v3)**: Corrected wait strategy to use text-based waits (actual API), added browser_instance requirement for parallel searches
- **2026-01-25 (v2)**: Added critical wait time requirements, mandatory two-phase approach, combined wait strategy, comprehensive troubleshooting
- **2026-01-25 (v1)**: Initial version documenting eBay structure changes and Amazon ASIN-based linking
