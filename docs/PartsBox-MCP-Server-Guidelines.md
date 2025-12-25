# **PartsBox MCP Server Usage**

# **PartsBox MCP Server Usage**

## **General Rules**

* Do not search the PartsBox website unless explicitly asked to.
* When calling API methods that allow retrieval limits to be applied, stick to small batches of no greater than 200 at a time to limit the amount of memory usage and increase performance.
* When calling API methods that accept a JMESPath query argument:
  * Always supply a JMESPath that matches just the information that is required.
  * Be specific about child elements also since child elements can also contain very large collections of data that are often not needed.
  * Always check the JMESPath against the MCP tool JSON schema to ensure it is correct before calling the API method.
* If you know that the amount of data that will be returned is likely large based on the requested JMESPath then limit the response to small chunks if limiting is available.
* Always ask for permission before performing any action that does not appear to be 'read-only'.

## **Querying**

* When searching for parts, always search at least this fields unless you know for sure that the data exists in a specific field:
  * part/name
  * part/tags
  * part/description
