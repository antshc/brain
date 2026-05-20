#!/bin/bash

# Usage: ./diff-for-review.sh <base-branch>
# Example: ./diff-for-review.sh release/10.9

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <base-branch>"
    echo "Example: $0 release/10.9"
    exit 1
fi

BASE_BRANCH="origin/$1"
REVIEW_DIR="bin/review_diff"

# Find the common ancestor commit
echo "Finding common ancestor between HEAD and $BASE_BRANCH..."
ANCESTOR=$(git merge-base HEAD "$BASE_BRANCH")
echo "Common ancestor commit: $ANCESTOR"

# Create review directory if it doesn't exist
mkdir -p "$REVIEW_DIR"

# Clean up old diff files
rm -f "$REVIEW_DIR"/*_diff.txt

# Get list of changed files
CHANGED_FILES=$(git diff --name-only "$ANCESTOR" HEAD)

if [ -z "$CHANGED_FILES" ]; then
    echo "No files changed between $ANCESTOR and HEAD"
    exit 0
fi

echo "Changed files:"
echo "$CHANGED_FILES"
echo ""

# Diff each file and save to review directory
for file in $CHANGED_FILES; do
    # Replace slashes with underscores for the filename
    safe_name=$(echo "$file" | tr '/' '_')
    output_file="$REVIEW_DIR/${safe_name}_diff.txt"
    
    echo "Saving diff for: $file -> $output_file"
    git diff "$ANCESTOR" HEAD -- "$file" > "$output_file"
done

echo ""
echo "Done! Diff files saved to $REVIEW_DIR/"
echo "Total files: $(echo "$CHANGED_FILES" | wc -l)"
