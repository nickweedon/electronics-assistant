#!/usr/bin/env python3
"""Mouser Order API - Get order details and order options."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_get, api_post, output_success, output_error, check_api_errors


def cmd_get(args):
    """Get order details by order number."""
    order_number = args.order_number.strip()
    if not order_number:
        output_error("Order number cannot be empty")

    result = api_get(f"order/{order_number}")
    check_api_errors(result)
    output_success(result)


def cmd_options(args):
    """Get available order options (shipping, payment, addresses) for a cart."""
    cart_key = args.cart_key.strip()
    if not cart_key:
        output_error("Cart key cannot be empty")

    payload = {"CartKey": cart_key}

    result = api_post("order/options/query", payload)
    check_api_errors(result)
    output_success(result)


def main():
    parser = argparse.ArgumentParser(description="Mouser Order Operations")
    sub = parser.add_subparsers(dest="command", required=True)

    # get order
    p_get = sub.add_parser("get", help="Get order details")
    p_get.add_argument("--order-number", required=True, help="Mouser or web order number")

    # get order options
    p_opts = sub.add_parser("options", help="Get order options for a cart")
    p_opts.add_argument("--cart-key", required=True, help="Cart identifier (UUID)")

    args = parser.parse_args()
    commands = {
        "get": cmd_get,
        "options": cmd_options,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
