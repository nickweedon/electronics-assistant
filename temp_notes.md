use the playwright extension MCP server to tell me what my first gmail email is (the most recent one). Do not failover to the regular MCP server if this one appears to not be working.
Do not use bulk operations and do not use the 'wait_for' tools (wait manually instead but don't call the tool for this). Always use a limit of 25 for pageable operations.

use the playwright extension MCP server to do a google search on 'blah' and tell me the first result. Do not failover to the regular MCP server if this one appears to not be working.


use the playwright MCP server to tell me what my first gmail email is (the most recent one). Do not failover to the regular MCP server if this one appears to not be working.
Do not use bulk operations


Use the playwright MCP to navigate to gmail. Set the limit to 5 and result type to JSON.



Use playwright to do an amazon search for gloves and describe to me the first entry. Use flatten mode with pagination and a limit of 500.



Use playwright to do an amazon search for gloves and describe to me the first entry.
Follow these steps for efficient searching:
1) Call browser_navigate to the URL with silent_mode: true.
2) Call browser_wait_for to wait for the page to fully load (use a sensible timeout)
3) Run browser_evaluate to extract the data.


Use playwright to do an amazon search for gloves and describe to me the first entry.

Use playwright to do an amazon search for gloves and describe to me first 5 entries.



Use playwright to do an amazon search for gloves and describe to me first 5 entries. Start navigation from the Amazon home page as to avoid bot detection.
Once complete, show me the image for the first item using xdg-open.


Pull back the prices and MOQ from LCSC for all of the items in @docs/E12_Resistors_1206_Quarter_Watt_Resistor_Kit_qty25.md. Once you have the list, check it against the markdown document and report and update any discrepencies.


Carry on with running @scripts/lcsc_add_to_cart.py to add all the items from @docs/E12_Resistors_1206_Quarter_Watt_Resistor_Kit_qty25.md to the cart. Start with just 2 or 3 items to test that it works first.
The was previously an issue where blank tabs were appearing but i have made some configuration changes that hopefully now address this.