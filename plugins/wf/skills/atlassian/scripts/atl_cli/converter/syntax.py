from __future__ import annotations

import re


def syntax_lines(markdown: str):
    fence = None
    for number, line in enumerate(markdown.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})([^`]*)$", line)
        if match:
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not match[2].strip():
                fence = None
            yield number, ""
            continue
        if fence:
            yield number, ""
            continue
        # A code span (including an ATL marker example) is literal, as are escapes.
        line = re.sub(r"(`+).*?\1(?!`)", lambda m: " " * len(m[0]), line)
        line = re.sub(r"\\.", lambda m: " " * len(m[0]), line)
        yield number, line
    if fence:
        raise ValueError("unterminated code fence")
