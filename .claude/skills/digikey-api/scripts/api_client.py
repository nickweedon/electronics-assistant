#!/usr/bin/env python3
"""
DigiKey API Client - Shared module for all DigiKey API scripts.

Provides:
- HTTP client with OAuth2 authentication (client credentials + user token)
- Token management (load, save, refresh)
- JMESPath query support with custom functions (nvl, int, str, regex_replace)
- Pagination helpers
- Standardized JSON output formatting
- Common argparse argument helpers

API: DigiKey REST API v4 at https://api.digikey.com
Auth: OAuth2 Bearer token via client_credentials (search) or user token (MyLists)
"""

import os
import sys
import json
import re
import time
import argparse
from pathlib import Path
from typing import Any, Optional

import requests
import jmespath
from jmespath import functions


# =============================================================================
# Environment & Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent


def _load_env():
    """Load environment variables from .env files if CLIENT_ID not set."""
    if os.getenv("CLIENT_ID") and os.getenv("CLIENT_SECRET"):
        return

    env_paths = [
        Path.cwd() / ".env",
        Path("/opt/src/mcp/digikey_mcp") / ".env",
        Path.home() / ".digikey" / ".env",
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

CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
USE_SANDBOX = os.getenv("USE_SANDBOX", "false").lower() == "true"

if USE_SANDBOX:
    API_BASE = "https://sandbox-api.digikey.com"
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
    AUTHORIZE_URL = "https://sandbox-api.digikey.com/v1/oauth2/authorize"
else:
    API_BASE = "https://api.digikey.com"
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
    AUTHORIZE_URL = "https://api.digikey.com/v1/oauth2/authorize"

TOKEN_FILE = SCRIPT_DIR / ".digikey_tokens"


# =============================================================================
# Token Management
# =============================================================================

_client_token = None


def _load_user_tokens():
    """Load user OAuth tokens from file.

    Returns:
        dict with 'user_token' and 'refresh_token', or None if not found.
    """
    if not TOKEN_FILE.exists():
        return None
    try:
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        if "user_token" in data and "refresh_token" in data:
            return data
        return None
    except (json.JSONDecodeError, OSError):
        return None


def _save_user_tokens(user_token, refresh_token):
    """Save user OAuth tokens to file."""
    data = {
        "user_token": user_token,
        "refresh_token": refresh_token,
        "timestamp": time.time(),
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_client_token():
    """Get OAuth2 client credentials token for Product Search API."""
    global _client_token
    if _client_token:
        return _client_token

    if not CLIENT_ID or not CLIENT_SECRET:
        output_error("CLIENT_ID and CLIENT_SECRET must be set in environment or .env file.")

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
    if resp.status_code != 200:
        output_error(f"Client token request failed: {resp.status_code} - {resp.text}")

    _client_token = resp.json()["access_token"]
    return _client_token


def _refresh_user_token():
    """Refresh the user access token using the refresh token.

    Returns:
        New user token string, or calls output_error on failure.
    """
    tokens = _load_user_tokens()
    if not tokens or not tokens.get("refresh_token"):
        output_error("No refresh token available. Run: auth.py set-tokens --user-token <token> --refresh-token <token>")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
    if resp.status_code != 200:
        output_error(f"Token refresh failed: {resp.status_code} - {resp.text}")

    token_data = resp.json()
    new_user_token = token_data["access_token"]
    new_refresh_token = token_data.get("refresh_token", tokens["refresh_token"])
    _save_user_tokens(new_user_token, new_refresh_token)
    return new_user_token


def _get_token(use_user_token=False):
    """Get the appropriate token for the request.

    Args:
        use_user_token: If True, use user OAuth token (for MyLists).
                       If False, use client credentials token (for search).

    Returns:
        Bearer token string.
    """
    if use_user_token:
        tokens = _load_user_tokens()
        if not tokens:
            output_error("No user tokens found. Run: auth.py set-tokens --user-token <token> --refresh-token <token>")
        return tokens["user_token"]
    else:
        return _get_client_token()


# =============================================================================
# HTTP Client
# =============================================================================

def _get_headers(customer_id="0", use_user_token=False):
    """Get standard headers for DigiKey API requests."""
    token = _get_token(use_user_token)
    return {
        "Authorization": f"Bearer {token}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "Content-Type": "application/json",
        "X-DIGIKEY-Locale-Site": "US",
        "X-DIGIKEY-Locale-Language": "en",
        "X-DIGIKEY-Locale-Currency": "USD",
        "X-DIGIKEY-Customer-Id": customer_id,
    }


def _handle_response(resp, url):
    """Handle API response, returning parsed JSON or error dict.

    For 400/403/404, returns structured error dict instead of raising.
    For 204/empty, returns success message.
    """
    if resp.status_code in [200, 201]:
        if not resp.content:
            return {"status": "success", "message": "Operation completed successfully"}
        return resp.json()

    if resp.status_code == 204:
        return {"status": "success", "message": "Operation completed successfully"}

    if resp.status_code in [400, 403, 404]:
        try:
            error_detail = resp.json()
        except (ValueError, json.JSONDecodeError):
            error_detail = {"detail": resp.text}

        error_type_map = {400: "BadRequest", 403: "Forbidden", 404: "ResourceNotFound"}
        return {
            "error": {
                "type": error_type_map.get(resp.status_code, "APIError"),
                "code": f"HTTP_{resp.status_code}",
                "status": resp.status_code,
                "message": error_detail.get("detail") or error_detail.get("title") or resp.text,
                "url": url,
                "details": error_detail,
            }
        }

    output_error(f"API request failed: {resp.status_code} - {resp.text}")


def _make_request(method, url, headers, data=None, use_user_token=False):
    """Make an API request with auto-retry on 401 token expiry."""
    method = method.upper()

    def _execute():
        if method == "GET":
            return requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            return requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PUT":
            return requests.put(url, headers=headers, json=data, timeout=30)
        elif method == "DELETE":
            return requests.delete(url, headers=headers, timeout=30)
        else:
            output_error(f"Unsupported HTTP method: {method}")

    resp = _execute()

    # Auto-retry on 401 (token expired)
    if resp.status_code == 401:
        try:
            error_data = resp.json()
            # Check multiple error message locations and patterns
            error_msg = (
                error_data.get("detail", "")
                + error_data.get("ErrorMessage", "")
            ).lower()
            if "bearer token" in error_msg and "expired" in error_msg:
                if use_user_token:
                    new_token = _refresh_user_token()
                    headers["Authorization"] = f"Bearer {new_token}"
                else:
                    global _client_token
                    _client_token = None
                    new_token = _get_client_token()
                    headers["Authorization"] = f"Bearer {new_token}"
                resp = _execute()
        except (ValueError, KeyError, json.JSONDecodeError):
            pass

    return _handle_response(resp, url)


def api_get(endpoint, params=None, customer_id="0", use_user_token=False):
    """Make a GET request to the DigiKey API.

    Args:
        endpoint: API endpoint path (e.g., "/products/v4/search/manufacturers")
        params: Optional dict of query parameters
        customer_id: Customer ID for the request
        use_user_token: Use user OAuth token instead of client token

    Returns:
        Parsed JSON response dict.
    """
    url = f"{API_BASE}{endpoint}"
    if params:
        query_parts = [f"{k}={v}" for k, v in params.items() if v is not None]
        if query_parts:
            url += "?" + "&".join(query_parts)

    headers = _get_headers(customer_id, use_user_token)
    return _make_request("GET", url, headers, use_user_token=use_user_token)


def api_post(endpoint, data=None, customer_id="0", use_user_token=False):
    """Make a POST request to the DigiKey API.

    Args:
        endpoint: API endpoint path
        data: Request body dict or list
        customer_id: Customer ID for the request
        use_user_token: Use user OAuth token instead of client token

    Returns:
        Parsed JSON response dict.
    """
    url = f"{API_BASE}{endpoint}"
    headers = _get_headers(customer_id, use_user_token)
    return _make_request("POST", url, headers, data, use_user_token=use_user_token)


def api_put(endpoint, data=None, customer_id="0", use_user_token=False):
    """Make a PUT request to the DigiKey API.

    Args:
        endpoint: API endpoint path
        data: Request body dict
        customer_id: Customer ID for the request
        use_user_token: Use user OAuth token instead of client token

    Returns:
        Parsed JSON response dict.
    """
    url = f"{API_BASE}{endpoint}"
    headers = _get_headers(customer_id, use_user_token)
    return _make_request("PUT", url, headers, data, use_user_token=use_user_token)


def api_delete(endpoint, customer_id="0", use_user_token=False):
    """Make a DELETE request to the DigiKey API.

    Args:
        endpoint: API endpoint path
        customer_id: Customer ID for the request
        use_user_token: Use user OAuth token instead of client token

    Returns:
        Parsed JSON response dict.
    """
    url = f"{API_BASE}{endpoint}"
    headers = _get_headers(customer_id, use_user_token)
    return _make_request("DELETE", url, headers, use_user_token=use_user_token)


# =============================================================================
# Custom JMESPath Functions
# =============================================================================

class CustomFunctions(functions.Functions):
    """Custom JMESPath functions matching partsbox-api conventions."""

    @functions.signature(
        {"types": ["string"]},
        {"types": ["string"]},
        {"types": ["string", "null"]},
    )
    def _func_regex_replace(self, pattern, replacement, value):
        if value is None:
            return None
        try:
            return re.sub(pattern, replacement, value)
        except (re.error, TypeError):
            return value

    @functions.signature({"types": ["string", "number", "null"]})
    def _func_int(self, value):
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
        return default if value is None else value


_jmespath_options = jmespath.Options(custom_functions=CustomFunctions())


def apply_query(data, expression):
    """Apply JMESPath expression with custom functions.

    Args:
        data: Data to query
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


def output_error(message):
    """Print error response to stdout and exit with code 1."""
    output_json({"success": False, "error": message})
    sys.exit(1)


def paginate_and_output(items, limit, offset, query=None):
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

    output_json({
        "success": True,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": offset + limit < total,
        "data": page,
        "query_applied": query_applied,
    })


# =============================================================================
# Argparse Helpers
# =============================================================================

def add_pagination_args(parser):
    """Add standard --limit, --offset, --query arguments."""
    parser.add_argument("--limit", type=int, default=50, help="Max items to return (default: 50)")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N items (default: 0)")
    parser.add_argument("--query", type=str, help="JMESPath filter/projection expression")


def parse_json_arg(value):
    """Parse a JSON string or @filename into a Python object."""
    if value.startswith("@"):
        filepath = value[1:]
        try:
            with open(filepath) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            output_error(f"Failed to read JSON from {filepath}: {e}")
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        output_error(f"Invalid JSON argument: {e}")


def parse_list_arg(value):
    """Parse a comma-separated string into a list of stripped strings."""
    return [item.strip() for item in value.split(",") if item.strip()]
