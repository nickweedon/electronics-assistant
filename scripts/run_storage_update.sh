#!/bin/bash
# Convenience wrapper for storage metadata updater
# Usage:
#   ./run_storage_update.sh dry-run              # Preview changes
#   ./run_storage_update.sh update-existing      # Update existing locations
#   ./run_storage_update.sh create-new           # Create new locations
#   ./run_storage_update.sh full                 # Both update and create
#   ./run_storage_update.sh full --no-interactive  # Non-interactive mode

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="/workspace/.claude/skills/partsbox-api/scripts/.venv/bin/python"
UPDATE_SCRIPT="$SCRIPT_DIR/update_storage_tags.py"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PYTHON"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: $0 {dry-run|update-existing|create-new|full} [--no-interactive]"
    exit 1
fi

MODE="$1"
shift

# Run the updater
exec "$VENV_PYTHON" "$UPDATE_SCRIPT" --mode "$MODE" "$@"
