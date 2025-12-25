# **Using JMESPath**

# **Using JMESPath**

## **Important General Usage Notes**

### **Use of forward slashes**

**CRITICAL SYNTAX NOTE:** Field names contain '/' characters (e.g., "part/name").
You MUST use DOUBLE QUOTES for field identifiers, NOT backticks:

* **CORRECT:** "part/name", "part/tags", "part/mpn"
* **WRONG:** \`part/name\` (backticks create literal strings, not field references)

Using backticks will silently fail \- queries will return empty results because
\`part/tags\` evaluates to the literal string "part/tags", not the field value.

Standard JMESPath examples:

* "[\?\\\"part/manufacturer\\\" \== 'Texas Instruments'\]" \- filter by manufacturer
* "[\?contains(\\\"part/tags\\\", 'resistor')\]" \- filter by tag
* "sort\_by(@, &\\\"part/name\\\")" \- sort by name
* "[\*\].{id: \\\"part/id\\\", name: \\\"part/name\\\"}" \- projection with field access

Custom functions available:

* nvl(value, default): Returns default if value is null
* int(value): Convert to integer (returns null on failure)
* str(value): Convert to string
* regex\_replace(pattern, replacement, value): Regex substitution

**IMPORTANT:** Use nvl() for safe filtering on nullable fields to avoid errors:

* "[\?contains(nvl(\\\"part/name\\\", ''), 'resistor')\]" \- safe name search
* "[\?contains(nvl(\\\"part/description\\\", ''), 'SMD')\]" \- safe description search
* "[\?contains(nvl(\\\"part/mpn\\\", ''), 'RC0805')\]" \- safe MPN search

#

### **Literal Syntax for nvl() Default Values**

When using the nvl() function with array or object default values, you MUST use backticks to create literal values. This is a critical JMESPath syntax requirement. For empty arrays, use backticks:

* **CORRECT:** nvl("field", \\\[\]\`)\`
* **WRONG:** nvl("field", \[\]) \- this evaluates to null, not an empty array\!

For empty objects, use backticks:

* CORRECT: nvl("field", \\\{}\`)\`
* WRONG: nvl("field", {}) \- this is invalid syntax

For empty strings, use single quotes:

* CORRECT: nvl("field", '')

For numbers, use backticks:

* CORRECT: nvl("field", \\\`0\`)\`

## **Common mistake: Using nvl("part/tags", \[\]) instead of nvl("part/tags", \\\[\]\`). The unquoted \[\]\` is interpreted as a JMESPath flatten/multi-select expression that evaluates to null, not as an empty array literal. This causes the error: "invalid type for value: None, expected one of: \['string', 'number', 'boolean', 'array', 'object'\], received: "null"". Rule of thumb: For nvl() defaults, use single quotes for strings ('') and backticks for arrays, objects, and numbers (\[\], {}, 0).How to query when JMESPath is available**

#

When searching for items, always try to perform broad keyword searches and use JMESPath to perform filtering such as filtering out items with 'no stock availability' and use the advice in the "Filtering Components by Parameter Ranges Using JMESPath" section below to assist.
When wanting to search for a range of items, use a JMESPath query to filter by a range of values, for example, filter on a range of Resistance 'Parameters' by applying a transform to the Resistance text field that allows a numerical range filter to be applied. Perform a sample query for one item first if you are unsure of what the data looks like.
Try to do large broad searches and pick items from the result of this search rather than many specific searches where possible.

#

## **Component Search Strategy: Using Multiple Keywords and Variations**

#

When searching for electronic components, never rely on a single exact keyword match. Component naming conventions vary widely across manufacturers, datasheets, and inventory systems. Always employ a multi-keyword strategy to ensure comprehensive results.

## **Key Principles**

#

Start with the broadest possible search (unfiltered if necessary) before applying JMESPath filters
Use multiple related terms including abbreviations, technical terms, and common variants
Search across multiple fields (part/name, part/description, part/tags, part/mpn)
When initial searches return zero or suspiciously few results, expand your keyword list or do an unfiltered manual scan

#

### **Example: Searching for Inductors**

#

Problem: Searching only for "inductor" may miss parts labeled with abbreviations or alternative terms like "ind", "choke", "coil", or parts identified only by their unit values (µH, uH, mH, nH).

Better approach \- search for multiple variants:
\[?contains(nvl("part/name", ''), 'ind') ||
  contains(nvl("part/description", ''), 'ind') ||
  contains(nvl("part/description", ''), 'choke') ||
  contains(nvl("part/description", ''), 'coil') ||
  contains(nvl("part/description", ''), 'uH') ||
  contains(nvl("part/description", ''), 'µH')\]

Note: This same principle applies to ALL component types. For resistors, search for "res", "resistor", "Ω", "ohm", etc. For capacitors, search for "cap", "capacitor", "µF", "uF", "pF", etc. For any component, consider abbreviations, full names, unit indicators, and related technical terms.

### **Warning Signs That Require Broader Search**

#

Zero results from a search that should logically return items (e.g., "no resistors found")
Unexpectedly low count when you know you have more
User questions the results

#

### **Best Practices**

#

DO: Search with multiple related keywords and abbreviations
DO: Include unit indicators (Ω, µH, µF, mA, V) in searches
DO: Verify suspicious zero-result searches with broader queries or unfiltered manual DON'T: Trust a single exact keyword match
DON'T: Assume standardized naming conventions

#

## **JMESPath Query Workflow**

#

NEVER construct a JMESPath query based on assumptions about field names or structure
ALWAYS reference the tool's schema documentation to confirm exact field paths before constructing queries
For complex nested data, consider making an initial call with a minimal JMESPath to inspect the actual structure, then refine your query
When calling API methods that accept a JMESPath query argument:
Before calling any API method with a JMESPath query, first review the tool's function schema in the available tools list to identify the exact field names and structure
Verify that every field referenced in your JMESPath matches the documented schema exactly (including nested paths)
When uncertain about field structure, first call the API with the default JMESPath (or no JMESPath) to see the actual response structure, then craft your custom query
Always supply a JMESPath that matches just the information that is required
Be specific about child elements also since child elements can also contain very large collections of data that are often not needed

#  **use JMESPath to perform filtering such as filtering out items with 'no stock availability' and use the advice in the "Filtering Components by Parameter Ranges Using JMESPath" section below to assist.**

* When wanting to search for a range of items, use a JMESPath query to filter by a range of values, for example, filter on a range of Resistance 'Parameters' by applying a transform to the Resistance text field that allows a numerical range filter to be applied. Perform a sample query for one item first if you are unsure of what the data looks like.
* Try to do large broad searches and pick items from the result of this search rather than many specific searches where possible.

# **Filtering Components by Parameter Ranges Using JMESPath**

When filtering components (e.g., resistors, capacitors) by parameter values that include unit suffixes, use the following pattern:

## **Core Pattern**

jmespath

nvl(int(regex\_replace('\<unit\_suffix\>$', '', \<parameter\_path\>)), \<out\_of\_range\_value\>)

## **Resistor Range Filtering Example**

To filter resistors by Ohm values (e.g., 10-500 Ohms), excluding kOhms and mOhms:

jmespath

Products\[?

  nvl(int(regex\_replace(' Ohms$', '', Parameters\[?ParameterText=='Resistance'\].ValueText | \[0\])), \`-1\`) \>= \`10\` &&

  nvl(int(regex\_replace(' Ohms$', '', Parameters\[?ParameterText=='Resistance'\].ValueText | \[0\])), \`-1\`) \<= \`500\`

\]

## **How It Works**

1. **`regex_replace(' Ohms$', '', ...)`** \- The `$` anchor ensures only exact suffix matches. "100 Ohms" becomes "100", but "10 kOhms" remains unchanged (no match).
2. **`int(...)`** \- Converts to integer. Returns `null` for non-numeric strings (e.g., "10 kOhms").
3. **`nvl(..., -1)`** \- Replaces `null` with a value outside the desired range, ensuring failed conversions are excluded.
4. **Range comparison** \- Only values within bounds pass the filter.

## **Adapting for Other Units**

| Component | Target Unit | Regex Pattern | Excluded |
| ----- | ----- | ----- | ----- |
| Resistors | Ohms | `' Ohms$'` | kOhms, mOhms, MOhms |
| Capacitors | pF | `' pF$'` | nF, µF, mF |
| Capacitors | µF | `' µF$'` | pF, nF, mF |
| Inductors | µH | `' µH$'` | nH, mH, H |

## **Important Notes**

* Always run a sample query first (limit 5-10) without filtering to inspect the actual `Parameters` structure and `ValueText` format.
* Use `str()` to convert values back to strings if needed to preserve response schema validation.
* Set the `nvl` default to a value guaranteed to be outside your filter range (e.g., `-1` for positive ranges).
* Perform category searches initially to find the appropriate category that can be used to narrow down broad searches.

###  **Full Example Query**  **{**

  \`limit\`: 50,

  \`keywords\`: \`RC0805\`,

  \`category\_id\`: \`52\`,

  \`jmespath\_query\`: \`{

  ProductsCount: ProductsCount,

  FilteredProducts: Products\[?

    nvl(int(regex\_replace(' Ohms$', '', Parameters\[?ParameterText=='Resistance'\].ValueText | \[0\])), \`\-1\`) \>= \`10\` &&

    nvl(int(regex\_replace(' Ohms$', '', Parameters\[?ParameterText=='Resistance'\].ValueText | \[0\])), \`\-1\`) \<= \`500\` &&

    Parameters\[?ParameterText=='Tolerance'\].ValueText | \[0\] \== '±1%'

  \].{

    MPN: ManufacturerProductNumber,

    DKN: ProductVariations\[0\].DigiKeyProductNumber,

    Resistance: Parameters\[?ParameterText=='Resistance'\].ValueText | \[0\],

    Tolerance: Parameters\[?ParameterText=='Tolerance'\].ValueText | \[0\],

    Price: UnitPrice,

    Stock: QuantityAvailable,

    MOQ: ProductVariations\[0\].MinimumOrderQuantity,

    Mfr: Manufacturer.Name

  }

}\`,

  \`search\_options\`: \`InStock\`

}
