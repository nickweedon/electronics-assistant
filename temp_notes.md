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
Ensure that you always pass both an output file and a log file to the script so that i can observe the progress.


Prepare to run @scripts/lcsc_add_to_cart.py to add all the items from @docs/E12_Resistors_1206_Quarter_Watt_Resistor_Kit_qty25.md to the cart.
Ensure that you pass both an output file and a log file to the script so that i can observe the progress.
Prepare necessary files but DO NOT RUN THE SCRIPT. Instead just show me the command line to run so that i can run it myself.



https://wmsc.lcsc.com/ftps/wm/product/query/list
https://wmsc.lcsc.com/ftps/wm/product/query/param/group


Read the LCSC guidlines and then find 1% alternatives to the parts in @data/E12_Resistors_1206_Quarter_Watt_Resistor_Kit_qty25.md. Create a new markdown file in the same format and the same directory that contains the full list plus the alternatives. Keep the same column structure


Read the @docs/LCSC-Guidelines.md document and create a BOM for @data/E12_Resistors_1206_Quarter_Watt_1Percent_Kit_qty100.md



uv run python scripts/lcsc_tool.py search test-data/lcsc_mpn_search.json /tmp/lcsc_mpn_search_results.json --max-concurrent 5 --limit 10

Returns the same results for each


read @docs/LCSC-Guidelines.md and search LCSC manually (no script) for arduino boards

search LCSC for arduino boards, use browser instance 4.


build out a new E24 1% 0805 resistor kit from LCSC. Also include blanks (0 ohm). Quantity is 100 but also list in the markdown document you create, the minimum order quantity. Add the markdown document to data/kits and give it a similar name format to the other kits. Rating should be quarter watt or better.


Investigate the @scripts/lcsc_tool.py check-pricing command and fix the problem where it is erroneously returning N/A for many fields such as description and manufacturer. Also ensure that any browser_wait commands are waiting on elements to appear and not always ONLY a hard coded timeout limit. Be sure though that any element that is waited on is ALWAYS rendered and that it is not just one that appears only for particular kinds of items.


Fix @data/kits/E24_Resistors_0805_Quarter_Watt_1Percent_Kit_qty100.md  and:
1) Fix any duplicate LCSC codes, remove the duplicate and find the missing item.
2) Add a new column called Quantity and set it to 100 for all items.
3) Fix any 'N/A' stock fields and either update the stock quantity or find an alternative is there is none in stock or insufficient in stock.
