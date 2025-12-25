#!/bin/bash
#
# Extract LCSC product codes by searching MPNs
# Usage: ./extract_lcsc_codes.sh MPN1 MPN2 MPN3...
#

# Test MPNs (first 5 from the document)
TEST_MPNS=(
    "CC0805JRNPO9BN100"
    "C0805C100J5GACTU"
    "CC0805JRNPO9BN120"
    "CC0805JRNPO9BN150"
    "CC0805JRNPO9BN180"
)

# Function to extract LCSC product code from search results
extract_product_code() {
    local mpn="$1"
    local search_url="https://www.lcsc.com/search?q=${mpn}"

    echo "Searching: $mpn" >&2

    # Fetch the search page
    local html=$(curl -s -L "$search_url")

    # Extract product code using grep and sed
    # Looking for pattern: product-detail/C123456.html
    local product_code=$(echo "$html" | grep -o 'product-detail/C[0-9]\+\.html' | head -1 | sed 's/product-detail\/\(C[0-9]\+\)\.html/\1/')

    if [ -n "$product_code" ]; then
        echo "  Found: $product_code" >&2
        echo "$product_code"
        return 0
    else
        echo "  NOT FOUND" >&2
        return 1
    fi
}

# Main execution
echo "=============================="
echo "LCSC Product Code Extraction"
echo "=============================="
echo ""

# Use provided MPNs or test MPNs
MPNS=("$@")
if [ ${#MPNS[@]} -eq 0 ]; then
    MPNS=("${TEST_MPNS[@]}")
    echo "Using test MPNs (first 5 from document)"
    echo ""
fi

# Process each MPN
results=()
for mpn in "${MPNS[@]}"; do
    code=$(extract_product_code "$mpn")
    if [ -n "$code" ]; then
        results+=("$mpn|$code|https://www.lcsc.com/product-detail/$code.html")
    else
        results+=("$mpn|NOT_FOUND|")
    fi
    sleep 0.5  # Be nice to the server
done

# Print summary
echo ""
echo "=============================="
echo "RESULTS SUMMARY"
echo "=============================="
printf "%-30s %-15s %s\n" "MPN" "Product Code" "URL"
echo "----------------------------------------------------------------------------------------------"

success=0
total=${#results[@]}

for result in "${results[@]}"; do
    IFS='|' read -r mpn code url <<< "$result"
    if [ "$code" != "NOT_FOUND" ]; then
        printf "✅ %-30s %-15s %s\n" "$mpn" "$code" "$url"
        ((success++))
    else
        printf "❌ %-30s %-15s %s\n" "$mpn" "NOT FOUND" ""
    fi
done

echo ""
echo "Success Rate: $success/$total ($(( success * 100 / total ))%)"
echo "=============================="
