#!/usr/bin/env bash
set -eu

if [ "$#" -ne 1 ]; then
  printf 'Usage: %s <harness-root>\n' "$0" >&2
  exit 64
fi

harness_root=$(cd "$1" && pwd -P)
workspace="$harness_root/workspace"

if [ ! -e "$workspace" ]; then
  printf '%s\n' "$harness_root"
  exit 0
fi

source_repos=()
for candidate in "$workspace"/*; do
  if [ -d "$candidate" ] && [ "$(git -C "$candidate" rev-parse --show-toplevel 2>/dev/null || true)" = "$(cd "$candidate" && pwd -P)" ]; then
    source_repos+=("$(cd "$candidate" && pwd -P)")
  fi
done

if [ "${#source_repos[@]}" -eq 0 ]; then
  printf 'No Source Repository found in workspace: %s\n' "$workspace" >&2
  exit 1
fi

if [ "${#source_repos[@]}" -ne 1 ]; then
  printf 'Source Repository selection is ambiguous in workspace: %s\n' "$workspace" >&2
  exit 1
fi

printf '%s\n' "${source_repos[0]}"