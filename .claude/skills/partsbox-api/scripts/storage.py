#!/usr/bin/env python3
"""PartsBox Storage Location API operations.

Subcommands: list, get, create, update, rename, archive, restore, settings, parts, lots
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
    parse_list_arg,
)


def cmd_list(args):
    result = api_request("storage/all")
    items = result.get("data", [])
    if not args.include_archived:
        items = [loc for loc in items if not loc.get("storage/archived", False)]
    paginate_and_output(items, args.limit, args.offset, args.query)


def cmd_get(args):
    result = api_request("storage/get", {"storage/id": args.id})
    data = result.get("data")
    if data is None:
        output_error(f"Storage location not found: {args.id}")
    output_success(data)


def cmd_create(args):
    payload = {"storage/name": args.name}
    if args.description:
        payload["storage/description"] = args.description
    if args.tags:
        payload["storage/tags"] = parse_list_arg(args.tags)

    result = api_request("storage/create", payload)
    output_success(result.get("data"))


def cmd_update(args):
    payload = {"storage/id": args.id}
    if args.comments is not None:
        payload["storage/comments"] = args.comments
    if args.tags:
        payload["storage/tags"] = parse_list_arg(args.tags)

    result = api_request("storage/update", payload)
    output_success(result.get("data"))


def cmd_rename(args):
    payload = {"storage/id": args.id, "storage/name": args.name}
    result = api_request("storage/rename", payload)
    output_success(result.get("data"))


def cmd_archive(args):
    result = api_request("storage/archive", {"storage/id": args.id})
    output_success(result.get("data"))


def cmd_restore(args):
    result = api_request("storage/restore", {"storage/id": args.id})
    output_success(result.get("data"))


def cmd_settings(args):
    payload = {"storage/id": args.id}
    if args.full is not None:
        payload["storage/full?"] = args.full.lower() == "true"
    if args.single_part is not None:
        payload["storage/single-part?"] = args.single_part.lower() == "true"
    if args.existing_parts_only is not None:
        payload["storage/existing-parts-only?"] = args.existing_parts_only.lower() == "true"

    result = api_request("storage/change-settings", payload)
    output_success(result.get("data"))


def cmd_parts(args):
    result = api_request("storage/parts", {"storage/id": args.id})
    items = result.get("data", [])
    paginate_and_output(items, args.limit, args.offset, args.query)


def cmd_lots(args):
    result = api_request("storage/lots", {"storage/id": args.id})
    items = result.get("data", [])
    paginate_and_output(items, args.limit, args.offset, args.query)


def main():
    parser = argparse.ArgumentParser(description="PartsBox Storage API")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List all storage locations")
    add_pagination_args(p)
    p.add_argument(
        "--include-archived",
        dest="include_archived",
        action="store_true",
        help="Include archived locations",
    )

    # get
    p = sub.add_parser("get", help="Get storage location by ID")
    p.add_argument("--id", required=True, help="Storage location ID")

    # create
    p = sub.add_parser("create", help="Create a new storage location")
    p.add_argument("--name", required=True, help="Storage location name (must be unique)")
    p.add_argument("--description", help="Description of the storage location")
    p.add_argument("--tags", help="Comma-separated tags")

    # update
    p = sub.add_parser("update", help="Update storage location metadata")
    p.add_argument("--id", required=True, help="Storage location ID")
    p.add_argument("--comments", help="New comments")
    p.add_argument("--tags", help="Comma-separated tags")

    # rename
    p = sub.add_parser("rename", help="Rename a storage location")
    p.add_argument("--id", required=True, help="Storage location ID")
    p.add_argument("--name", required=True, help="New name")

    # archive
    p = sub.add_parser("archive", help="Archive a storage location")
    p.add_argument("--id", required=True, help="Storage location ID")

    # restore
    p = sub.add_parser("restore", help="Restore an archived storage location")
    p.add_argument("--id", required=True, help="Storage location ID")

    # settings
    p = sub.add_parser("settings", help="Change storage location settings")
    p.add_argument("--id", required=True, help="Storage location ID")
    p.add_argument("--full", choices=["true", "false"], help="Mark location as full")
    p.add_argument(
        "--single-part",
        dest="single_part",
        choices=["true", "false"],
        help="Single-part-only mode",
    )
    p.add_argument(
        "--existing-parts-only",
        dest="existing_parts_only",
        choices=["true", "false"],
        help="Restrict to existing parts only",
    )

    # parts
    p = sub.add_parser("parts", help="List parts in a storage location (aggregated)")
    p.add_argument("--id", required=True, help="Storage location ID")
    add_pagination_args(p)

    # lots
    p = sub.add_parser("lots", help="List lots in a storage location")
    p.add_argument("--id", required=True, help="Storage location ID")
    add_pagination_args(p)

    args = parser.parse_args()
    commands = {
        "list": cmd_list,
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "rename": cmd_rename,
        "archive": cmd_archive,
        "restore": cmd_restore,
        "settings": cmd_settings,
        "parts": cmd_parts,
        "lots": cmd_lots,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
