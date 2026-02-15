#!/usr/bin/env python3
"""PartsBox Builds API operations.

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
)


def cmd_list(args):
    result = api_request("project/get-builds", {"project/id": args.project_id})
    items = result.get("data", [])
    paginate_and_output(items, args.limit, args.offset, args.query)


def cmd_get(args):
    result = api_request("build/get", {"build/id": args.id})
    data = result.get("data")
    if data is None:
        output_error(f"Build not found: {args.id}")
    output_success(data)


def cmd_update(args):
    payload = {"build/id": args.id}
    if args.comments is not None:
        payload["build/comments"] = args.comments

    result = api_request("build/update", payload)
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Builds API")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List builds for a project")
    p.add_argument("--project-id", dest="project_id", required=True, help="Project ID")
    add_pagination_args(p)

    # get
    p = sub.add_parser("get", help="Get build by ID")
    p.add_argument("--id", required=True, help="Build ID")

    # update
    p = sub.add_parser("update", help="Update build metadata")
    p.add_argument("--id", required=True, help="Build ID")
    p.add_argument("--comments", help="New comments")

    args = parser.parse_args()
    commands = {"list": cmd_list, "get": cmd_get, "update": cmd_update}
    commands[args.command](args)


if __name__ == "__main__":
    main()
