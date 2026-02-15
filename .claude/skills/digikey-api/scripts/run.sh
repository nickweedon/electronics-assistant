#!/bin/bash
# Wrapper to run DigiKey API scripts using the venv Python.
# Usage: bash .claude/skills/digikey-api/scripts/run.sh <script.py> [args...]
#
# Example: bash .claude/skills/digikey-api/scripts/run.sh search.py keyword --keywords "STM32F407" --limit 5

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo '{"success": false, "error": "Virtual environment not found. Run: uv venv '"$SCRIPT_DIR"'/.venv && uv pip install --python '"$SCRIPT_DIR"'/.venv/bin/python -r '"$SCRIPT_DIR"'/requirements.txt"}'
    exit 1
fi

SCRIPT="$1"
shift

if [ -z "$SCRIPT" ]; then
    echo '{"success": false, "error": "Usage: run.sh <script.py> [args...]"}'
    exit 1
fi

# Source DigiKey MCP .env if CLIENT_ID not set
if [ -z "$CLIENT_ID" ] && [ -f /opt/src/mcp/digikey_mcp/.env ]; then
    export $(grep -v '^#' /opt/src/mcp/digikey_mcp/.env | xargs)
fi

exec "$VENV_PYTHON" "$SCRIPT_DIR/$SCRIPT" "$@"
