#!/usr/bin/env python3
"""PartsBox Orders API operations.

Subcommands: list, get, create
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import (
    api_request,
    output_success,
    output_error,
    paginate_and_output,
    add_pagination_args,
    parse_json_arg,
)


def cmd_list(args):
    result = api_request("order/all")
    items = result.get("data", [])
    paginate_and_output(items)


def cmd_get(args):
    result = api_request("order/get", {"order/id": args.id})
    data = result.get("data")
    if data is None:
        output_error(f"Order not found: {args.id}")
    output_success(data)


def cmd_create(args):
    payload = {"order/vendor": args.vendor}
    if args.order_number:
        payload["order/number"] = args.order_number
    if args.comments:
        payload["order/comments"] = args.comments
    if args.entries:
        payload["order/entries"] = parse_json_arg(args.entries)

    result = api_request("order/create", payload)
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Orders API")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List all orders")
    add_pagination_args(p)

    # get
    p = sub.add_parser("get", help="Get order by ID")
    p.add_argument("--id", required=True, help="Order ID")

    # create
    p = sub.add_parser("create", help="Create a new purchase order")
    p.add_argument("--vendor", required=True, help="Vendor/supplier name")
    p.add_argument("--order-number", dest="order_number", help="Vendor order number")
    p.add_argument("--comments", help="Order comments")
    p.add_argument("--entries", help="Initial entries as JSON array")

    args = parser.parse_args()
    commands = {"list": cmd_list, "get": cmd_get, "create": cmd_create}
    commands[args.command](args)


if __name__ == "__main__":
    main()
