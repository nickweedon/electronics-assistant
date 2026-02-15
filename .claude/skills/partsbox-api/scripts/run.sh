#!/bin/bash
# Wrapper to run PartsBox API scripts using the venv Python.
# Usage: bash .claude/skills/partsbox-api/scripts/run.sh <script.py> [args...]
#
# Example: bash .claude/skills/partsbox-api/scripts/run.sh parts.py list --limit 10

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo '{"success": false, "error": "Virtual environment not found. Run: uv venv '"$SCRIPT_DIR"'/.venv && uv pip install --python '"$SCRIPT_DIR"'/.venv/bin/python requests jmespath"}'
    exit 1
fi

SCRIPT="$1"
shift

if [ -z "$SCRIPT" ]; then
    echo '{"success": false, "error": "Usage: run.sh <script.py> [args...]"}'
    exit 1
fi

# Source .env if PARTSBOX_API_KEY not set
if [ -z "$PARTSBOX_API_KEY" ] && [ -f /mnt/c/docker/partsbox-mcp-env ]; then
    export $(grep -v '^#' /mnt/c/docker/partsbox-mcp-env | xargs)
fi

exec "$VENV_PYTHON" "$SCRIPT_DIR/$SCRIPT" "$@"
