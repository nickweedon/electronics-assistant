#!/usr/bin/env python3
"""Mouser Shopping Cart API - Get, add to, and update cart items."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_get, api_post, output_success, output_error, check_api_errors


def cmd_get(args):
    """Get cart contents by cart key."""
    cart_key = args.cart_key.strip()
    if not cart_key:
        output_error("Cart key cannot be empty")

    result = api_get("cart", params={"cartKey": cart_key})
    check_api_errors(result)
    output_success(result)


def cmd_add(args):
    """Add an item to the cart."""
    cart_key = args.cart_key.strip()
    part_number = args.part_number.strip()
    if not cart_key:
        output_error("Cart key cannot be empty")
    if not part_number:
        output_error("Part number cannot be empty")
    if args.quantity < 1:
        output_error("Quantity must be at least 1")

    cart_item = {
        "MouserPartNumber": part_number,
        "Quantity": args.quantity,
    }
    if args.customer_part_number:
        cart_item["CustomerPartNumber"] = args.customer_part_number

    payload = {
        "CartKey": cart_key,
        "CartItems": [cart_item],
    }

    result = api_post("cart/items/insert", payload)
    check_api_errors(result)
    output_success(result)


def cmd_update(args):
    """Update quantity of a cart item (set to 0 to remove)."""
    cart_key = args.cart_key.strip()
    part_number = args.part_number.strip()
    if not cart_key:
        output_error("Cart key cannot be empty")
    if not part_number:
        output_error("Part number cannot be empty")
    if args.quantity < 0:
        output_error("Quantity cannot be negative (use 0 to remove)")

    payload = {
        "CartKey": cart_key,
        "CartItems": [
            {
                "MouserPartNumber": part_number,
                "Quantity": args.quantity,
            }
        ],
    }

    result = api_post("cart/items/update", payload)
    check_api_errors(result)
    output_success(result)


def main():
    parser = argparse.ArgumentParser(description="Mouser Shopping Cart")
    sub = parser.add_subparsers(dest="command", required=True)

    # get cart
    p_get = sub.add_parser("get", help="Get cart contents")
    p_get.add_argument("--cart-key", required=True, help="Cart identifier (UUID)")

    # add to cart
    p_add = sub.add_parser("add", help="Add item to cart")
    p_add.add_argument("--cart-key", required=True, help="Cart identifier (UUID)")
    p_add.add_argument("--part-number", required=True, help="Mouser part number")
    p_add.add_argument("--quantity", type=int, required=True, help="Quantity to add (>= 1)")
    p_add.add_argument("--customer-part-number", help="Optional customer reference number")

    # update cart item
    p_upd = sub.add_parser("update", help="Update cart item quantity")
    p_upd.add_argument("--cart-key", required=True, help="Cart identifier (UUID)")
    p_upd.add_argument("--part-number", required=True, help="Mouser part number")
    p_upd.add_argument("--quantity", type=int, required=True, help="New quantity (0 to remove)")

    args = parser.parse_args()
    commands = {
        "get": cmd_get,
        "add": cmd_add,
        "update": cmd_update,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
