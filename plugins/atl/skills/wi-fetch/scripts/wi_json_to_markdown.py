#!/usr/bin/env python3
"""Convert Jira work item JSON (with ADF description) to Markdown.

Usage:
    python3 wi_json_to_markdown.py '<json_string>'
    echo '<json>' | python3 wi_json_to_markdown.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pyadf2md'))

from pyadf2md.adf2md import adf2md


def convert(wi_json: dict) -> str:
    fields = wi_json.get("fields", wi_json)
    parts = []

    summary = fields.get("summary")
    if summary:
        parts.append(f"# {summary}")

    description = fields.get("description")
    if description:
        content = description.get("content", []) if isinstance(description, dict) else []
        md = adf2md(content)
        if md:
            parts.append(md)

    return "\n\n".join(parts)


def main():
    if len(sys.argv) > 1:
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()

    data = json.loads(raw)
    print(convert(data))


if __name__ == "__main__":
    main()
