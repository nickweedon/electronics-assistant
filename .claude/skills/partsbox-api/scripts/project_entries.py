#!/usr/bin/env python3
"""PartsBox Project Entries (BOM) API operations.

Subcommands: get, add, update, delete
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


def cmd_get(args):
    payload = {"project/id": args.project_id}
    if args.build_id:
        payload["build/id"] = args.build_id

    result = api_request("project/get-entries", payload)
    items = result.get("data", [])
    paginate_and_output(items)


def cmd_add(args):
    entries = parse_json_arg(args.entries)
    payload = {
        "project/id": args.project_id,
        "project/entries": entries,
    }
    result = api_request("project/add-entries", payload)
    output_success(result.get("data"))


def cmd_update(args):
    entries = parse_json_arg(args.entries)
    payload = {
        "project/id": args.project_id,
        "project/entries": entries,
    }
    result = api_request("project/update-entries", payload)
    output_success(result.get("data"))


def cmd_delete(args):
    payload = {
        "project/id": args.project_id,
        "entry/ids": parse_list_arg(args.entry_ids),
    }
    result = api_request("project/delete-entries", payload)
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Project Entries (BOM) API")
    sub = parser.add_subparsers(dest="command", required=True)

    # get
    p = sub.add_parser("get", help="Get BOM entries for a project")
    p.add_argument("--project-id", dest="project_id", required=True, help="Project ID")
    p.add_argument("--build-id", dest="build_id", help="Build ID for historical snapshot")
    add_pagination_args(p)

    # add
    p = sub.add_parser("add", help="Add BOM entries to a project")
    p.add_argument("--project-id", dest="project_id", required=True, help="Project ID")
    p.add_argument(
        "--entries",
        required=True,
        help='JSON array of entries, e.g. \'[{"entry/part-id":"abc","entry/quantity":10}]\'',
    )

    # update
    p = sub.add_parser("update", help="Update existing BOM entries")
    p.add_argument("--project-id", dest="project_id", required=True, help="Project ID")
    p.add_argument(
        "--entries",
        required=True,
        help='JSON array of entries with entry/id, e.g. \'[{"entry/id":"abc","entry/quantity":20}]\'',
    )

    # delete
    p = sub.add_parser("delete", help="Delete BOM entries from a project")
    p.add_argument("--project-id", dest="project_id", required=True, help="Project ID")
    p.add_argument(
        "--entry-ids",
        dest="entry_ids",
        required=True,
        help="Comma-separated entry IDs to delete",
    )

    args = parser.parse_args()
    commands = {"get": cmd_get, "add": cmd_add, "update": cmd_update, "delete": cmd_delete}
    commands[args.command](args)


if __name__ == "__main__":
    main()
