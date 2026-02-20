#!/usr/bin/env python3
"""
PartsBox API Client - Shared module for all PartsBox API scripts.

Provides:
- HTTP client with authentication (PARTSBOX_API_KEY)
- Standardized JSON output formatting
- Common argparse argument helpers

API: All operations use POST to https://api.partsbox.com/api/1/{operation}
Auth: APIKey header with PARTSBOX_API_KEY environment variable
Fields: All field names use "/" separator (e.g., "part/name", "stock/quantity")
"""

import os
import sys
import json
import argparse
from pathlib import Path

import requests


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
# List Output
# =============================================================================


def paginate_and_output(items: list, *args):
    """Output all items as a flat list."""
    output_json({"success": True, "total": len(items), "data": items})


# =============================================================================
# Argparse Helpers
# =============================================================================


def add_pagination_args(parser):
    """No-op: kept for backward compatibility with scripts that call it."""
    pass


def parse_json_arg(value: str):
    """Parse a JSON string into a Python object."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        output_error(f"Invalid JSON argument: {e}")


def parse_list_arg(value: str) -> list:
    """Parse a comma-separated string into a list of stripped strings."""
    return [item.strip() for item in value.split(",") if item.strip()]
