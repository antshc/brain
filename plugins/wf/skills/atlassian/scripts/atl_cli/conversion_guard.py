from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from .converter.adf_to_md import adf_to_markdown, render_block
from .converter.md_to_adf import markdown_to_adf
from .converter.blocks import CODE_LANG_ALLOWLIST
from .converter.syntax import syntax_lines
from .converter.table_widths import parse_width_marker
from .converter.patterns import (
    ERROR_MARKER_RE,
    INLINE_CARD_CLOSE_RE,
    INLINE_CARD_OPEN_RE,
    breakout_marker_mark,
    children_marker_params,
    table_marker_attrs,
)

_PROFILE = Path(__file__).resolve().parent.parent / "config" / "confluence-markdown.json"
_WORKER = Path(__file__).with_name("lint_worker.py")


class GuardError(ValueError):
    pass


def lint_markdown(markdown: str) -> None:
    # The API loads ambient config even with --config. A child process gives it an empty
    # working directory without changing the caller's CWD or global library state.
    if not _PROFILE.is_file():
        raise GuardError("Markdown lint configuration missing")
    try:
        with tempfile.TemporaryDirectory(prefix="atl-lint-") as directory:
            result = subprocess.run(
                [sys.executable, str(_WORKER), str(_PROFILE)], input=markdown, text=True,
                capture_output=True, cwd=directory, check=False, timeout=30,
            )
    except (OSError, subprocess.TimeoutExpired) as exception:
        raise GuardError(f"Markdown lint worker failed: {type(exception).__name__}") from None
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise GuardError("Markdown lint worker failed; install scripts/requirements.txt") from None
    if result.returncode or report.get("error"):
        raise GuardError(report.get("error", "Markdown lint worker failed"))
    if report["failures"]:
        raise GuardError("Markdown lint failed: " + "; ".join(report["failures"]))


def _has_code_in_link(line: str) -> bool:
    # Mask code spans first so a literal `[x](y)` inside code is not mistaken for a link.
    masked = re.sub(r"\\.", "  ", line)
    masked = re.sub(r"(`+)(.+?)\1(?!`)", "\0", masked)
    return bool(re.search(r"\[[^\]]*\0[^\]]*\]\(", masked))


def _quote_content(line: str) -> tuple[int, str]:
    depth = 0
    content = line.lstrip()
    while content.startswith(">"):
        depth += 1
        content = content[1:].lstrip()
    return depth, content


def _table_follows_marker(lines: list[tuple[int, str]], index: int, line: str) -> bool:
    marker_depth, _ = _quote_content(line)
    for _, following in lines[index + 1:]:
        depth, content = _quote_content(following)
        if depth != marker_depth:
            if marker_depth or following.strip():
                return False
            continue
        if content:
            return content.startswith("|")
    return False


def validate_markdown(markdown: str, *, placeholders: bool = False, media: bool = False) -> None:
    lines = list(syntax_lines(markdown))
    details = []
    in_fence = None
    for number, raw in enumerate(markdown.splitlines(), 1):
        match = re.match(r"^\s*(`{3,}|~{3,})([^`]*)$", raw)
        if not match:
            continue
        if in_fence is None:
            info = match[2].strip().lower()
            if info and info not in CODE_LANG_ALLOWLIST and not (media and info == "mermaid"):
                raise GuardError(f"line {number}: unsupported code language or info string {info!r}")
            in_fence = match[1]
        elif match[1][0] == in_fence[0] and len(match[1]) >= len(in_fence) and not match[2].strip():
            in_fence = None
    in_list = False
    for index, (number, line) in enumerate(lines):
        if re.match(r"\s*(?:[-*+] |\d+\. )", line):
            in_list = True
        elif line and not line[0].isspace():
            in_list = False
        if line.strip() and markdown.splitlines()[number - 1].startswith("    ") and not in_list:
            raise GuardError(f"line {number}: indented code is unsupported; use a code fence")
        if not media and re.search(r"!\[", line):
            raise GuardError(f"line {number}: image requires the publish-page media pipeline")
        # `syntax_lines` blanks code spans, so this check reads the raw line; fenced lines stay empty.
        if line and _has_code_in_link(markdown.splitlines()[number - 1]):
            raise GuardError(f"line {number}: code span inside a link is not supported; drop the backticks or the link")
        if re.match(r"^\s*\[[^\]]+\]:", line):
            raise GuardError(f"line {number}: reference links are not supported; use inline links")
        if re.fullmatch(r"=+", line.strip()):
            raise GuardError(f"line {number}: setext headings are not supported; use # headings")
        for comment in re.findall(r"<!--.*?-->", line):
            if not re.match(r"<!--\s*(?:/?adf:|media-size:)", comment):
                raise GuardError(f"line {number}: unsupported HTML comment; put literal examples in code")
        if re.search(r"<!--\s*(?:/?adf:|media-size:)", line):
            for comment in re.finditer(r"<!--.*?-->", line):
                tag = comment[0]
                try:
                    table_attrs = table_marker_attrs(tag)
                except ValueError as exception:
                    raise GuardError(f"line {number}: {exception}") from None
                if re.match(r"<!--\s*/?adf:comment\b", tag):
                    if not re.fullmatch(r'<!--\s*(?:adf:comment id="[A-Za-z0-9-]+"|/adf:comment)\s*-->', tag):
                        raise GuardError(f"line {number}: malformed comment anchor")
                elif re.match(r"<!--\s*adf:(?:attachment|diagram)\b", tag):
                    if not placeholders:
                        raise GuardError(f"line {number}: unresolved attachment/diagram placeholder")
                elif re.match(r"<!--\s*adf:error\b", tag):
                    if not placeholders:
                        raise GuardError(
                            f"line {number}: unresolved conversion error (adf:error); "
                            "restore the content and remove the tag and its message before publishing"
                        )
                    if not ERROR_MARKER_RE.fullmatch(tag):
                        raise GuardError(f"line {number}: malformed adf:error tag")
                elif re.match(r"<!--\s*/?adf:inline-card\b", tag):
                    if not (INLINE_CARD_OPEN_RE.fullmatch(tag) or INLINE_CARD_CLOSE_RE.fullmatch(tag)):
                        raise GuardError(f"line {number}: malformed inline-card marker")
                elif re.match(r"<!--\s*(?:media-size:|adf:ignore:(?:start|end))", tag):
                    continue
                elif not (re.fullmatch(r"<!--\s*adf:toc\s*-->", tag) or children_marker_params(tag) is not None or table_attrs or breakout_marker_mark(tag)):
                    raise GuardError(f"line {number}: unsupported or malformed ATL marker")
                if table_attrs is not None or breakout_marker_mark(tag) is not None:
                    is_table = table_attrs is not None
                    attributes = {
                        key.lower(): value
                        for key, value in re.findall(r'([a-z-]+)="([^\"]*)"', tag, re.IGNORECASE if is_table else 0)
                    }
                    allowed = {"layout", "width", "colwidths", "cell-widths", "header-hash", "rows-hash"} if is_table else {"mode", "width"}
                    if attributes.keys() - allowed:
                        raise GuardError(f"line {number}: unsupported marker attribute")
                    if "width" in attributes and not re.fullmatch(r"\d+(?:\.\d+)?", attributes["width"]):
                        raise GuardError(f"line {number}: marker width must be numeric")
                    if is_table:
                        try:
                            parse_width_marker(attributes)
                        except ValueError as exception:
                            raise GuardError(f"line {number}: {exception}") from None
                    if not is_table and attributes.get("mode") not in {"wide", "full-width"}:
                        raise GuardError(f"line {number}: breakout requires mode wide or full-width")
                if table_attrs is not None:
                    if not _table_follows_marker(lines, index, line):
                        raise GuardError(f"line {number}: table marker must precede a table")
                if breakout_marker_mark(tag) is not None:
                    following_raw = next((text for text in markdown.splitlines()[number:] if text.strip()), "")
                    if not re.match(r"\s*(?:<details>|<!--\s*adf:toc|`{3,}|~{3,})", following_raw):
                        raise GuardError(f"line {number}: breakout marker must precede expand, TOC, or code")
            if "-->" not in line:
                raise GuardError(f"line {number}: unterminated ATL marker")
        if line.strip() == "<details>":
            details.append(number)
        elif line.strip() == "</details>":
            if not details:
                raise GuardError(f"line {number}: stray </details>")
            details.pop()
        # The converter only supports these HTML forms. HTML-looking literal text must be escaped.
        for tag in re.findall(r"</?[A-Za-z][^>]*>", re.sub(r"<!--.*?-->", "", line)):
            if not re.fullmatch(r"</?(?:details|summary)>|<br\s*/?>", tag):
                raise GuardError(f"line {number}: unsupported HTML {tag}")
    if details:
        raise GuardError(f"line {details[-1]}: unterminated <details>")


def _merge_text(nodes: list[dict]) -> list[dict]:
    result = []
    for node in nodes:
        if not isinstance(node, dict):
            result.append(node)
            continue
        if node.get("type") == "text" and not node.get("text"):
            continue
        if result and isinstance(result[-1], dict) and node.get("type") == "text" and result[-1].get("type") == "text" and node.get("marks") == result[-1].get("marks"):
            result[-1]["text"] += node["text"]
        else:
            result.append(node)
    return result


_DEFAULTS = {
    "orderedList": {"order": 1},
    "table": {"layout": "default", "isNumberColumnEnabled": False},
    "tableCell": {"colspan": 1, "rowspan": 1},
    "tableHeader": {"colspan": 1, "rowspan": 1},
    "mediaSingle": {"layout": "center", "widthType": "pixel"},
    # Confluence stores every status lozenge with style "bold"; Markdown has no form for it.
    "status": {"style": "bold"},
}


# Confluence stores `bash` as `shell` and the Markdown `text` fence as `plaintext`; other
# languages are compared as written so a real language change stays visible.
_CODE_LANGUAGE_ALIASES = {"shell": "bash", "text": "plaintext"}

_MARKS_EXCLUDED_BY_CODE = {"strong", "em", "strike"}

_BLOCK_CONTAINERS = {"doc", "blockquote", "panel", "expand"}


def _trim_trailing_space(nodes: list) -> None:
    """Markdown strips trailing whitespace of a paragraph; drop it from unmarked text nodes."""
    while nodes and isinstance(nodes[-1], dict) and nodes[-1].get("type") == "text" and not nodes[-1].get("marks"):
        stripped = nodes[-1].get("text", "").rstrip()
        if stripped:
            nodes[-1]["text"] = stripped
            return
        nodes.pop()


def semantic_document(doc: dict, *, transport: bool = False) -> dict:
    """Normalize only named defaults and transport identifiers; keep unknown attributes."""
    def visit(value):
        if isinstance(value, list):
            return _merge_text([visit(item) for item in value])
        if not isinstance(value, dict):
            return value
        node = {key: visit(item) for key, item in value.items()}
        kind = node.get("type")
        attrs = node.get("attrs", {})
        for key, default in _DEFAULTS.get(kind, {}).items():
            if attrs.get(key) == default:
                attrs.pop(key)
        if kind == "doc":
            node.pop("version", None)
            if node.get("content") == [{"type": "paragraph"}]:
                node.pop("content")
        if kind == "codeBlock" and attrs.get("language") in _CODE_LANGUAGE_ALIASES:
            attrs["language"] = _CODE_LANGUAGE_ALIASES[attrs["language"]]
        if kind == "text" and "marks" in node:
            node["marks"] = sorted(node["marks"], key=lambda mark: json.dumps(mark, sort_keys=True))
        attrs.pop("localId", None)
        if kind == "annotation" and attrs.get("annotationType") == "inlineComment":
            attrs.pop("annotationType")
        if transport:
            if kind == "text" and any(mark.get("type") == "code" for mark in node.get("marks", [])):
                # Confluence's schema excludes these marks beside `code` and drops them on store.
                node["marks"] = [mark for mark in node["marks"] if mark.get("type") not in _MARKS_EXCLUDED_BY_CODE]
                if not node["marks"]:
                    node.pop("marks")
            if kind in {"extension", "bodiedExtension", "inlineExtension"} and isinstance(attrs.get("parameters"), dict):
                # Confluence stamps every stored macro with generated metadata and its host page id.
                attrs["parameters"].pop("macroMetadata", None)
                if isinstance(attrs["parameters"].get("macroParams"), dict):
                    attrs["parameters"]["macroParams"].pop("_parentId", None)
            if kind == "media":
                # Uploaded IDs remain stable on read-back of this exact publication.
                attrs.pop("collection", None)
        if attrs:
            node["attrs"] = attrs
        else:
            node.pop("attrs", None)
        if kind in {"paragraph", "heading"} and isinstance(node.get("content"), list):
            _trim_trailing_space(node["content"])
        if kind in _BLOCK_CONTAINERS and isinstance(node.get("content"), list):
            # An empty block paragraph renders to nothing, so it cannot survive a Markdown round trip.
            node["content"] = [
                child for child in node["content"]
                if not (isinstance(child, dict) and child.get("type") == "paragraph" and not child.get("content"))
            ]
        if node.get("content") == []:
            node.pop("content")
        return node
    return visit(copy.deepcopy(doc))


def _difference(expected, actual, path: str = "doc") -> str | None:
    if type(expected) is not type(actual) and not (isinstance(expected, (float, int)) and isinstance(actual, (float, int))):
        return path
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            return path + ".keys"
        return next((difference for key in expected if (difference := _difference(expected[key], actual[key], f"{path}.{key}"))), None)
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return path + ".length"
        return next((difference for index, (left, right) in enumerate(zip(expected, actual)) if (difference := _difference(left, right, f"{path}[{index}]"))), None)
    return path if expected != actual else None


def compare_documents(expected: dict, actual: dict, *, transport: bool = False) -> None:
    difference = _difference(semantic_document(expected, transport=transport), semantic_document(actual, transport=transport))
    if difference:
        raise GuardError(f"conversion changes semantic content at {difference}")


def _is_code_in_link(marks: list[dict]) -> bool:
    kinds = {mark.get("type") for mark in marks}
    return {"link", "code"} <= kinds


def drop_code_in_links(doc: dict) -> dict:
    """Copy of `doc` without the `code` mark on linked text, which Markdown does not carry."""
    def visit(value):
        if isinstance(value, list):
            return [visit(item) for item in value]
        if not isinstance(value, dict):
            return value
        node = {key: visit(item) for key, item in value.items()}
        if node.get("type") == "text" and isinstance(node.get("marks"), list) and _is_code_in_link(node["marks"]):
            node["marks"] = [mark for mark in node["marks"] if mark.get("type") != "code"]
        return node
    return visit(doc)


def check_round_trip(doc: dict, *, fetching: bool = False) -> list[str]:
    projected = copy.deepcopy(doc)
    warnings = []

    def prepare(node: dict) -> dict | list[dict] | None:
        kind = node.get("type")
        attrs = node.get("attrs", {})
        if "marks" in node:
            kept = []
            for mark in node["marks"]:
                if mark.get("type") == "annotation" and mark.get("attrs", {}).get("annotationType", "inlineComment") != "inlineComment":
                    warnings.append("non-comment annotation omitted")
                else:
                    kept.append(mark)
            if _is_code_in_link(kept):
                warnings.append("code inside link omitted")
                kept = [mark for mark in kept if mark.get("type") != "code"]
            if kept:
                node["marks"] = kept
            else:
                node.pop("marks")
        if kind == "table" and not any(cell.get("type") == "tableHeader" for row in node.get("content", []) for cell in row.get("content", [])):
            if not fetching:
                raise GuardError("headerless table cannot be republished losslessly")
            warnings.append("headerless table exported as text; lossless republish unavailable")
            return markdown_to_adf(render_block(node))["content"][0]
        if kind in {"mediaSingle", "mediaGroup", "media", "extension"}:
            if kind in {"mediaSingle", "mediaGroup", "media"}:
                allowed = {"media": {"id", "type", "collection", "alt", "width", "height", "localId"}, "mediaSingle": {"layout", "width", "widthType", "localId"}, "mediaGroup": {"localId"}}[kind]
                if attrs.keys() - allowed:
                    if not fetching:
                        raise GuardError("unsupported media metadata cannot be republished losslessly")
                    warnings.append("unsupported media metadata omitted")
                # Validate nested media metadata before replacing its parent with a placeholder.
                for child in node.get("content", []):
                    prepare(child)
            if kind == "extension" and attrs.get("extensionKey") == "toc":
                return markdown_to_adf("<!-- adf:toc -->")["content"][0]
            # Media has no pure reverse mapping: preserve its exact typed placeholder here.
            return markdown_to_adf(render_block(node))["content"]
        if kind == "expand" and len(node.get("content", [])) == 1 and node["content"][0].get("attrs", {}).get("extensionKey") == "toc":
            result = markdown_to_adf("<!-- adf:toc -->")["content"][0]
            if node.get("marks"):
                result["marks"] = node["marks"]
            return result
        if kind == "inlineExtension" and attrs.get("extensionKey") in {"anchor", "create-from-template"}:
            warnings.append("inline extension omitted: " + attrs["extensionKey"])
            return None
        if kind == "table" and any(c.get("attrs", {}).get(key, 1) != 1 for row in node.get("content", []) for c in row.get("content", []) for key in ("colspan", "rowspan")):
            if not fetching:
                raise GuardError("table spans cannot be republished losslessly")
            warnings.append("table spans flattened; lossless republish unavailable")
            return markdown_to_adf(render_block(node))["content"][0]
        if kind in {"tableCell", "tableHeader"} and any(attrs.get(key, 1) != 1 for key in ("rowspan", "colspan")):
            raise GuardError("table spans cannot be republished losslessly")
        if "content" in node:
            children = []
            for child in node["content"]:
                item = prepare(child)
                if isinstance(item, list):
                    children.extend(item)
                elif item is not None:
                    children.append(item)
            node["content"] = children
        return node

    projected = prepare(projected)
    rendered = adf_to_markdown(projected)
    reparsed = markdown_to_adf(rendered)
    compare_documents(projected, reparsed)
    canonical = adf_to_markdown(reparsed)
    if adf_to_markdown(markdown_to_adf(canonical)) != canonical:
        raise GuardError("Markdown conversion does not reach a stable fixed point")
    if any("omitted" in warning for warning in warnings) and not fetching:
        raise GuardError("lossy conversion: " + "; ".join(sorted(set(warnings))))
    return sorted(set(warnings))


def guard_adf(doc: dict, *, fetching: bool = False) -> list[str]:
    if not isinstance(doc, dict) or doc.get("type") != "doc":
        raise GuardError("ADF body must be a parsed JSON object with type doc")
    if doc.get("version", 1) != 1:
        raise GuardError("ADF version must be 1")
    def validate_node(node: dict) -> None:
        if not isinstance(node, dict) or not isinstance(node.get("type"), str):
            raise GuardError("ADF node must have a string type")
        if not isinstance(node.get("attrs", {}), dict) or not isinstance(node.get("marks", []), list):
            raise GuardError("ADF attrs must be an object and marks a list")
        if node.get("type") == "text" and not isinstance(node.get("text"), str):
            raise GuardError("ADF text must be a string")
        for mark in node.get("marks", []):
            if not isinstance(mark, dict) or not isinstance(mark.get("type"), str) or not isinstance(mark.get("attrs", {}), dict):
                raise GuardError("ADF mark must have a string type and object attrs")
        if not isinstance(node.get("content", []), list):
            raise GuardError("ADF content must be a list")
        for child in node.get("content", []):
            validate_node(child)
    validate_node(doc)
    return check_round_trip(doc, fetching=fetching)
