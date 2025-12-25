# **Digikey MCP Server Guidelines**

# **Digikey MCP Server Usage**

## **General Rules**

* Do not search the Digikey website unless explicitly asked to.
* Do not create BOM CSV files unless explicitly asked to. Always favor using the Digikey MyLists API.
* Only create lists after explicit user request or confirmation.
* When calling API methods that allow retrieval limits to be applied (such as get\_parts\_by\_list\_id), stick to small batches of no greater than 200 at a time to limit the amount of memory usage and increase performance.
* If you know that the amount of data that will be returned is likely large based on the requested JMESPath then limit the response to small chunks if limiting is available.
* Always display a short high level summary (500 words max) of any BOM that is created. This summary should include:
  * Total cost
  * Total part count
  * List values for each decade (when creating component lists)
  * Note any items that are invalid based on the 'Part Verification Steps' section below.

## **Part Verification Steps**

When generating lists of components, for each part it always performs a live check on the Digi-Key website to:

* Confirm the part exists and has a valid Digi-Key part number.
* Verify the part is in stock and that the stock levels satisfy the requested quantity. No back-ordering is acceptable; the available quantity must be greater than or equal to the requested quantity right now.
* Ensure the part is not discontinued.
* Confirm that the Minimum Order Quantity (MOQ) is less than or equal to the requested quantity.
* Do not modify the requested quantity in order to satisfy the MOQ or stock level. Instead look for an alternative part.
* If any parts do not exist or cannot be ordered due to lack of stock or not meeting MOQ then clearly list these parts and the reason that they could not be added to the order.

## **Pricing Guidance**

* Always remember to use the correct price for an item based upon the quantity ordered.
* Always use the cheapest packaging. It does not matter what the packaging is but if you must choose then pick 'Cut Tape' if the price is the same.

## **Authentication Requirements**

* When making any MyLists related calls, call oauth\_start\_login unless the user is already authenticated. Wait for the user to report back to you that they have done this before calling oauth\_complete\_login.
* Authentication status can be checked with oauth\_status
* The auth\_code should not need to be refreshed.
* The user\_token will automatically be refreshed by the API calls if it is seen to be expired. If you expect this is not happening then you can still call oauth\_refresh.

## **List Management**

* Always update the existing list that has been recently mentioned unless asked to create a new list.
* Always ask before modifying any list, including:
  * Adding parts
  * Deleting parts
  * Deleting the list

## **Component Kit Building Rules**

When generating component kits that intentionally cover a range of values (such as a desktop repair component kit):

* If any of the following is not specified then prompt the user:
  * Value count per decade
  * Quantity per value
  * Tolerance
* If package size is not specified then default to 0805\.
* When selecting values across a range, follow commonly used conventions such as E-series subsets (e.g., E6 or E12) and ensure the full range is covered.
* Optimize for low cost and availability.
* Consider using the search\_product\_substitutions tool method when you need to find product alternatives.
* When creating component kits/lists, store the value type in the customer reference field (e.g. for resistors, 2K3, 10K etc).

## **E-Series Example:**

* E6 series: 6 values per decade (10, 15, 22, 33, 47, 68\)
* E12 series: 12 values per decade (10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82\)
