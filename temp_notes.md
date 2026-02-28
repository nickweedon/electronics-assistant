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


Fix @data/kits/E24_Resistors_0805_Quarter_Watt_1Percent_Kit_qty100.md  and:
1) Fix any duplicate LCSC codes, remove the duplicate and find the missing item.
2) Fix any 'N/A' stock fields and either update the stock quantity or find an alternative is there is none in stock or insufficient in stock.


Search for the items recommended from aliexpress. Do some analysis and provide a list of links to specific items that you recommend.


/create-skill Create a new local skill called 'lcsc-supplier' that should be invoked whenever interaction is needed with the LCSC electronics supplier. This skill should ALWAYS also trigger the 'playwright' skill. The behavior of this skill should be taken from the existing instructions in this projects CLAUDE.md file and its pertinent linked documents. We are essentially turning this existing CLAUDE.md based behavior into a skill.
One caveat however is that will no longer be using scripts/lcsc_tool.py as it has now been deprecated in favor of 


Do a price check at LCSC on the first ten of the items in @data/kits/E24_Capacitors_Mixed_10pF_470uF_25V-100V_5pct_qty25-100.md 

Do a price check at LCSC on the first ten of the items in this file




So don't respond or do anything yet and DO NOT activate and skills but i'm just telling you that i am curious about how elephants talk.  

Alright, lets do it now!



Don't do anything yet but just letting you know i really like flowers. 


/elephant-talk Hello there my elephant!


  Invoke the skill-maintenance-context skill before doing anything else. I want to create a new skill based around the API that the Digikey MCP server uses but i DO NOT WANT to use the
   Digikey MCP server. Instead I would like you to understand the Digikey MCP server source code at           
  ../digikey_mcp and create individual parameterized python scripts that call the API. You should also consider  
  using handlebars templates if there are cases where code fragments could be useful for this skill (like when    
  perform macro level tasks involving multiple API calls). If you do not see any immediate such use cases though
  then it is better to not create any .hbs files yet as these can be added later.


  use playwright to list my aliexpress orders at                                                                                      
  https://www.aliexpress.com/p/order/index.html?spm=a2g0o.home.headerAcount.2.468a6278jHGmO5&_gl=1*3yzwja*_gcl_au*ODEwODkyODQ1LjE     
  3NjkzOTMwNzQ.*_ga*MTM4MDAxNjkwMS4xNzcwMTc1ODQ3*_ga_VED1YSGNC7*czE3NzExODczMzUkbzIkZzAkdDE3NzExODczMzUkajYwJGwwJGgw                  




I need you to now update the partsbox skill so that when receiving stock, the same format and style is used when adding items                                                                                              


Update the items in this table in the md in partsbox but uploading the image from each items corresponding aliexpress item. Skip the first one since it has already been uploaded


can you add a new column to this table that is the thumbnail image of the item? 


/playwright Create two re-usable actions:
1) List all LCSC orders
2) List the items within an LCSC order

Create these as separate actions to maximize re-usablility 


node scripts-temp/playwright/www.lcsc.com/list-order-items/script.js --orderId=WM2601260050


You made a number of significant improvements to the script writing process during    
  this session, especially the use of the X11 message to ask me to do things during      /clear
  script development and selector exploration. I would like to actually always have the  
  script development and selector exploration phase always use headed mode as it is      
  good to watch and see how it progresses.                                               
  Can you update the playwright script to incorporate these improvements as well as any  
  other improvements you noted.    


  Modify the playwright skill to add these additional instructions when building a     
  login screen:                                                                          
  1) Always take the user to the actual login screen, don't make the user have to click  
  the login button.                                                                      
  2)                                                                                     
    A) Always have scripts automatically detect when not logged in                       
    B) Launch the login process (should be a separate action to maximize re-used) in     
  headed mode                                                                            
    C) Detect when the user has logged in                                                
    D) Go back into headless mode and complete the original action 



  
  I want to look at replacing our semi-persistant browser and http server with instead using tmux with node.js REPL. The idea     
  would be that we would run the the existing action script we are working on via node REPL through tmux and then be able to      
  incrementally execute code to manipulate the browser. Can you use 'thunderstore.io' as an example and create a script that      
  locates the 5 most popular valheim plugins and list them.         