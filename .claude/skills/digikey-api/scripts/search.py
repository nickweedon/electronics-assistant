#!/usr/bin/env python3
"""DigiKey Product Search API - Search products, details, substitutions, media, manufacturers, categories."""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import (
    api_get, api_post, output_success, output_error,
    add_pagination_args, paginate_and_output, apply_query,
    parse_list_arg,
)


def cmd_keyword(args):
    """Search for products by keyword."""
    keywords = args.keywords.strip()
    if not keywords:
        output_error("Keywords cannot be empty")

    body = {
        "Keywords": keywords,
        "Limit": min(args.limit, 50),
        "Offset": args.offset,
    }

    if args.manufacturer_id:
        body["ManufacturerId"] = args.manufacturer_id
    if args.category_id:
        body["CategoryId"] = args.category_id
    if args.search_options:
        body["SearchOptionList"] = parse_list_arg(args.search_options)
    if args.sort_field:
        body["SortOptions"] = {
            "Field": args.sort_field,
            "SortOrder": args.sort_order or "Ascending",
        }

    result = api_post("/products/v4/search/keyword", body)

    if "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    if args.query:
        filtered, error = apply_query(result, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(result)


def cmd_product_details(args):
    """Get detailed product information."""
    pn = args.product_number.strip()
    if not pn:
        output_error("Product number cannot be empty")

    params = {}
    if args.manufacturer_id:
        params["manufacturerId"] = args.manufacturer_id

    result = api_get(f"/products/v4/search/{pn}/productdetails", params or None)

    if "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    if args.query:
        filtered, error = apply_query(result, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(result)


def cmd_substitutions(args):
    """Search for product substitutions."""
    pn = args.product_number.strip()
    if not pn:
        output_error("Product number cannot be empty")

    params = {"limit": str(args.limit)}
    result = api_get(f"/products/v4/search/{pn}/substitutions", params)

    if "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    if args.query:
        filtered, error = apply_query(result, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(result)


def cmd_media(args):
    """Get product media (images, datasheets, videos)."""
    pn = args.product_number.strip()
    if not pn:
        output_error("Product number cannot be empty")

    result = api_get(f"/products/v4/search/{pn}/media")

    if "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    output_success(result)


def cmd_manufacturers(args):
    """Get all manufacturers."""
    result = api_get("/products/v4/search/manufacturers")

    if "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    if args.query:
        filtered, error = apply_query(result, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(result)


def cmd_categories(args):
    """Get categories (optionally by ID)."""
    if args.category_id:
        result = api_get(f"/products/v4/search/categories/{args.category_id}")
    else:
        result = api_get("/products/v4/search/categories")

    if "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    if args.query:
        filtered, error = apply_query(result, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(result)


def main():
    parser = argparse.ArgumentParser(description="DigiKey Product Search")
    sub = parser.add_subparsers(dest="command", required=True)

    # keyword search
    p_kw = sub.add_parser("keyword", help="Search by keyword")
    p_kw.add_argument("--keywords", required=True, help="Search terms or part numbers")
    p_kw.add_argument("--limit", type=int, default=10, help="Max results 1-50 per page (default: 10)")
    p_kw.add_argument("--offset", type=int, default=0, help="Starting index (default: 0)")
    p_kw.add_argument("--manufacturer-id", help="Filter by manufacturer ID")
    p_kw.add_argument("--category-id", help="Filter by category ID")
    p_kw.add_argument("--search-options", help="Comma-separated: LeadFree,RoHSCompliant,InStock")
    p_kw.add_argument("--sort-field", help="Sort field: None,Packaging,ProductStatus,DigiKeyProductNumber,ManufacturerProductNumber,Manufacturer,MinimumQuantity,QuantityAvailable,Price,Supplier")
    p_kw.add_argument("--sort-order", help="Ascending or Descending (default: Ascending)")
    p_kw.add_argument("--query", help="JMESPath expression to filter response")

    # product details
    p_det = sub.add_parser("product-details", help="Get product details")
    p_det.add_argument("--product-number", required=True, help="DigiKey or manufacturer part number")
    p_det.add_argument("--manufacturer-id", help="Manufacturer ID for disambiguation")
    p_det.add_argument("--query", help="JMESPath expression")

    # substitutions
    p_sub = sub.add_parser("substitutions", help="Find substitute products")
    p_sub.add_argument("--product-number", required=True, help="Product to find substitutes for")
    p_sub.add_argument("--limit", type=int, default=10, help="Max substitutions (default: 10)")
    p_sub.add_argument("--query", help="JMESPath expression")

    # media
    p_med = sub.add_parser("media", help="Get product media")
    p_med.add_argument("--product-number", required=True, help="Product to get media for")

    # manufacturers
    p_mfr = sub.add_parser("manufacturers", help="Get all manufacturers")
    p_mfr.add_argument("--query", help="JMESPath expression")

    # categories
    p_cat = sub.add_parser("categories", help="Get categories")
    p_cat.add_argument("--category-id", help="Specific category ID (omit for all)")
    p_cat.add_argument("--query", help="JMESPath expression")

    args = parser.parse_args()
    commands = {
        "keyword": cmd_keyword,
        "product-details": cmd_product_details,
        "substitutions": cmd_substitutions,
        "media": cmd_media,
        "manufacturers": cmd_manufacturers,
        "categories": cmd_categories,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
