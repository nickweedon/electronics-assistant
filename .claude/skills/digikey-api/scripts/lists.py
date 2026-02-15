#!/usr/bin/env python3
"""DigiKey MyLists Management - Create, read, rename, delete lists."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import (
    api_get, api_post, api_put, api_delete,
    output_success, output_error, apply_query, parse_list_arg,
)


def cmd_get_all(args):
    """Get all lists for the authenticated user."""
    result = api_get("/mylists/v1/lists", customer_id=args.customer_id, use_user_token=True)

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    # API returns a list directly; wrap it
    data = result if isinstance(result, list) else result
    if isinstance(data, list):
        data = {"lists": data}

    if args.query:
        filtered, error = apply_query(data, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(data)


def cmd_create(args):
    """Create a new list."""
    name = args.name.strip()
    if not name:
        output_error("List name cannot be empty")

    body = {"ListName": name}
    if args.tags:
        body["Tags"] = parse_list_arg(args.tags)
    if args.source:
        body["Source"] = args.source

    result = api_post("/mylists/v1/lists", body, customer_id=args.customer_id, use_user_token=True)

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    output_success(result)


def cmd_get(args):
    """Get a specific list by ID."""
    params = {}
    if args.include_parts:
        params["includeParts"] = "true"

    result = api_get(
        f"/mylists/v1/lists/{args.list_id}",
        params or None,
        customer_id=args.customer_id,
        use_user_token=True,
    )

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    if args.query:
        filtered, error = apply_query(result, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(result)


def cmd_rename(args):
    """Rename a list."""
    name = args.name.strip()
    if not name:
        output_error("New name cannot be empty")

    result = api_put(
        f"/mylists/v1/lists/{args.list_id}/listName/{name}",
        customer_id=args.customer_id,
        use_user_token=True,
    )

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    output_success(result)


def cmd_delete(args):
    """Delete a list."""
    result = api_delete(
        f"/mylists/v1/lists/{args.list_id}",
        customer_id=args.customer_id,
        use_user_token=True,
    )

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    output_success(result)


def main():
    parser = argparse.ArgumentParser(description="DigiKey MyLists Management")
    sub = parser.add_subparsers(dest="command", required=True)

    # get all lists
    p_all = sub.add_parser("get-all", help="Get all lists")
    p_all.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")
    p_all.add_argument("--query", help="JMESPath expression")

    # create list
    p_create = sub.add_parser("create", help="Create a new list")
    p_create.add_argument("--name", required=True, help="List name")
    p_create.add_argument("--tags", help="Comma-separated tags")
    p_create.add_argument("--source", choices=["other", "internal", "external", "mobile", "search", "b2b"], help="List source")
    p_create.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    # get list by ID
    p_get = sub.add_parser("get", help="Get list by ID")
    p_get.add_argument("--list-id", required=True, help="List ID")
    p_get.add_argument("--include-parts", action="store_true", help="Include parts in response")
    p_get.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")
    p_get.add_argument("--query", help="JMESPath expression")

    # rename list
    p_rename = sub.add_parser("rename", help="Rename a list")
    p_rename.add_argument("--list-id", required=True, help="List ID")
    p_rename.add_argument("--name", required=True, help="New list name")
    p_rename.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    # delete list
    p_del = sub.add_parser("delete", help="Delete a list")
    p_del.add_argument("--list-id", required=True, help="List ID")
    p_del.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    args = parser.parse_args()
    commands = {
        "get-all": cmd_get_all,
        "create": cmd_create,
        "get": cmd_get,
        "rename": cmd_rename,
        "delete": cmd_delete,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
