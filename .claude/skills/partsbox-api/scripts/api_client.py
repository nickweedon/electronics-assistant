#!/usr/bin/env python3
"""
PartsBox API Client - Shared module for all PartsBox API scripts.

Provides:
- HTTP client with authentication (PARTSBOX_API_KEY)
- JMESPath query support with custom functions (nvl, int, str, regex_replace)
- Pagination helpers
- Standardized JSON output formatting
- Common argparse argument helpers

API: All operations use POST to https://api.partsbox.com/api/1/{operation}
Auth: APIKey header with PARTSBOX_API_KEY environment variable
Fields: All field names use "/" separator (e.g., "part/name", "stock/quantity")
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Any, Optional

import requests
import jmespath
from jmespath import functions


# =============================================================================
# Environment & Configuration
# =============================================================================

def _load_env():
    """Load environment variables from .env files if PARTSBOX_API_KEY not set."""
    if os.getenv("PARTSBOX_API_KEY"):
        return

    env_paths = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent.parent.parent / ".env",
        Path.home() / ".partsbox" / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip("'\"")
                        if key and not os.getenv(key):
                            os.environ[key] = value
            break


_load_env()

API_KEY = os.getenv("PARTSBOX_API_KEY", "")
BASE_URL = "https://api.partsbox.com/api/1"


# =============================================================================
# Custom JMESPath Functions
# =============================================================================

class CustomFunctions(functions.Functions):
    """Custom JMESPath functions matching PartsBox MCP server conventions."""

    @functions.signature(
        {"types": ["string"]},
        {"types": ["string"]},
        {"types": ["string", "null"]},
    )
    def _func_regex_replace(self, pattern, replacement, value):
        """Regex find-and-replace: regex_replace(' ohm$', '', '100 ohm') -> '100'"""
        if value is None:
            return None
        try:
            return re.sub(pattern, replacement, value)
        except (re.error, TypeError):
            return value

    @functions.signature({"types": ["string", "number", "null"]})
    def _func_int(self, value):
        """Convert to integer: int('100') -> 100, int('invalid') -> null"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @functions.signature(
        {"types": ["string", "number", "boolean", "array", "object", "null"]}
    )
    def _func_str(self, value):
        """Convert to string: str(100) -> '100', str(null) -> 'null'"""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @functions.signature(
        {"types": ["string", "number", "boolean", "array", "object", "null"]},
        {"types": ["string", "number", "boolean", "array", "object"]},
    )
    def _func_nvl(self, value, default):
        """Return default if null: nvl(null, 'N/A') -> 'N/A'"""
        return default if value is None else value


_jmespath_options = jmespath.Options(custom_functions=CustomFunctions())


# =============================================================================
# API Client
# =============================================================================

_session = None


def _get_session():
    """Get or create HTTP session with auth headers."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(
            {
                "Authorization": f"APIKey {API_KEY}",
                "Content-Type": "application/json",
            }
        )
    return _session


def api_request(operation: str, data: dict = None) -> dict:
    """Make a POST request to the PartsBox API.

    Args:
        operation: API operation path (e.g., "part/all", "stock/add")
        data: Request payload dict

    Returns:
        Parsed JSON response dict.
        Calls output_error() and exits on failure.
    """
    if not API_KEY:
        output_error("PARTSBOX_API_KEY not set. Set in environment or .env file.")

    url = f"{BASE_URL}/{operation}"
    try:
        response = _get_session().post(url, json=data or {}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        output_error(f"API request to {operation} failed: {e}")


def api_download(url: str) -> requests.Response:
    """Make a GET request for file downloads.

    Args:
        url: Full URL to download from

    Returns:
        Raw response object.
        Calls output_error() and exits on failure.
    """
    if not API_KEY:
        output_error("PARTSBOX_API_KEY not set.")

    try:
        response = _get_session().get(url, timeout=60)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        output_error(f"Download failed: {e}")


# =============================================================================
# JMESPath Query Support
# =============================================================================


def apply_query(data, expression: str):
    """Apply JMESPath expression with custom functions.

    Args:
        data: Data to query (typically a list of dicts)
        expression: JMESPath expression string

    Returns:
        Tuple of (result, error_message). error_message is None on success.
    """
    try:
        result = jmespath.search(expression, data, options=_jmespath_options)
        return (result if result is not None else [], None)
    except jmespath.exceptions.JMESPathError as e:
        return ([], str(e))


# =============================================================================
# Output Helpers
# =============================================================================


def output_json(data):
    """Print JSON to stdout."""
    print(json.dumps(data, indent=2, default=str))


def output_success(data, **kwargs):
    """Print success response and exit cleanly."""
    result = {"success": True, "data": data}
    result.update(kwargs)
    output_json(result)


def output_error(message: str):
    """Print error response to stdout and exit with code 1."""
    output_json({"success": False, "error": message})
    sys.exit(1)


# =============================================================================
# Pagination
# =============================================================================


def paginate_and_output(items: list, limit: int, offset: int, query: str = None):
    """Apply optional JMESPath query, paginate results, and output JSON.

    Args:
        items: Full list of items from API
        limit: Max items per page
        offset: Starting index
        query: Optional JMESPath expression
    """
    query_applied = None

    if query:
        items, error = apply_query(items, query)
        if error:
            output_error(f"JMESPath query error: {error}")
        query_applied = query
        if not isinstance(items, list):
            output_success(items, query_applied=query_applied)
            return

    total = len(items)
    page = items[offset : offset + limit]

    output_json(
        {
            "success": True,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total,
            "data": page,
            "query_applied": query_applied,
        }
    )


# =============================================================================
# Argparse Helpers
# =============================================================================


def add_pagination_args(parser):
    """Add standard --limit, --offset, --query arguments."""
    parser.add_argument(
        "--limit", type=int, default=50, help="Max items to return (default: 50)"
    )
    parser.add_argument(
        "--offset", type=int, default=0, help="Skip first N items (default: 0)"
    )
    parser.add_argument(
        "--query", type=str, help="JMESPath filter/projection expression"
    )


def parse_json_arg(value: str):
    """Parse a JSON string into a Python object."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        output_error(f"Invalid JSON argument: {e}")


def parse_list_arg(value: str) -> list:
    """Parse a comma-separated string into a list of stripped strings."""
    return [item.strip() for item in value.split(",") if item.strip()]
