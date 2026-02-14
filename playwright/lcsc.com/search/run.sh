#!/bin/bash
# Wrapper script for LCSC search - automatically sets NODE_PATH
NODE_PATH=$(npm root -g) node "$(dirname "$0")/script.js" "$@"
