#!/usr/bin/env python3
"""PartsBox Projects API operations.

Subcommands: list, get, create, update, delete, archive, restore
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
    result = api_request("project/all")
    items = result.get("data", [])
    if not args.include_archived:
        items = [p for p in items if not p.get("project/archived", False)]
    paginate_and_output(items, args.limit, args.offset, args.query)


def cmd_get(args):
    result = api_request("project/get", {"project/id": args.id})
    data = result.get("data")
    if data is None:
        output_error(f"Project not found: {args.id}")
    output_success(data)


def cmd_create(args):
    payload = {"project/name": args.name}
    if args.description:
        payload["project/description"] = args.description
    if args.comments:
        payload["project/comments"] = args.comments
    if args.entries:
        payload["project/entries"] = parse_json_arg(args.entries)

    result = api_request("project/create", payload)
    output_success(result.get("data"))


def cmd_update(args):
    payload = {"project/id": args.id}
    if args.name:
        payload["project/name"] = args.name
    if args.description is not None:
        payload["project/description"] = args.description
    if args.comments is not None:
        payload["project/comments"] = args.comments

    result = api_request("project/update", payload)
    output_success(result.get("data"))


def cmd_delete(args):
    result = api_request("project/delete", {"project/id": args.id})
    output_success(result.get("data"))


def cmd_archive(args):
    result = api_request("project/archive", {"project/id": args.id})
    output_success(result.get("data"))


def cmd_restore(args):
    result = api_request("project/restore", {"project/id": args.id})
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Projects API")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List all projects")
    add_pagination_args(p)
    p.add_argument(
        "--include-archived",
        dest="include_archived",
        action="store_true",
        help="Include archived projects",
    )

    # get
    p = sub.add_parser("get", help="Get project by ID")
    p.add_argument("--id", required=True, help="Project ID")

    # create
    p = sub.add_parser("create", help="Create a new project")
    p.add_argument("--name", required=True, help="Project name")
    p.add_argument("--description", help="Project description")
    p.add_argument("--comments", help="Project comments")
    p.add_argument("--entries", help="Initial BOM entries as JSON array")

    # update
    p = sub.add_parser("update", help="Update project metadata")
    p.add_argument("--id", required=True, help="Project ID")
    p.add_argument("--name", help="New name")
    p.add_argument("--description", help="New description")
    p.add_argument("--comments", help="New comments")

    # delete
    p = sub.add_parser("delete", help="Delete a project")
    p.add_argument("--id", required=True, help="Project ID")

    # archive
    p = sub.add_parser("archive", help="Archive a project")
    p.add_argument("--id", required=True, help="Project ID")

    # restore
    p = sub.add_parser("restore", help="Restore an archived project")
    p.add_argument("--id", required=True, help="Project ID")

    args = parser.parse_args()
    commands = {
        "list": cmd_list,
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "delete": cmd_delete,
        "archive": cmd_archive,
        "restore": cmd_restore,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
