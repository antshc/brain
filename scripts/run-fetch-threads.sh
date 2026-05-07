#!/bin/bash
# Standalone wrapper to run fetch_and_classify_threads.
# Usage: run-fetch-threads.sh <PR_URL>

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "$1" ]]; then
  echo "Usage: $0 <PR_URL>" >&2
  exit 1
fi

python3 "$SCRIPT_DIR/fetch_threads.py" "$1"
