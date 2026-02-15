#!/usr/bin/env python3
"""DigiKey OAuth Management - Token status, refresh, and manual setup."""

import sys
import os
import time
import argparse
import urllib.parse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import (
    _load_user_tokens, _save_user_tokens, _get_client_token,
    _refresh_user_token, CLIENT_ID, CLIENT_SECRET, TOKEN_FILE,
    AUTHORIZE_URL, USE_SANDBOX, output_success, output_error,
)


def cmd_status(args):
    """Show token status."""
    info = {
        "client_id_set": bool(CLIENT_ID),
        "client_secret_set": bool(CLIENT_SECRET),
        "environment": "SANDBOX" if USE_SANDBOX else "PRODUCTION",
        "token_file": str(TOKEN_FILE),
    }

    # Check client token
    try:
        _get_client_token()
        info["client_token"] = "valid"
    except SystemExit:
        info["client_token"] = "failed"

    # Check user tokens
    tokens = _load_user_tokens()
    if tokens:
        info["user_token"] = "loaded"
        info["refresh_token"] = "loaded"
        ts = tokens.get("timestamp")
        if ts:
            age_hours = (time.time() - ts) / 3600
            info["token_age_hours"] = round(age_hours, 1)
    else:
        info["user_token"] = "not found"
        info["refresh_token"] = "not found"

    output_success(info)


def cmd_refresh(args):
    """Force-refresh the user token."""
    new_token = _refresh_user_token()
    output_success({"message": "User token refreshed successfully", "token_preview": new_token[:20] + "..."})


def cmd_login_url(args):
    """Generate the OAuth authorization URL."""
    if not CLIENT_ID:
        output_error("CLIENT_ID not set.")

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": "https://localhost:8139/callback",
    }
    url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    output_success({"authorization_url": url, "instructions": "Open this URL in a browser to authorize. After authorization, use set-tokens to save the tokens."})


def cmd_set_tokens(args):
    """Manually set user tokens."""
    _save_user_tokens(args.user_token, args.refresh_token)
    output_success({"message": "Tokens saved successfully", "token_file": str(TOKEN_FILE)})


def main():
    parser = argparse.ArgumentParser(description="DigiKey OAuth Management")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show token status")
    sub.add_parser("refresh", help="Force-refresh user token")
    sub.add_parser("login-url", help="Generate OAuth authorization URL")

    p_set = sub.add_parser("set-tokens", help="Manually set tokens")
    p_set.add_argument("--user-token", required=True, help="OAuth user access token")
    p_set.add_argument("--refresh-token", required=True, help="OAuth refresh token")

    args = parser.parse_args()
    commands = {
        "status": cmd_status,
        "refresh": cmd_refresh,
        "login-url": cmd_login_url,
        "set-tokens": cmd_set_tokens,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
