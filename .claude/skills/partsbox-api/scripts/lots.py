#!/usr/bin/env python3
"""PartsBox Lots API operations.

Subcommands: list, get, update
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
    parse_list_arg,
)


def cmd_list(args):
    result = api_request("lot/all")
    items = result.get("data", [])
    paginate_and_output(items, args.limit, args.offset, args.query)


def cmd_get(args):
    result = api_request("lot/get", {"lot/id": args.id})
    data = result.get("data")
    if data is None:
        output_error(f"Lot not found: {args.id}")
    output_success(data)


def cmd_update(args):
    payload = {"lot/id": args.id}
    if args.name is not None:
        payload["lot/name"] = args.name
    if args.description is not None:
        payload["lot/description"] = args.description
    if args.comments is not None:
        payload["lot/comments"] = args.comments
    if args.expiration_date is not None:
        payload["lot/expiration-date"] = args.expiration_date
    if args.tags:
        payload["lot/tags"] = parse_list_arg(args.tags)
    if args.custom_fields:
        payload["lot/custom"] = parse_json_arg(args.custom_fields)

    result = api_request("lot/update", payload)
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Lots API")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List all lots")
    add_pagination_args(p)

    # get
    p = sub.add_parser("get", help="Get lot by ID")
    p.add_argument("--id", required=True, help="Lot ID")

    # update
    p = sub.add_parser("update", help="Update lot information")
    p.add_argument("--id", required=True, help="Lot ID")
    p.add_argument("--name", help="New name")
    p.add_argument("--description", help="New description")
    p.add_argument("--comments", help="New comments")
    p.add_argument(
        "--expiration-date",
        dest="expiration_date",
        type=int,
        help="Expiration timestamp (UNIX ms)",
    )
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--custom-fields", dest="custom_fields", help="Custom fields as JSON")

    args = parser.parse_args()
    commands = {"list": cmd_list, "get": cmd_get, "update": cmd_update}
    commands[args.command](args)


if __name__ == "__main__":
    main()
