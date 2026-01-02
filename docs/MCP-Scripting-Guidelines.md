# MCP Scripting Guidelines

## When to Write Scripts vs. Making Direct MCP Calls

**CRITICAL: For tasks requiring more than 10 repetitive MCP calls** (e.g., pricing lookups, bulk searches):

1. **ALWAYS create a Python script** - this is 5-10x faster than sequential tool calls
2. **NEVER fall back to manual tool calls** if the script has a fixable error (missing dependency, syntax error, etc.)

## Writing MCP Automation Scripts

### Step 1: Check for Existing Scripts

Check if there is any existing or similar script already under `scripts/`.

If there is a script serving the same or similar purpose then extend this script.

**ALWAYS** parameterize scripts so that they can be easily re-used in the future.

Also, have the script have a parameter to specify an output file such as a JSON file and write the script in such a way that the output file can be monitored for progress.

### Step 2: Read the Example File FIRST

```bash
# MANDATORY: Always read this file before writing any MCP automation script
cat playwright_example.py
```

The `playwright_example.py` file contains:
- Complete setup instructions (virtual environment, package installation)
- Working code patterns for MCP tool calls
- Tool naming conventions (server prefix required)
- Result access patterns (`.data` attribute)
- Documentation links for FastMCP

### Step 3: Follow the Established Pattern

Key requirements from the example:

- **Package**: Use `fastmcp` library (install with `uv pip install fastmcp`)
- **Tool names**: Must include server prefix: `"<server-name>_<tool-name>"`
  - Example: `"playwright-mcp-server_browser_navigate"` (NOT just `"browser_navigate"`)
- **Configuration**: Load from `.mcp.json` using `Client(config)`
- **Results**: Access structured data via `.data` attribute on CallToolResult
- **Async**: All MCP calls must use `async`/`await` pattern

### Step 4: Experiment First

If writing a new script or adding script features then:

1. Make a manual call to the related MCP server to ensure that the approach works
2. Use a reduced data set of just 2 or 3 items first to make sure the script works before running it against all the data items

### Step 5: Handle Errors Properly

If your script fails:
- ❌ **WRONG**: Abandon the script and revert to manual tool calls
- ✅ **CORRECT**: Fix the script error (install dependencies, fix syntax, adjust tool names)

Common fixable errors:
- `ModuleNotFoundError: No module named 'fastmcp'` → Run `uv pip install fastmcp`
- Tool not found errors → Add server prefix to tool name
- Attribute errors on results → Use `.data` instead of direct access

### Step 6: Script Organization

- Store all scripts in `scripts/` directory
- Parameterize inputs (accept command-line args or file inputs)
- Output results as JSON for easy parsing
- Check for existing scripts in `scripts/` before writing new ones
- Consider future reuse when designing the interface

## Example Script Structure

```python
#!/usr/bin/env python3
import asyncio
import json
from pathlib import Path
from fastmcp import Client

async def get_pricing(lcsc_codes: list) -> list:
    config_path = Path(__file__).parent.parent / ".mcp.json"
    with open(config_path) as f:
        config = json.load(f)

    client = Client(config)
    results = []

    async with client:
        for code in lcsc_codes:
            result = await client.call_tool(
                "playwright-mcp-server_browser_execute_bulk",
                {"commands": [...]}
            )
            results.append(result.data)

    return results
```

## Environment

**ALWAYS** run all local Python scripts using `uv` and the locally installed `.venv`. If the `.venv` is missing then create a new one using `uv`.

**NEVER** install things outside of the local `.venv` unless explicitly asked to.
