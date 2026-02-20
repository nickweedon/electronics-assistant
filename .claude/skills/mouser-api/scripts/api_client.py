#!/usr/bin/env python3
"""
Mouser API Client - Shared module for all Mouser API scripts.

Provides:
- HTTP client with dual API key authentication (part vs order keys)
- Standardized JSON output formatting
- Common argparse argument helpers

API: Mouser REST API v1 at https://api.mouser.com/api/v1
Auth: API key passed as query parameter (?apiKey=...)
Keys: MOUSER_PART_API_KEY (search) and MOUSER_ORDER_API_KEY (cart/order)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Any, Optional

import requests


# =============================================================================
# Environment & Configuration
# =============================================================================

def _load_env():
    """Load environment variables from .env files if Mouser keys not set."""
    if os.getenv("MOUSER_PART_API_KEY") and os.getenv("MOUSER_ORDER_API_KEY"):
        return

    env_paths = [
        Path("/workspace") / ".env",
        Path.cwd() / ".env",
        Path.home() / ".mouser" / ".env",
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

PART_API_KEY = os.getenv("MOUSER_PART_API_KEY", "")
ORDER_API_KEY = os.getenv("MOUSER_ORDER_API_KEY", "")
BASE_URL = os.getenv("MOUSER_API_BASE_URL", "https://api.mouser.com/api/v1")
TIMEOUT = int(os.getenv("MOUSER_API_TIMEOUT", "30"))


# =============================================================================
# API Client
# =============================================================================

_session = None


def _get_session():
    """Get or create HTTP session."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "Content-Type": "application/json",
        })
    return _session


def _get_api_key(endpoint: str) -> str:
    """Select the correct API key based on endpoint.

    Search endpoints use MOUSER_PART_API_KEY.
    Cart, order, and history endpoints use MOUSER_ORDER_API_KEY.
    """
    if "search/" in endpoint or "/search/" in endpoint:
        if not PART_API_KEY:
            output_error("MOUSER_PART_API_KEY not set. Set in environment or .env file.")
        return PART_API_KEY
    else:
        if not ORDER_API_KEY:
            output_error("MOUSER_ORDER_API_KEY not set. Set in environment or .env file.")
        return ORDER_API_KEY


def api_get(endpoint: str, params: dict = None) -> dict:
    """Make a GET request to the Mouser API.

    Args:
        endpoint: API endpoint path (e.g., "order/12345")
        params: Additional query parameters

    Returns:
        Parsed JSON response dict.
        Calls output_error() and exits on failure.
    """
    api_key = _get_api_key(endpoint)
    url = f"{BASE_URL}/{endpoint}"
    query = {"apiKey": api_key}
    if params:
        query.update(params)

    try:
        response = _get_session().get(url, params=query, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        output_error(f"GET {endpoint} failed: {e}")


def api_post(endpoint: str, json_data: dict = None) -> dict:
    """Make a POST request to the Mouser API.

    Args:
        endpoint: API endpoint path (e.g., "search/keyword")
        json_data: Request body dict

    Returns:
        Parsed JSON response dict.
        Calls output_error() and exits on failure.
    """
    api_key = _get_api_key(endpoint)
    url = f"{BASE_URL}/{endpoint}"
    query = {"apiKey": api_key}

    try:
        response = _get_session().post(url, params=query, json=json_data or {}, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        output_error(f"POST {endpoint} failed: {e}")


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


def check_api_errors(response: dict):
    """Check for Mouser API error responses (HTTP 200 with Errors array)."""
    errors = response.get("Errors")
    if errors:
        messages = [f"{e.get('Code', '?')}: {e.get('Message', 'Unknown error')}" for e in errors]
        output_error(f"API returned errors: {'; '.join(messages)}")


# =============================================================================
# Argparse Helpers
# =============================================================================

def parse_json_arg(value: str):
    """Parse a JSON string into a Python object."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        output_error(f"Invalid JSON argument: {e}")


def parse_list_arg(value: str) -> list:
    """Parse a comma-separated string into a list of stripped strings."""
    return [item.strip() for item in value.split(",") if item.strip()]
