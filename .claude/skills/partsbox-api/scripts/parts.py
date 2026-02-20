#!/usr/bin/env python3
"""PartsBox Parts API operations.

Subcommands: list, get, create, update, delete, stock, lots, storage,
             add-meta, remove-meta, add-substitutes, remove-substitutes
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
    result = api_request("part/all")
    items = result.get("data", [])
    paginate_and_output(items)


def cmd_get(args):
    result = api_request("part/get", {"part/id": args.id})
    data = result.get("data")
    if data is None:
        output_error(f"Part not found: {args.id}")
    output_success(data)


def cmd_create(args):
    payload = {"part/name": args.name, "part/type": args.type}
    if args.description:
        payload["part/description"] = args.description
    if args.notes:
        payload["part/notes"] = args.notes
    if args.footprint:
        payload["part/footprint"] = args.footprint
    if args.manufacturer:
        payload["part/manufacturer"] = args.manufacturer
    if args.mpn:
        payload["part/mpn"] = args.mpn
    if args.tags:
        payload["part/tags"] = parse_list_arg(args.tags)
    if args.cad_keys:
        payload["part/cad-keys"] = parse_list_arg(args.cad_keys)
    if args.low_stock is not None:
        payload["part/low-stock"] = {"report": args.low_stock}
    if args.custom_fields:
        payload["part/custom"] = parse_json_arg(args.custom_fields)

    result = api_request("part/create", payload)
    output_success(result.get("data"))


def cmd_update(args):
    payload = {"part/id": args.id}
    if args.name:
        payload["part/name"] = args.name
    if args.description is not None:
        payload["part/description"] = args.description
    if args.notes is not None:
        payload["part/notes"] = args.notes
    if args.footprint is not None:
        payload["part/footprint"] = args.footprint
    if args.manufacturer is not None:
        payload["part/manufacturer"] = args.manufacturer
    if args.mpn is not None:
        payload["part/mpn"] = args.mpn
    if args.tags:
        payload["part/tags"] = parse_list_arg(args.tags)
    if args.cad_keys:
        payload["part/cad-keys"] = parse_list_arg(args.cad_keys)
    if args.low_stock is not None:
        payload["part/low-stock"] = {"report": args.low_stock}
    if args.custom_fields:
        payload["part/custom"] = parse_json_arg(args.custom_fields)

    result = api_request("part/update", payload)
    output_success(result.get("data"))


def cmd_delete(args):
    result = api_request("part/delete", {"part/id": args.id})
    output_success(result.get("data"))


def cmd_stock(args):
    result = api_request("part/stock", {"part/id": args.id})
    data = result.get("data", 0)
    total = data.get("stock/total", 0) if isinstance(data, dict) else data
    output_success({"part_id": args.id, "total_stock": total})


def cmd_lots(args):
    result = api_request("part/lots", {"part/id": args.id})
    items = result.get("data", [])
    paginate_and_output(items, args.limit, args.offset)


def cmd_storage(args):
    result = api_request("part/storage", {"part/id": args.id})
    items = result.get("data", [])
    paginate_and_output(items, args.limit, args.offset)


def cmd_add_meta(args):
    payload = {
        "part/id": args.id,
        "part/meta-part-ids": parse_list_arg(args.member_ids),
    }
    result = api_request("part/add-meta-part-ids", payload)
    output_success(result.get("data"))


def cmd_remove_meta(args):
    payload = {
        "part/id": args.id,
        "part/meta-part-ids": parse_list_arg(args.member_ids),
    }
    result = api_request("part/remove-meta-part-ids", payload)
    output_success(result.get("data"))


def cmd_add_substitutes(args):
    payload = {
        "part/id": args.id,
        "part/substitute-ids": parse_list_arg(args.substitute_ids),
    }
    result = api_request("part/add-substitute-ids", payload)
    output_success(result.get("data"))


def cmd_remove_substitutes(args):
    payload = {
        "part/id": args.id,
        "part/substitute-ids": parse_list_arg(args.substitute_ids),
    }
    result = api_request("part/remove-substitute-ids", payload)
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Parts API")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="List all parts")
    add_pagination_args(p)

    # get
    p = sub.add_parser("get", help="Get part by ID")
    p.add_argument("--id", required=True, help="Part ID")

    # create
    p = sub.add_parser("create", help="Create a new part")
    p.add_argument("--name", required=True, help="Part name")
    p.add_argument(
        "--type",
        default="local",
        choices=["local", "linked", "sub-assembly", "meta"],
        help="Part type (default: local)",
    )
    p.add_argument("--description", help="Part description")
    p.add_argument("--notes", help="Part notes")
    p.add_argument("--footprint", help="Part footprint")
    p.add_argument("--manufacturer", help="Manufacturer name")
    p.add_argument("--mpn", help="Manufacturer part number")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--cad-keys", dest="cad_keys", help="Comma-separated CAD keys")
    p.add_argument("--low-stock", dest="low_stock", type=int, help="Low stock threshold")
    p.add_argument("--custom-fields", dest="custom_fields", help="Custom fields as JSON")

    # update
    p = sub.add_parser("update", help="Update an existing part")
    p.add_argument("--id", required=True, help="Part ID")
    p.add_argument("--name", help="New name")
    p.add_argument("--description", help="New description")
    p.add_argument("--notes", help="New notes")
    p.add_argument("--footprint", help="New footprint")
    p.add_argument("--manufacturer", help="New manufacturer")
    p.add_argument("--mpn", help="New MPN")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--cad-keys", dest="cad_keys", help="Comma-separated CAD keys")
    p.add_argument("--low-stock", dest="low_stock", type=int, help="Low stock threshold")
    p.add_argument("--custom-fields", dest="custom_fields", help="Custom fields as JSON")

    # delete
    p = sub.add_parser("delete", help="Delete a part")
    p.add_argument("--id", required=True, help="Part ID")

    # stock
    p = sub.add_parser("stock", help="Get total stock count for a part")
    p.add_argument("--id", required=True, help="Part ID")

    # lots
    p = sub.add_parser("lots", help="List stock sources (per-lot detail)")
    p.add_argument("--id", required=True, help="Part ID")
    add_pagination_args(p)

    # storage
    p = sub.add_parser("storage", help="List stock sources (aggregated by location)")
    p.add_argument("--id", required=True, help="Part ID")
    add_pagination_args(p)

    # add-meta
    p = sub.add_parser("add-meta", help="Add members to a meta-part")
    p.add_argument("--id", required=True, help="Meta-part ID")
    p.add_argument("--member-ids", dest="member_ids", required=True, help="Comma-separated member part IDs")

    # remove-meta
    p = sub.add_parser("remove-meta", help="Remove members from a meta-part")
    p.add_argument("--id", required=True, help="Meta-part ID")
    p.add_argument("--member-ids", dest="member_ids", required=True, help="Comma-separated member part IDs")

    # add-substitutes
    p = sub.add_parser("add-substitutes", help="Add substitutes to a part")
    p.add_argument("--id", required=True, help="Part ID")
    p.add_argument("--substitute-ids", dest="substitute_ids", required=True, help="Comma-separated substitute part IDs")

    # remove-substitutes
    p = sub.add_parser("remove-substitutes", help="Remove substitutes from a part")
    p.add_argument("--id", required=True, help="Part ID")
    p.add_argument("--substitute-ids", dest="substitute_ids", required=True, help="Comma-separated substitute part IDs")

    args = parser.parse_args()
    commands = {
        "list": cmd_list,
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "delete": cmd_delete,
        "stock": cmd_stock,
        "lots": cmd_lots,
        "storage": cmd_storage,
        "add-meta": cmd_add_meta,
        "remove-meta": cmd_remove_meta,
        "add-substitutes": cmd_add_substitutes,
        "remove-substitutes": cmd_remove_substitutes,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
