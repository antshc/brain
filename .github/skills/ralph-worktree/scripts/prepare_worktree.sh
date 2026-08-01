#!/usr/bin/env bash
set -eu

if [ "$#" -ne 3 ]; then
  printf 'Usage: %s <harness-root> <target-branch> <feature-branch>\n' "$0" >&2
  exit 64
fi

harness_root=$(cd "$1" && pwd -P)
target_branch=$2
feature_branch=$3
source_repo="$("$(dirname "$0")/resolve_source_repository.sh" "$harness_root")"

worktree_path="$source_repo.worktrees/$feature_branch"
actualize_worktree=false
if [ "$(git -C "$source_repo" branch --show-current)" = "$feature_branch" ]; then
  worktree_path=$source_repo
  actualize_worktree=true
elif [ ! -d "$worktree_path" ]; then
  mkdir -p "$source_repo.worktrees"
  git -C "$source_repo" fetch --all --prune --quiet
  git -C "$source_repo" worktree add --quiet -b "$feature_branch" "$worktree_path" "origin/$target_branch" >/dev/null
else
  actualize_worktree=true
fi

if [ "$actualize_worktree" = true ]; then
  git -C "$worktree_path" rev-parse --is-inside-work-tree >/dev/null
  git -C "$worktree_path" fetch --all --prune --quiet
  if ! git -C "$worktree_path" merge "origin/$target_branch" >/dev/null; then
    printf 'SOURCE_REPO: %s\nWORKTREE_PATH: %s\nBRANCH: %s\nTARGET_BRANCH: %s\nMERGE_CONFLICTS:\n%s\n' "$source_repo" "$worktree_path" "$feature_branch" "$target_branch" "$(git -C "$worktree_path" diff --name-only --diff-filter=U)"
    exit 3
  fi
fi

printf 'SOURCE_REPO: %s\nWORKTREE_PATH: %s\nBRANCH: %s\nTARGET_BRANCH: %s\n' "$source_repo" "$worktree_path" "$feature_branch" "$target_branch"