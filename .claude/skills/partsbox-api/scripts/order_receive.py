#!/usr/bin/env python3
"""PartsBox Order Receive operation.

Processes received inventory into a storage location.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_request, output_success, parse_json_arg


def main():
    parser = argparse.ArgumentParser(
        description="Receive an order into storage (PartsBox API)"
    )
    parser.add_argument("--order-id", dest="order_id", required=True, help="Order ID")
    parser.add_argument(
        "--storage-id", dest="storage_id", required=True, help="Storage location ID to receive into"
    )
    parser.add_argument(
        "--entries",
        help="JSON array of entries to receive (omit to receive all items)",
    )
    parser.add_argument("--comments", help="Receipt comments")

    args = parser.parse_args()

    payload = {
        "order/id": args.order_id,
        "stock/storage-id": args.storage_id,
    }
    if args.entries:
        payload["order/entries"] = parse_json_arg(args.entries)
    if args.comments:
        payload["stock/comments"] = args.comments

    result = api_request("order/receive", payload)
    output_success(result.get("data"))


if __name__ == "__main__":
    main()
