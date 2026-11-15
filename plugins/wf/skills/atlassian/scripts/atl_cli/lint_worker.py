from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        from pymarkdown.api import PyMarkdownApi, PyMarkdownApiException
    except ImportError:
        print(json.dumps({"error": "pymarkdownlnt missing; install scripts/requirements.txt"}))
        return 1
    try:
        source = sys.stdin.read()
        result = PyMarkdownApi().configuration_file_path(sys.argv[1]).scan_string(source if source.strip() else "<!-- empty document -->\n")
    except PyMarkdownApiException:
        print(json.dumps({"error": "PyMarkdown configuration or scan failed"}))
        return 1
    failures = [
        f"line {item.line_number}, column {item.column_number}: {item.rule_id} {item.rule_description}"
        for item in result.scan_failures
    ]
    failures.extend(f"line {item.line_number}: invalid lint pragma" for item in result.pragma_errors)
    failures.extend("PyMarkdown critical error" for _ in result.critical_errors)
    print(json.dumps({"failures": failures}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
