#!/bin/bash
# Wrapper to run Mouser API scripts using the venv Python.
# Usage: bash .claude/skills/mouser-api/scripts/run.sh <script.py> [args...]
#
# Example: bash .claude/skills/mouser-api/scripts/run.sh search.py keyword --keyword "arduino" --records 5

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo '{"success": false, "error": "Virtual environment not found. Run: uv venv '"$SCRIPT_DIR"'/.venv && uv pip install --python '"$SCRIPT_DIR"'/.venv/bin/python requests"}'
    exit 1
fi

SCRIPT="$1"
shift

if [ -z "$SCRIPT" ]; then
    echo '{"success": false, "error": "Usage: run.sh <script.py> [args...]"}'
    exit 1
fi

# Source project .env if API keys not set
if [ -z "$MOUSER_PART_API_KEY" ] && [ -f /workspace/.env ]; then
    export $(grep -v '^#' /workspace/.env | xargs)
fi

exec "$VENV_PYTHON" "$SCRIPT_DIR/$SCRIPT" "$@"
