#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$DIR" rev-parse --show-toplevel)"
FILE="$ROOT/me.txt"

[[ -f "$FILE" ]] || { echo "me.txt not found: $FILE" >&2; exit 1; }
printf '%s\n' "$FILE"
