# Playwright MCP Server Guidelines

## Server Selection

**DEFAULT:** Always use `playwright-mcp-server` for all browser automation tasks.

**EXCEPTION:** Only use `playwright-real-session-mcp-server` when the user explicitly requests it (phrases like "use a real browser session").

**ON FAILURE:** If the standard server fails (bot detection, access denied, timeout, etc.):
1. Report the failure and explain what went wrong
2. Ask if they want to try the real session server
3. Wait for explicit permission before switching
4. **NEVER** auto-failover to the real session server

## Browser Automation Settings

When calling `browser_snapshot` or `browser_navigate`:
- Use `flatten: true` by default
- Use `limit: 150` by default
- After seeing initial results, decide whether to page through more results or construct a JMESPath query

## Efficient Searching Steps

Follow these steps for efficient searching:

1. **Navigate**: Call `browser_navigate` to the URL with `silent_mode: true`.

2. **Explore**: Call `browser_snapshot` with flatten mode true and limit 150 to explore the data structure:
   - Start at offset 0
   - Look for the ACTUAL CONTENT you're searching for (e.g., product listings, search results, data tables)
   - **DO NOT assume the first 150 items contain what you need** - navigation, headers, and UI elements often come first
   - Continue paging (offset 150, 300, 450, etc.) until you find at least 2-3 examples of the target content
   - Examine the structure: role, name, depth, parent_role, and any other attributes

3. **Extract**: Only AFTER finding actual examples of the target content, construct and run a `browser_snapshot` call using a JMESPath query based on the observed structure.

**CRITICAL**:
- Step 2 is EXPLORATION - you must page until you find the content you're looking for
- Step 3 is EXTRACTION - you must base your query on what you actually observed, not assumptions
- If you attempt a JMESPath query without having observed the target content structure first, you are doing it wrong

## JMESPath Queries

When using any tool that supports JMESPath queries, follow the guidelines in [Using JMESPath](Using-JMESPath.md).

## Web Search Fallback

If you suspect, after doing a standard 'Web Search' or 'Web Fetch', that there may be additional important information that is only visible or navigable via a single page web application, then use the Playwright MCP server to check for this and navigate accordingly.
