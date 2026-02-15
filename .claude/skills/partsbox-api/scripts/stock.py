#!/usr/bin/env python3
"""PartsBox Stock API operations.

Subcommands: add, remove, move, update
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_request, output_success, output_error


def cmd_add(args):
    payload = {
        "stock/part-id": args.part_id,
        "stock/storage-id": args.storage_id,
        "stock/quantity": args.quantity,
    }
    if args.comments:
        payload["stock/comments"] = args.comments
    if args.price is not None:
        payload["stock/price"] = args.price
    if args.currency:
        payload["stock/currency"] = args.currency
    if args.lot_name:
        payload["lot/name"] = args.lot_name
    if args.lot_description:
        payload["lot/description"] = args.lot_description
    if args.order_id:
        payload["stock/order-id"] = args.order_id

    result = api_request("stock/add", payload)
    output_success(result.get("data"))


def cmd_remove(args):
    payload = {
        "stock/part-id": args.part_id,
        "stock/storage-id": args.storage_id,
        "stock/quantity": args.quantity,
    }
    if args.comments:
        payload["stock/comments"] = args.comments
    if args.lot_id:
        payload["stock/lot-id"] = args.lot_id

    result = api_request("stock/remove", payload)
    output_success(result.get("data"))


def cmd_move(args):
    payload = {
        "stock/part-id": args.part_id,
        "stock/storage-id": args.source_storage_id,
        "stock/target-storage-id": args.target_storage_id,
        "stock/quantity": args.quantity,
    }
    if args.comments:
        payload["stock/comments"] = args.comments
    if args.lot_id:
        payload["stock/lot-id"] = args.lot_id

    result = api_request("stock/move", payload)
    output_success(result.get("data"))


def cmd_update(args):
    payload = {
        "stock/part-id": args.part_id,
        "stock/timestamp": args.timestamp,
    }
    if args.quantity is not None:
        payload["stock/quantity"] = args.quantity
    if args.comments is not None:
        payload["stock/comments"] = args.comments
    if args.price is not None:
        payload["stock/price"] = args.price
    if args.currency is not None:
        payload["stock/currency"] = args.currency

    result = api_request("stock/update", payload)
    output_success(result.get("data"))


def main():
    parser = argparse.ArgumentParser(description="PartsBox Stock API")
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p = sub.add_parser("add", help="Add stock for a part")
    p.add_argument("--part-id", dest="part_id", required=True, help="Part ID")
    p.add_argument("--storage-id", dest="storage_id", required=True, help="Storage location ID")
    p.add_argument("--quantity", type=int, required=True, help="Quantity to add")
    p.add_argument("--comments", help="Comments")
    p.add_argument("--price", type=float, help="Unit price")
    p.add_argument("--currency", help="Currency code (e.g., usd, eur)")
    p.add_argument("--lot-name", dest="lot_name", help="New lot name")
    p.add_argument("--lot-description", dest="lot_description", help="New lot description")
    p.add_argument("--order-id", dest="order_id", help="Associated order ID")

    # remove
    p = sub.add_parser("remove", help="Remove stock from inventory")
    p.add_argument("--part-id", dest="part_id", required=True, help="Part ID")
    p.add_argument("--storage-id", dest="storage_id", required=True, help="Storage location ID")
    p.add_argument("--quantity", type=int, required=True, help="Quantity to remove")
    p.add_argument("--comments", help="Comments")
    p.add_argument("--lot-id", dest="lot_id", help="Specific lot ID to remove from")

    # move
    p = sub.add_parser("move", help="Move stock between locations")
    p.add_argument("--part-id", dest="part_id", required=True, help="Part ID")
    p.add_argument("--source-storage-id", dest="source_storage_id", required=True, help="Source storage ID")
    p.add_argument("--target-storage-id", dest="target_storage_id", required=True, help="Target storage ID")
    p.add_argument("--quantity", type=int, required=True, help="Quantity to move")
    p.add_argument("--comments", help="Comments")
    p.add_argument("--lot-id", dest="lot_id", help="Specific lot ID to move")

    # update
    p = sub.add_parser("update", help="Update an existing stock entry")
    p.add_argument("--part-id", dest="part_id", required=True, help="Part ID")
    p.add_argument("--timestamp", type=int, required=True, help="Stock entry timestamp (UNIX ms)")
    p.add_argument("--quantity", type=int, help="New quantity")
    p.add_argument("--comments", help="New comments")
    p.add_argument("--price", type=float, help="New unit price")
    p.add_argument("--currency", help="New currency code")

    args = parser.parse_args()
    commands = {
        "add": cmd_add,
        "remove": cmd_remove,
        "move": cmd_move,
        "update": cmd_update,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
