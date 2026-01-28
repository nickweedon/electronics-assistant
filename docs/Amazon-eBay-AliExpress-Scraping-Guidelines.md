# Amazon, eBay, and AliExpress Web Scraping Guidelines

## Overview

This document provides specific guidance for extracting product information from Amazon, eBay, and AliExpress using Playwright MCP Server. Each site has specific DOM structures and anti-bot protections that require different approaches.

## CRITICAL: Choosing the Right Playwright Server

**For Amazon and eBay**: Always use `mcp__playwright-mcp-server__*` tools (standard sessionless server).

**For AliExpress**: Always use `mcp__playwright-real-session-mcp-server__*` tools (real user session).

### Why Different Tools?

**Amazon and eBay**:

- Standard automation works well
- No persistent CAPTCHA challenges
- Sessionless server is more efficient
- **Correct**: `mcp__playwright-mcp-server__browser_execute_bulk`
- **Wrong**: `mcp__playwright-real-session-mcp-server__browser_execute_bulk`

**AliExpress**:

- Aggressive CAPTCHA protection blocks standard automation
- Requires persistent browser session
- User must solve CAPTCHAs manually
- **Correct**: `mcp__playwright-real-session-mcp-server__browser_execute_bulk`
- **Wrong**: `mcp__playwright-mcp-server__browser_execute_bulk`

## When to Use This Guide

**MANDATORY**: Read this document whenever you need to:

- Search for products on Amazon, eBay, or AliExpress
- Extract pricing information from these sites
- Generate product links for users
- Compare prices across these platforms
- Understand the limitations and anti-bot protections of each platform

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

## AliExpress - CAPTCHA Protection Limitations

### ⚠️ CRITICAL: Automated Scraping Not Supported

**IMPORTANT**: Unlike Amazon and eBay, AliExpress has aggressive anti-bot CAPTCHA protection that **blocks all automated scraping attempts**, regardless of wait times, browser fingerprinting, or other techniques.

### What Happens When You Try to Scrape AliExpress

**Test Results** (as of 2026-01-25):

```javascript
// Both standard and real-session Playwright servers are blocked
mcp__playwright-mcp-server__browser_run_code(...)
mcp__playwright-real-session-mcp-server__browser_run_code(...)

// Result: Page redirects to CAPTCHA interception page
{
  "pageTitle": "Captcha Interception",
  "pageUrl": "https://www.aliexpress.com/.../_____tmd_____/punish?x5secdata=...",
  "resultCount": 0
}
```

**Symptoms**:

- Page URL contains `/_____tmd_____/punish?` or `/captcha`
- Page title shows "Captcha Interception"
- Zero product results found
- All selectors return empty arrays

### Why AliExpress Blocks Automation

AliExpress employs multiple anti-bot detection techniques:

1. **Browser Fingerprinting**: Detects headless browsers and automated tools
2. **Behavioral Analysis**: Monitors mouse movements, timing patterns, and interactions
3. **TLS Fingerprinting**: Analyzes encrypted connection patterns
4. **IP Reputation**: Flags traffic from data centers and VPNs
5. **Token-Based Challenges**: Requires JavaScript execution and client-side validation

**None of these can be bypassed with standard Playwright automation.**

### Real User Session Browser Approach (RECOMMENDED)

While the standard Playwright server is blocked by AliExpress, the **real-session browser** maintains a persistent, logged-in browser session that appears more like a real user and can successfully navigate AliExpress with manual CAPTCHA solving.

**Tool to Use**: `mcp__playwright-real-session-mcp-server__*` (NOT the standard `mcp__playwright-mcp-server__*`)

#### Workflow for AliExpress with Real Browser

##### Phase 1: Navigate to Search Page

```javascript
mcp__playwright-real-session-mcp-server__browser_execute_bulk(
  commands=[
    {"tool": "browser_navigate", "args": {"url": "https://www.aliexpress.com/w/wholesale-SOT-23-to-DIP-adapter-PCB.html", "silent_mode": true}},
    {"tool": "browser_wait_for", "args": {"time": 3}},
    {"tool": "browser_snapshot", "args": {"flatten": true, "limit": 100}, "return_result": true}
  ]
)
```

##### Phase 2: Handle CAPTCHA (If Present)

If the snapshot shows a CAPTCHA challenge (e.g., "Please slide to verify"), inform the user:

```
"AliExpress is showing a CAPTCHA. I can see the verification on the page. Please solve the CAPTCHA in your browser, then let me know when it's complete and I'll continue."
```

Wait for user confirmation, then check if the page loaded:

```javascript
mcp__playwright-real-session-mcp-server__browser_execute_bulk(
  commands=[
    {"tool": "browser_wait_for", "args": {"time": 2}},
    {"tool": "browser_snapshot", "args": {"flatten": true, "limit": 150}, "return_result": true}
  ],
  browser_instance="0"  // Use same instance to maintain session
)
```

##### Phase 3: Extract Data or Provide Verified URLs

Once the search results are loaded and CAPTCHA (if any) is solved, you can:

**Option A - Extract product data** (if feasible):

```javascript
mcp__playwright-real-session-mcp-server__browser_execute_bulk(
  commands=[
    {"tool": "browser_evaluate", "args": {
      "function": "() => { /* Extract product titles, prices, links based on observed DOM structure */ }"
    }, "return_result": true}
  ],
  browser_instance="0"  // Same instance
)
```

**Option B - Provide the verified working URL**:

- Confirm the search loaded successfully
- Provide the URL for user to browse manually
- URL is verified to work (not just constructed)

##### Phase 4: Additional Searches (Same Session)

For multiple search terms, navigate to each in the SAME browser session (CAPTCHAs already solved):

```javascript
mcp__playwright-real-session-mcp-server__browser_execute_bulk(
  commands=[
    {"tool": "browser_navigate", "args": {"url": "https://www.aliexpress.com/w/wholesale-TQFP-44-breakout-board.html", "silent_mode": true}},
    {"tool": "browser_wait_for", "args": {"time": 3}},
    {"tool": "browser_snapshot", "args": {"flatten": true, "limit": 100}, "return_result": true}
  ],
  browser_instance="0"  // SAME instance maintains session
)
```

#### Advantages of Real Browser Approach

- ✅ **Persistent Session**: CAPTCHA solved once, works for multiple searches
- ✅ **Direct URLs**: Can verify searches loaded and provide clean URLs
- ✅ **Session Affinity**: Using same `browser_instance` maintains login/cookies
- ✅ **User Can Assist**: User can solve CAPTCHAs when needed
- ✅ **No API Restrictions**: Can view actual rendered page
- ✅ **Works for Complex Pages**: Handles dynamic content loading

#### Disadvantages

- ❌ **Manual CAPTCHA Solving**: May require user intervention
- ❌ **No Direct Data Extraction**: Can't use `browser_evaluate` to extract JSON
- ❌ **Manual Browsing Required**: User browses links to see prices and details
- ❌ **Session Management**: Must maintain same browser instance

#### When to Use Real Browser vs Manual Approach

**ALWAYS use Real Browser Session as the PRIMARY approach**:

- Use `mcp__playwright-real-session-mcp-server__*` tools for all AliExpress searches
- Navigate to search URLs and verify they load
- User solves CAPTCHAs if/when they appear
- Once CAPTCHA is solved, session persists for multiple searches
- Provides actual search URLs that work
- Allows verification that searches return results

**Use Manual URL Provision ONLY as a fallback**:

- Only if real browser session is unavailable or broken
- Only if user explicitly requests manual URLs instead of automated navigation

### Alternative Approaches for AliExpress

If the real browser session approach is not working, you can use these fallback methods:

#### 1. Manual Search and Link Sharing

**Workflow**:

1. User opens AliExpress in their regular browser
2. Searches for product (e.g., "SOT-23 to DIP adapter PCB")
3. Copies product links from search results
4. Provides links to you for documentation

**Advantages**:

- No CAPTCHA issues
- Can see full product details, reviews, seller ratings
- Can compare multiple sellers manually
- Natural browsing experience

**URL Format**:

```
https://www.aliexpress.com/item/{ITEM_ID}.html
```

Example:

```
https://www.aliexpress.com/item/1005003084629473.html
```

#### 2. Use AliExpress Search URLs (For User Reference)

While you cannot automate the search, you can provide properly formatted search URLs for the user to open manually.

**Search URL Format**:

```
https://www.aliexpress.com/w/wholesale-{search-terms}.html
```

**Search Parameters**:

- Use hyphens (`-`) to separate words in search terms
- Optionally add sorting: `?SortType=total_tranpro_desc` (most orders)
- Optionally add price range: `&minPrice=0.5&maxPrice=5`
- Optionally add free shipping: `&isFreeShip=y`

**Examples**:

```
https://www.aliexpress.com/w/wholesale-SOT-23-to-DIP-adapter.html
https://www.aliexpress.com/w/wholesale-SMD-adapter-PCB.html
https://www.aliexpress.com/w/wholesale-TQFP-44-breakout-board.html
https://www.aliexpress.com/w/wholesale-SOT-223-adapter.html?SortType=total_tranpro_desc&isFreeShip=y
```

#### 3. Screenshot-Based Product Sharing

**Workflow**:

1. User takes screenshots of AliExpress product listings
2. Shares screenshots with you
3. You can analyze product specs, pricing visible in screenshots
4. User manually copies product links

**Use Cases**:

- Quick price comparisons when exact product specs are visible
- Reviewing seller ratings and reviews
- Checking shipping estimates

#### 4. Price Comparison When Product Found Elsewhere

**Strategy**:

- Search for the same product on Amazon, eBay, or authorized distributors first
- Document pricing from scrapable sites
- Note that AliExpress typically offers lower prices but longer shipping
- Recommend user manually check AliExpress if significant savings expected

### Search Terms for Manual AliExpress Searches

Based on the Breadboarding Adapter Kit requirements, these search terms work well on AliExpress:

| Adapter Type | Recommended Search Term | Expected Results |
| --- | --- | --- |
| SOT-23 (3-pin) | "SOT-23 to DIP adapter PCB" | PCBs, $0.20-0.50 each |
| SOT-23-6 | "SOT-23-6 adapter board" | 6-pin adapters, $0.30-0.80 each |
| SOT-223 | "SOT-223 to DIP adapter" | PCBs, $0.30-0.60 each |
| TQFP-44 | "TQFP-44 breakout board 0.8mm" | Fine-pitch adapters, $0.50-1.50 each |
| SOIC-14 | "SOIC-14 to DIP-14 adapter" | 14-pin adapters, $0.40-0.80 each |
| SOD-323/SMA | "SOD-323 adapter PCB" | Diode adapters, $0.20-0.40 each |
| Generic | "SMD to DIP adapter kit" | Mixed sets, often bulk packs |

**Tip**: Add "PCB" to searches to get blank adapters (requires soldering) vs. pre-assembled modules

### When to Recommend AliExpress

Despite automation limitations, AliExpress is still valuable for:

**Budget Electronics Projects**:

- SMD to DIP adapter boards ($0.20-1.50 vs $2.50-7.00 from Digikey)
- Bulk component kits
- Project enclosures and hardware
- Non-critical passive components

**Advantages over other platforms**:

- Significantly lower prices (often 60-80% cheaper)
- Huge selection of maker/hobbyist items
- Bulk quantities available
- Free or low-cost shipping (2-4 weeks)

**Disadvantages**:

- Long shipping times (2-6 weeks)
- No automated price checking available
- Variable quality (check seller ratings)
- Harder to get refunds/support

### Handling User Requests for AliExpress Searches

**When a user asks you to search AliExpress**:

1. **USE REAL BROWSER SESSION (PRIMARY APPROACH)**:
   - Use `mcp__playwright-real-session-mcp-server__*` tools
   - Navigate to properly formatted search URLs with sorting and free shipping filters
   - Example: `https://www.aliexpress.com/w/wholesale-SOT-23-adapter.html?SortType=total_tranpro_desc&isFreeShip=y`
   - If CAPTCHA appears, inform user and wait for them to solve it
   - Once solved, session persists for multiple searches
   - Navigate to additional search URLs using the SAME browser instance
   - Verify searches loaded and provide working URLs to user

2. **Explain what to look for**:
   - Price range expectations based on budget estimates
   - Quantity per listing (bulk packs vs individual)
   - Check seller ratings (look for 95%+ positive)
   - Read recent reviews for quality feedback
   - Verify product specifications match requirements

3. **Offer to compare with other platforms**:
   "I can also search Amazon and eBay automatically to compare pricing. Would you like me to do that?"

4. **Manual URL provision (fallback only)**:
   - Only if real browser session is unavailable/broken
   - Only if user explicitly requests URLs instead of automated navigation

### URL Construction for Manual Use

**Clean Product Link Format**:

```
https://www.aliexpress.com/item/{ITEM_ID}.html
```

**Extract Item ID from complex URLs**:

```javascript
// Full URL example:
https://www.aliexpress.com/item/32852480645.html?spm=a2g0o.productlist.main.1.2f3e7c4fHqR3Xo

// Clean URL (remove tracking):
https://www.aliexpress.com/item/32852480645.html
```

**DO NOT** include:

- `spm` parameters (tracking codes)
- `srcSns` parameters (social media tracking)
- Any other query parameters

### Future Possibilities

**Potential workarounds** (not currently implemented):

1. **AliExpress API**: Official API exists but requires business account and approval
2. **Browser Extensions**: User could use extensions to export search results
3. **RSS Feeds**: Some sellers offer product RSS feeds
4. **Mobile App**: Different protection, but still challenging to automate

**Current Status**: Manual browsing is the only reliable method.

## Common Mistakes and Solutions

1. **Insufficient Wait Times** ⚠️ MOST COMMON (Amazon/eBay): Returns empty arrays. Use combined time + text waits (see patterns above).

2. **Attempting to Scrape AliExpress** ⚠️ CRITICAL: AliExpress blocks all automation with CAPTCHA. Provide manual search URLs instead. Do NOT attempt automated scraping.

3. **Using Old eBay Selectors**: `.s-item` no longer works. Use `ul.srp-results > li.s-card` (2026 structure).

4. **Skipping Two-Phase Verification** (Amazon/eBay): Verify structure exists before extraction to distinguish selector issues from wait time problems.

5. **Including Tracking Parameters**: Amazon links expire. Use clean `/dp/{ASIN}` format. Strip eBay query params with `.split('?')[0]`. AliExpress: use `/item/{ID}.html` format.

6. **Not Handling eBay Price Ranges**: Iterate all `.s-card__price` elements: `priceEls.forEach(p => { priceText += p.textContent.trim() + ' '; })`.

7. **Parallel Search Instance Confusion** (Amazon/eBay): When running parallel searches, specify different `browser_instance` values to prevent navigation/evaluation mismatches.

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

### Amazon and eBay (Automated Scraping)

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

### AliExpress (Real Browser Session Required)

When user requests AliExpress searches:

- [ ] **CRITICAL**: ALWAYS use `mcp__playwright-real-session-mcp-server__*` tools (NOT standard playwright-mcp-server)
- [ ] **CRITICAL**: Navigate to formatted search URLs using real browser session
- [ ] Generate properly formatted search URLs with sorting and filters: `?SortType=total_tranpro_desc&isFreeShip=y`
- [ ] Navigate and wait for page load (3 seconds)
- [ ] Take snapshot to verify page loaded or if CAPTCHA present
- [ ] If CAPTCHA appears, inform user and wait for them to solve it
- [ ] Use SAME `browser_instance` for multiple searches to maintain session
- [ ] Provide verified working URLs to user for manual browsing
- [ ] Suggest search terms based on product requirements
- [ ] Offer to search Amazon/eBay automatically for comparison
- [ ] If user provides links, clean tracking parameters: `https://www.aliexpress.com/item/{ID}.html`
- [ ] Set realistic price expectations (60-80% cheaper but 2-6 weeks shipping)
- [ ] Recommend checking seller ratings (95%+ positive)
- [ ] Note that AliExpress is best for budget projects, not time-sensitive needs

