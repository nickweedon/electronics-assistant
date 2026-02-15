#!/usr/bin/env python3
"""DigiKey MyLists Parts - CRUD operations for parts within lists."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import (
    api_get, api_post, api_put, api_delete,
    output_success, output_error, apply_query, parse_json_arg,
)


def cmd_get_all(args):
    """Get all parts from a list."""
    params = {}
    if args.start_index is not None:
        params["startIndex"] = str(args.start_index)
    if args.limit is not None:
        params["limit"] = str(args.limit)
    if args.include_attrition:
        params["includeAttrition"] = "true"

    result = api_get(
        f"/mylists/v1/lists/{args.list_id}/parts",
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


def cmd_add(args):
    """Add parts to a list."""
    parts = parse_json_arg(args.parts_json)
    if not isinstance(parts, list):
        parts = [parts]

    # Convert snake_case keys to PascalCase for API
    api_parts = []
    field_mapping = {
        "part_id": "PartId",
        "requested_part_number": "RequestedPartNumber",
        "manufacturer_name": "ManufacturerName",
        "customer_reference": "CustomerReference",
        "reference_designator": "ReferenceDesignator",
        "notes": "Notes",
        "selected_quantity_index": "SelectedQuantityIndex",
        "attrition": "Attrition",
        "quantities": "Quantities",
    }
    quantity_mapping = {
        "selected_pack_type": "SelectedPackType",
        "quantity": "Quantity",
        "target_price": "TargetPrice",
    }

    for part in parts:
        api_part = {}
        for key, value in part.items():
            api_key = field_mapping.get(key, key)
            if key == "quantities" and isinstance(value, list):
                api_part[api_key] = [
                    {quantity_mapping.get(qk, qk): qv for qk, qv in q.items()}
                    for q in value
                ]
            else:
                api_part[api_key] = value
        api_parts.append(api_part)

    endpoint = f"/mylists/v1/lists/{args.list_id}/parts"
    if args.index:
        endpoint += f"?index={args.index}"

    result = api_post(endpoint, api_parts, customer_id=args.customer_id, use_user_token=True)

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    # Wrap list result
    if isinstance(result, list):
        result = {"part_ids": result}

    output_success(result)


def cmd_get(args):
    """Get a specific part from a list."""
    result = api_get(
        f"/mylists/v1/lists/{args.list_id}/parts/{args.part_id}",
        customer_id=args.customer_id,
        use_user_token=True,
    )

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    output_success(result)


def cmd_update(args):
    """Update a part in a list."""
    part_data = parse_json_arg(args.part_json)

    # Convert snake_case keys to PascalCase
    field_mapping = {
        "customer_reference": "CustomerReference",
        "reference_designator": "ReferenceDesignator",
        "notes": "Notes",
        "selected_quantity_index": "SelectedQuantityIndex",
        "attrition": "Attrition",
        "quantities": "Quantities",
    }

    api_data = {}
    for key, value in part_data.items():
        api_data[field_mapping.get(key, key)] = value

    result = api_put(
        f"/mylists/v1/lists/{args.list_id}/parts/{args.part_id}",
        api_data,
        customer_id=args.customer_id,
        use_user_token=True,
    )

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    output_success(result)


def cmd_delete(args):
    """Delete a part from a list."""
    result = api_delete(
        f"/mylists/v1/lists/{args.list_id}/parts/{args.part_id}",
        customer_id=args.customer_id,
        use_user_token=True,
    )

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    output_success(result)


def main():
    parser = argparse.ArgumentParser(description="DigiKey MyLists Parts")
    sub = parser.add_subparsers(dest="command", required=True)

    # get all parts
    p_all = sub.add_parser("get-all", help="Get all parts from a list")
    p_all.add_argument("--list-id", required=True, help="List ID")
    p_all.add_argument("--start-index", type=int, help="Starting index for pagination")
    p_all.add_argument("--limit", type=int, help="Max parts to return")
    p_all.add_argument("--include-attrition", action="store_true", help="Include attrition data")
    p_all.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")
    p_all.add_argument("--query", help="JMESPath expression")

    # add parts
    p_add = sub.add_parser("add", help="Add parts to a list")
    p_add.add_argument("--list-id", required=True, help="List ID")
    p_add.add_argument("--parts-json", required=True, help='JSON array of parts or @filename (e.g. \'[{"RequestedPartNumber": "296-8875-1-ND"}]\')')
    p_add.add_argument("--index", type=int, default=0, help="Insert position (default: 0)")
    p_add.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    # get single part
    p_get = sub.add_parser("get", help="Get a specific part from a list")
    p_get.add_argument("--list-id", required=True, help="List ID")
    p_get.add_argument("--part-id", required=True, help="Part UniqueId")
    p_get.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    # update part
    p_upd = sub.add_parser("update", help="Update a part in a list")
    p_upd.add_argument("--list-id", required=True, help="List ID")
    p_upd.add_argument("--part-id", required=True, help="Part UniqueId")
    p_upd.add_argument("--part-json", required=True, help='JSON with fields to update or @filename (e.g. \'{"Notes": "Updated"}\')')
    p_upd.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    # delete part
    p_del = sub.add_parser("delete", help="Delete a part from a list")
    p_del.add_argument("--list-id", required=True, help="List ID")
    p_del.add_argument("--part-id", required=True, help="Part UniqueId")
    p_del.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    args = parser.parse_args()
    commands = {
        "get-all": cmd_get_all,
        "add": cmd_add,
        "get": cmd_get,
        "update": cmd_update,
        "delete": cmd_delete,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
