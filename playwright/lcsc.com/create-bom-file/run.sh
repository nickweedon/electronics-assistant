#!/bin/bash
# Wrapper script for LCSC create-bom-file
# Note: This script doesn't need NODE_PATH since it uses only Node.js built-in modules
node "$(dirname "$0")/script.js" "$@"
