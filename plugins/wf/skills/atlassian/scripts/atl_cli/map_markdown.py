"""`map-markdown`: the single boundary for Markdown <-> Atlassian Document Format conversion.
Offline; guarded CLI uses a packaged lint profile, with no network or Atlassian dependency.

Usage:
    atl.py map-markdown md-to-adf        < input.md   > output.json
    atl.py map-markdown adf-to-md        < input.json > output.md
    atl.py map-markdown detect-adf-only  < input.md   > report.json

Other commands call `md_to_adf`/`adf_to_md` in-process; both raise `ConversionError` carrying
the same `<reason>` the CLI prints as `error: <reason>`.
"""
from __future__ import annotations

import argparse
import json
import sys

from .converter.adf_to_md import (
    ConversionIssue,
    adf_to_markdown,
    adf_to_markdown_tolerant,
    issue_line,
    new_issue,
    render_issue_section,
)
from .converter.detect import detect_adf_only
from .converter.md_to_adf import markdown_to_adf
from .converter.patterns import ERROR_MARKER_RE
from .converter.syntax import syntax_lines

DOC_NODE = "doc"


class ConversionError(Exception):
    """The converter rejected its input; the message is the reason only, never a traceback."""


def md_to_adf(markdown: str, *, guarded: bool = False) -> dict:
    try:
        reject_conversion_errors(markdown)
        if guarded:
            from .conversion_guard import guard_adf, lint_markdown, validate_markdown
            from .page_diagrams.patterns import strip_ignored_sections
            markdown = strip_ignored_sections(markdown)
            validate_markdown(markdown)
            lint_markdown(markdown)
        doc = markdown_to_adf(markdown)
        if guarded:
            guard_adf(doc)
        return doc
    except (ValueError, NotImplementedError) as exception:
        raise ConversionError(str(exception)) from None


def adf_to_md(doc: object, *, guarded: bool = False) -> str:
    """ADF document -> Markdown, newline-terminated exactly like the CLI's stdout."""
    try:
        if guarded:
            from .conversion_guard import drop_code_in_links, guard_adf, lint_markdown, validate_markdown
            for warning in guard_adf(doc, fetching=True):
                print(f"warning: {warning}", file=sys.stderr)
            doc = drop_code_in_links(doc)
        markdown = adf_to_markdown(doc) + "\n"
        if guarded:
            validate_markdown(markdown, placeholders=True)
            lint_markdown(markdown)
        return markdown
    except (ValueError, NotImplementedError) as exception:
        raise ConversionError(str(exception)) from None


def reject_conversion_errors(markdown: str) -> None:
    """A fetched file still carrying an `adf:error` tag lost content; never publish it."""
    for number, line in syntax_lines(markdown):
        match = ERROR_MARKER_RE.search(line)
        if match:
            raise ValueError(
                f'line {number}: unresolved conversion error {match["error_id"]} (adf:error); '
                "restore the content and remove the tag and its message before publishing"
            )


def adf_to_md_tolerant(doc: object, *, guarded: bool = False) -> tuple[str, list[ConversionIssue]]:
    """ADF -> Markdown for fetches: never raises on content it cannot convert.

    Each unconvertible node becomes an in-place `adf:error` line; guard failures and lossy-export
    warnings become document-level (`node="doc"`) issues. Finish with `append_conversion_issues`.
    """
    issues: list[ConversionIssue] = []
    if not isinstance(doc, dict):
        new_issue(issues, DOC_NODE, f"ADF body must be a parsed JSON object, got {type(doc).__name__}")
        return "", issues
    source = doc
    if guarded:
        from .conversion_guard import drop_code_in_links
        doc = drop_code_in_links(doc)
    markdown, issues = adf_to_markdown_tolerant(doc)
    if guarded:
        from .conversion_guard import guard_adf
        try:
            warnings = guard_adf(source, fetching=True)
        except (ValueError, NotImplementedError, AttributeError, TypeError) as exception:
            # Node issues already explain a guard failure caused by the same nodes.
            if not issues:
                new_issue(issues, DOC_NODE, f"conversion check failed: {exception}")
        else:
            if warnings:
                new_issue(issues, DOC_NODE, "lossy conversion: " + "; ".join(warnings))
    return markdown + "\n", issues


def append_conversion_issues(markdown: str, issues: list[ConversionIssue]) -> str:
    """Append document-level issue lines and the ignored `## Conversion errors` section."""
    if not issues:
        return markdown
    doc_lines = [issue_line(issue) for issue in issues if issue.node == DOC_NODE]
    parts = [markdown.rstrip("\n")] if markdown.strip() else []
    if doc_lines:
        parts.append("\n\n".join(doc_lines))
    parts.append(render_issue_section(issues))
    return "\n\n".join(parts) + "\n"


def report_conversion_issues(issues: list[ConversionIssue], destination: str) -> None:
    if issues:
        print(
            f"warning: {len(issues)} conversion error(s) tagged with adf:error in {destination}; "
            "see its '## Conversion errors' section",
            file=sys.stderr,
        )


def main(argv: list[str] | None = None, *, prog: str | None = None) -> int:
    parser = argparse.ArgumentParser(prog=prog, description="Convert between Markdown and Atlassian Document Format.")
    subparsers = parser.add_subparsers(dest="direction", required=True)
    subparsers.add_parser("md-to-adf", help="Markdown (stdin) -> ADF JSON (stdout)")
    subparsers.add_parser("adf-to-md", help="ADF JSON (stdin) -> Markdown (stdout)")
    subparsers.add_parser("detect-adf-only", help="Markdown (stdin) -> ADF-only construct report (stdout)")
    args = parser.parse_args(argv)

    source = sys.stdin.read()

    try:
        if args.direction == "md-to-adf":
            doc = md_to_adf(source, guarded=True)
            json.dump(doc, sys.stdout, indent=2)
            sys.stdout.write("\n")
        elif args.direction == "detect-adf-only":
            constructs = detect_adf_only(source)
            json.dump({"adfOnly": bool(constructs), "constructs": constructs}, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            doc = json.loads(source)
            sys.stdout.write(adf_to_md(doc, guarded=True))
    except (ConversionError, ValueError, NotImplementedError) as exception:
        print(f"error: {exception}", file=sys.stderr)
        return 1

    return 0
