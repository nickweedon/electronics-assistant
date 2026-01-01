#!/usr/bin/env python3
"""
Example script using FastMCP Client to control Playwright via MCP

SETUP INSTRUCTIONS (for future reference):
1. Create virtual environment if it doesn't exist:
   $ uv venv --python 3.12

2. Activate the virtual environment:
   $ source .venv/bin/activate

3. Install fastmcp package:
   $ uv pip install fastmcp

4. Run the script:
   $ python playwright_example.py

IMPORTANT NOTES:
- The package name is 'fastmcp' (not 'gofastmcp' or 'fast-mcp')
- Tool names are prefixed with server name from .mcp.json
  Example: "playwright-mcp-server_browser_navigate"
- Results are CallToolResult objects - use .data to access structured content
- Config is loaded from .mcp.json in the same directory

USEFUL DOCUMENTATION LINKS:
- FastMCP Client Overview:
  https://gofastmcp.com/clients/client

- FastMCP Installation Guide:
  https://gofastmcp.com/getting-started/installation

- Configuration-Based Clients (how to use .mcp.json):
  https://gofastmcp.com/clients/client#configuration-based-clients

- FastMCP GitHub Repository:
  https://github.com/jlowin/fastmcp

- Model Context Protocol (MCP) Specification:
  https://spec.modelcontextprotocol.io/

- uv Package Manager:
  https://docs.astral.sh/uv/getting-started/installation/

KEY PATTERN:
The config-based client pattern shown here automatically handles:
- Starting/stopping MCP server processes
- Managing stdio/SSE/HTTP transports
- Prefixing tool names with server names
- Connection lifecycle management
"""

import asyncio
import json
from pathlib import Path
from fastmcp import Client


async def main():
    # Load MCP configuration from .mcp.json
    # This config defines all available MCP servers (playwright, digikey, etc.)
    config_path = Path(__file__).parent / ".mcp.json"
    with open(config_path) as f:
        config = json.load(f)

    # Create FastMCP Client with the configuration
    # The Client class handles connections to all configured MCP servers
    client = Client(config)

    # Use async context manager to ensure proper connection lifecycle
    async with client:
        print("Navigating to www.example.com (silent mode)...")

        # STEP 1: Navigate to the page in silent mode
        # silent_mode=True prevents returning the snapshot in navigation response
        # This is more efficient when you plan to call browser_snapshot separately
        #
        # Tool documentation: The playwright-mcp-server tools are defined in your
        # .mcp.json config. For Playwright MCP docs see:
        # https://github.com/executeautomation/playwright-mcp-server
        #
        # Note: Tool names follow pattern: "<server-name>_<tool-name>"
        # where server-name comes from the key in .mcp.json's mcpServers object
        nav_result = await client.call_tool(
            "playwright-mcp-server_browser_navigate",
            {
                "url": "https://www.example.com",
                "silent_mode": True  # Don't return snapshot in navigation response
            }
        )

        # Access result data using .data attribute
        # CallToolResult has these important attributes:
        # - .data: Dictionary with the structured response
        # - .content: List of Content objects (TextContent, ImageContent, etc.)
        # - .is_error: Boolean indicating if the call failed
        # - .structured_content: Same as .data (alternative accessor)
        #
        # For most use cases, .data is what you want to access
        nav_data = nav_result.data
        print(f"Navigation successful: {nav_data['success']}")
        print(f"URL: {nav_data['url']}\n")

        # STEP 2: Call browser_snapshot to get the page content
        # This retrieves the ARIA accessibility snapshot of the current page
        #
        # ARIA snapshots provide a structured representation of page elements
        # based on accessibility roles. This is more reliable than HTML parsing
        # for automated browser interaction.
        #
        # Common parameters:
        # - flatten: Convert hierarchical tree to flat list with depth info
        # - limit: Maximum items to return (useful with flatten for pagination)
        # - offset: Starting index for pagination (requires flatten or jmespath_query)
        # - jmespath_query: Filter/transform snapshot using JMESPath expressions
        # - output_format: "yaml" (default) or "json"
        #
        # For JMESPath query examples, see the CLAUDE.md file in this repo:
        # docs/Using-JMESPath.md
        print("Capturing page snapshot...")
        snapshot_result = await client.call_tool(
            "playwright-mcp-server_browser_snapshot",
            {
                # Optional parameters you can use:
                # "flatten": True,  # Flatten ARIA tree to list
                # "limit": 150,     # Limit number of items
                # "output_format": "json"  # Return as JSON instead of YAML
            }
        )

        # Access the snapshot data
        snapshot_data = snapshot_result.data

        print("\nSnapshot captured successfully!")
        print(f"Total items: {snapshot_data.get('total_items', 'N/A')}")
        print(f"Output format: {snapshot_data.get('output_format', 'N/A')}")
        print(f"\nSnapshot content (first 800 chars):")
        snapshot_content = snapshot_data.get('snapshot', '')
        print(snapshot_content[:800] if snapshot_content else 'No snapshot')


if __name__ == "__main__":
    asyncio.run(main())
