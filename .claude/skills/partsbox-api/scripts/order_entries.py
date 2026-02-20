#!/usr/bin/env python3
"""PartsBox Order Entries API operations.

Subcommands: get, add, delete
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


def cmd_get(args):
    result = api_request("order/get-entries", {"order/id": args.order_id})
    items = result.get("data", [])
    paginate_and_output(items)


def cmd_add(args):
    entries = parse_json_arg(args.entries)
    payload = {
        "order/id": args.order_id,
        "order/entries": entries,
    }
    result = api_request("order/add-entries", payload)
    output_success(result.get("data"))


def cmd_delete(args):
    payload = {
        "order/id": args.order_id,
        "stock/id": args.stock_id,
    }
    result = api_request("order/delete-entry", payload)
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Order Entries API")
    sub = parser.add_subparsers(dest="command", required=True)

    # get
    p = sub.add_parser("get", help="List items in an order")
    p.add_argument("--order-id", dest="order_id", required=True, help="Order ID")
    add_pagination_args(p)

    # add
    p = sub.add_parser("add", help="Add items to an order")
    p.add_argument("--order-id", dest="order_id", required=True, help="Order ID")
    p.add_argument(
        "--entries",
        required=True,
        help='JSON array of entries, e.g. \'[{"entry/part-id":"abc","entry/quantity":10}]\'',
    )

    # delete
    p = sub.add_parser("delete", help="Delete an entry from an order")
    p.add_argument("--order-id", dest="order_id", required=True, help="Order ID")
    p.add_argument("--stock-id", dest="stock_id", required=True, help="Stock entry ID to delete")

    args = parser.parse_args()
    commands = {"get": cmd_get, "add": cmd_add, "delete": cmd_delete}
    commands[args.command](args)


if __name__ == "__main__":
    main()
