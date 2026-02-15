#!/usr/bin/env python3
"""Mouser Order History API - List past orders."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_post, output_success, output_error, check_api_errors


def cmd_list(args):
    """List order history for the past N days."""
    if args.days < 1:
        output_error("Days must be at least 1")

    payload = {"Days": args.days}

    result = api_post("orderhistory/query", payload)
    check_api_errors(result)
    output_success(result)


def main():
    parser = argparse.ArgumentParser(description="Mouser Order History")
    sub = parser.add_subparsers(dest="command", required=True)

    # list history
    p_list = sub.add_parser("list", help="List past orders")
    p_list.add_argument("--days", type=int, default=30, help="Look back N days (default: 30)")

    args = parser.parse_args()
    commands = {
        "list": cmd_list,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
