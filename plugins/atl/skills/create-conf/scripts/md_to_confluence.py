"""
Create a Confluence page from a local Markdown file.

Usage:
    python3 md_to_confluence.py --file <path.md> --parent-id <id> --space <space_key>

Environment variables required:
    ACLI_EMAIL       - Atlassian account email
    ACLI_API_TOKEN   - Atlassian API token
    ACLI_SITE        - Atlassian site (e.g. zerto.atlassian.net)
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error

import markdown


def extract_title(md_text: str) -> str:
    """Extract the first H1 heading from markdown text."""
    for line in md_text.splitlines():
        match = re.match(r'^#\s+(.+)', line)
        if match:
            return match.group(1).strip()
    raise ValueError("No H1 heading found in the markdown file. Add a '# Title' line.")


def md_to_html(md_text: str) -> str:
    """Convert markdown text to HTML."""
    return markdown.markdown(md_text, extensions=['tables', 'fenced_code'])


def create_page(site: str, email: str, token: str, space: str, parent_id: str, title: str, html: str) -> dict:
    """POST to Confluence REST API and return the response JSON."""
    url = f"https://{site}/wiki/rest/api/content"
    payload = json.dumps({
        "type": "page",
        "title": title,
        "ancestors": [{"id": parent_id}],
        "space": {"key": space},
        "body": {
            "storage": {
                "value": html,
                "representation": "storage",
            }
        },
    }).encode()

    creds = base64.b64encode(f"{email}:{token}".encode()).decode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {creds}",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def main():
    parser = argparse.ArgumentParser(description="Create a Confluence page from a Markdown file.")
    parser.add_argument("--file", required=True, help="Path to the local Markdown file")
    parser.add_argument("--parent-id", required=True, help="Numeric ID of the parent Confluence page")
    parser.add_argument("--space", required=True, help="Confluence space key")
    args = parser.parse_args()

    email = os.environ.get("ACLI_EMAIL")
    token = os.environ.get("ACLI_API_TOKEN")
    site = os.environ.get("ACLI_SITE")

    if not all([email, token, site]):
        print("ERROR: ACLI_EMAIL, ACLI_API_TOKEN, and ACLI_SITE must be set in the environment.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file, encoding="utf-8") as f:
            md_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        title = extract_title(md_text)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    html = md_to_html(md_text)

    try:
        result = create_page(site, email, token, args.space, args.parent_id, title, html)
    except RuntimeError as e:
        print(f"ERROR: Failed to create page: {e}", file=sys.stderr)
        sys.exit(1)

    page_url = f"https://{site}/wiki{result['_links']['webui']}"
    print(f"Created: {result['title']}")
    print(f"URL: {page_url}")


if __name__ == "__main__":
    main()
