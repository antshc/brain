# Convert a Confluence page view JSON response to GitHub Markdown.
# Requires: pip install markdownify
#
# Usage:
#   # Pass JSON as a positional argument:
#   python3 page_view_json_to_markdown.py "$(cat page_response.json)"
#
#   # Pipe JSON via stdin:
#   cat page_response.json | python3 page_view_json_to_markdown.py

import argparse
import json
import sys

from markdownify import markdownify


def convert_to_markdown(html_value: str) -> str:
    return markdownify(html_value, heading_style='ATX', code_language='').strip()


def main():
    arg_parser = argparse.ArgumentParser(
        description='Convert a Confluence page view JSON response to GitHub Markdown.'
    )
    arg_parser.add_argument(
        'page_response',
        nargs='?',
        help='Confluence page JSON response. Pass as a string argument or pipe via stdin.',
    )
    args = arg_parser.parse_args()

    if args.page_response:
        raw = args.page_response
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        arg_parser.error('Provide page_response as an argument or pipe it via stdin.')

    data = json.loads(raw)
    html_value = data['body']['view']['value']
    print(convert_to_markdown(html_value))


if __name__ == '__main__':
    main()
