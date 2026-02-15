#!/usr/bin/env python3
"""DigiKey Pricing API - Product pricing via product details endpoint.

Note: The v4 API does not have a standalone /productpricing endpoint.
Pricing data is extracted from the product details response.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from api_client import api_get, output_success, output_error, apply_query


def cmd_product(args):
    """Get product pricing by extracting from product details."""
    pn = args.product_number.strip()
    if not pn:
        output_error("Product number cannot be empty")

    result = api_get(
        f"/products/v4/search/{pn}/productdetails",
        customer_id=args.customer_id,
    )

    if isinstance(result, dict) and "error" in result:
        output_error(result["error"].get("message", str(result["error"])))

    # Extract pricing information from product details
    product = result.get("Product", {})
    variations = product.get("ProductVariations", [])

    # Build a pricing-focused response
    pricing_data = {
        "ManufacturerPartNumber": product.get("ManufacturerProductNumber"),
        "UnitPrice": product.get("UnitPrice"),
        "QuantityAvailable": product.get("QuantityAvailable"),
        "RequestedQuantity": args.quantity,
        "ProductUrl": product.get("ProductUrl"),
        "Variations": [],
    }

    for var in variations:
        std_pricing = var.get("StandardPricing", [])
        my_pricing = var.get("MyPricing", [])

        # Calculate price for requested quantity
        calculated_price = None
        for tier in sorted(std_pricing, key=lambda t: t.get("BreakQuantity", 0), reverse=True):
            if args.quantity >= tier.get("BreakQuantity", 0):
                calculated_price = tier.get("UnitPrice")
                break

        pricing_data["Variations"].append({
            "DigiKeyProductNumber": var.get("DigiKeyProductNumber"),
            "PackageType": var.get("PackageType", {}).get("Name"),
            "MinimumOrderQuantity": var.get("MinimumOrderQuantity"),
            "StandardPackage": var.get("StandardPackage"),
            "QuantityAvailableforPackageType": var.get("QuantityAvailableforPackageType"),
            "CalculatedUnitPrice": calculated_price,
            "ExtendedPrice": round(calculated_price * args.quantity, 4) if calculated_price else None,
            "StandardPricing": std_pricing,
            "MyPricing": my_pricing,
        })

    if args.query:
        filtered, error = apply_query(pricing_data, args.query)
        if error:
            output_error(f"JMESPath query error: {error}")
        output_success(filtered)
    else:
        output_success(pricing_data)


def cmd_digi_reel(args):
    """Get DigiReel pricing.

    Note: This endpoint may not be available in all v4 API configurations.
    Falls back to product details if the dedicated endpoint is unavailable.
    """
    pn = args.product_number.strip()
    if not pn:
        output_error("Product number cannot be empty")

    params = {"requestedQuantity": str(args.quantity)}
    result = api_get(
        f"/products/v4/search/{pn}/digireelpricing",
        params,
        customer_id=args.customer_id,
    )

    if isinstance(result, dict) and "error" in result:
        # Fall back to product details with DigiReel fee info
        details = api_get(f"/products/v4/search/{pn}/productdetails")
        if isinstance(details, dict) and "error" in details:
            output_error(f"DigiReel pricing not available for {pn}")

        product = details.get("Product", {})
        for var in product.get("ProductVariations", []):
            if var.get("DigiReelFee") is not None:
                output_success({
                    "DigiKeyProductNumber": var.get("DigiKeyProductNumber"),
                    "ManufacturerPartNumber": product.get("ManufacturerProductNumber"),
                    "RequestedQuantity": args.quantity,
                    "DigiReelFee": var.get("DigiReelFee"),
                    "StandardPricing": var.get("StandardPricing", []),
                    "Note": "DigiReel pricing extracted from product details",
                })
                return

        output_error(f"No DigiReel option available for {pn}")

    output_success(result)


def main():
    parser = argparse.ArgumentParser(description="DigiKey Pricing")
    sub = parser.add_subparsers(dest="command", required=True)

    # product pricing
    p_prod = sub.add_parser("product", help="Get product pricing tiers")
    p_prod.add_argument("--product-number", required=True, help="DigiKey or manufacturer part number")
    p_prod.add_argument("--quantity", type=int, default=1, help="Requested quantity (default: 1)")
    p_prod.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")
    p_prod.add_argument("--query", help="JMESPath expression")

    # DigiReel pricing
    p_reel = sub.add_parser("digi-reel", help="Get DigiReel pricing")
    p_reel.add_argument("--product-number", required=True, help="DigiKey part number (DigiReel compatible)")
    p_reel.add_argument("--quantity", type=int, required=True, help="Requested quantity")
    p_reel.add_argument("--customer-id", default="0", help="Customer ID (default: 0)")

    args = parser.parse_args()
    commands = {
        "product": cmd_product,
        "digi-reel": cmd_digi_reel,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
