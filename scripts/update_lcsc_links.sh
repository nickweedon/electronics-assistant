#!/bin/bash
#
# Update Price-Optimized-Orders.md with LCSC product links
#

INPUT_FILE="docs/Price-Optimized-Orders.md"
OUTPUT_FILE="docs/Price-Optimized-Orders.md.new"
MAPPING_FILE="/tmp/mpn_to_url.txt"

echo "Updating LCSC links in $INPUT_FILE..."

# Create a copy to work with
cp "$INPUT_FILE" "$OUTPUT_FILE"

# Read mapping file and apply replacements
while read -r mpn code url; do
    # Skip if already has a link (contains [ or ])
    # Replace: | MPN | with | [MPN](URL) |
    # Only replace in lines that contain "| LCSC |"
    # Use # as delimiter to avoid conflicts with / in URLs
    sed -i "/| LCSC |/s#| ${mpn} |#| [${mpn}](${url}) |#" "$OUTPUT_FILE"
    echo "  ✅ $mpn -> $code"
done < "$MAPPING_FILE"

echo ""
echo "Updated file saved to: $OUTPUT_FILE"
echo ""
echo "To apply changes:"
echo "  mv $OUTPUT_FILE $INPUT_FILE"
