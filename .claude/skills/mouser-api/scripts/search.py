#!/usr/bin/env python3
"""Mouser Part Search API - Search by keyword or exact part number."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_post, output_success, output_error, check_api_errors


def cmd_keyword(args):
    """Search for parts by keyword."""
    keyword = args.keyword.strip()
    if not keyword:
        output_error("Keyword cannot be empty")

    records = args.records
    if records < 1 or records > 50:
        output_error("Records must be between 1 and 50 (API limit)")

    payload = {
        "SearchByKeywordRequest": {
            "keyword": keyword,
            "records": records,
            "startingRecord": args.start,
        }
    }

    result = api_post("search/keyword", payload)
    check_api_errors(result)

    search_results = result.get("SearchResults", {})
    output_success(search_results)


def cmd_part_number(args):
    """Search for a part by exact part number."""
    part_number = args.part_number.strip()
    if not part_number:
        output_error("Part number cannot be empty")

    payload = {
        "SearchByPartRequest": {
            "mouserPartNumber": part_number,
        }
    }

    result = api_post("search/partnumber", payload)
    check_api_errors(result)

    search_results = result.get("SearchResults", {})
    output_success(search_results)


def main():
    parser = argparse.ArgumentParser(description="Mouser Part Search")
    sub = parser.add_subparsers(dest="command", required=True)

    # keyword search
    p_kw = sub.add_parser("keyword", help="Search by keyword")
    p_kw.add_argument("--keyword", required=True, help="Search term")
    p_kw.add_argument("--records", type=int, default=50, help="Max results 1-50 (default: 50)")
    p_kw.add_argument("--start", type=int, default=0, help="Starting record for pagination (default: 0)")

    # part number search
    p_pn = sub.add_parser("part-number", help="Search by exact part number")
    p_pn.add_argument("--part-number", required=True, help="Mouser or manufacturer part number")

    args = parser.parse_args()
    commands = {
        "keyword": cmd_keyword,
        "part-number": cmd_part_number,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
