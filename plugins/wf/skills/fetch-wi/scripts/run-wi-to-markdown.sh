#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/workitem.md"

cat "$SCRIPT_DIR/workitem.json" | python3 "$SCRIPT_DIR/wi_json_to_markdown.py" > "$OUTPUT_FILE"
echo "Saved to $OUTPUT_FILE"
