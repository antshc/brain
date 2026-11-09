"""Capability catalogue for the atl Confluence round-trip regression: one check per
`map-markdown-adf`, `publish-page`, and `fetch-page` capability, evaluated against the artifacts
a real run leaves in its run directory (pure, offline)."""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

INLINE_ANCHOR_TEXT = "regression anchor phrase"
INLINE_COMMENT_BODY = "Regression inline comment"
FOOTER_COMMENT_BODY = "Regression footer comment"
IGNORED_TEXT = "LOCAL-ONLY-NOTE"
IMAGE_NAME = "regression-image.png"
FILE_NAME = "regression-notes.txt"
DIAGRAM_IDS = ("regression-flow", "regression-sequence")

_COMMENTS_SECTION_RE = re.compile(r"\n*<!-- adf:ignore:start -->\n## Comments.*\Z", re.DOTALL)
_ASSETS_DIR_RE = re.compile(r"fetched-\d+\.md\.assets/")
_ANCHOR_RE = re.compile(
    r'<!-- adf:comment id="[^"]+" -->' + re.escape(INLINE_ANCHOR_TEXT) + r"<!-- /adf:comment -->"
)


@dataclass(frozen=True)
class Artifacts:
    """What a run leaves behind; `None` marks an artifact the run has not produced yet."""

    title: str
    run_dir: Path
    publish_1: dict | None = None
    fetched_1: str | None = None
    publish_2: dict | None = None
    fetched_2: str | None = None


@dataclass(frozen=True)
class Capability:
    id: str
    area: str
    title: str
    needs: tuple[str, ...]
    check: Callable[[Artifacts], str | None] = field(repr=False)


@dataclass(frozen=True)
class Outcome:
    capability: Capability
    status: str  # "pass" | "fail" | "skipped"
    detail: str


def body(markdown: str) -> str:
    """Fetched Markdown without the trailing `## Comments` block, asset dirs normalized."""
    return _ASSETS_DIR_RE.sub("ASSETS/", _COMMENTS_SECTION_RE.sub("", markdown)).rstrip() + "\n"


def comments_section(markdown: str) -> str:
    match = _COMMENTS_SECTION_RE.search(markdown)
    return match.group(0) if match else ""


def _contains(artifact: str, *snippets: str) -> Callable[[Artifacts], str | None]:
    def check(artifacts: Artifacts) -> str | None:
        text = body(getattr(artifacts, artifact))
        missing = [snippet for snippet in snippets if snippet not in text]
        return f"missing: {missing[0]!r}" if missing else None

    return check


def _ordered(artifact: str, *snippets: str) -> Callable[[Artifacts], str | None]:
    def check(artifacts: Artifacts) -> str | None:
        text = body(getattr(artifacts, artifact))
        position = 0
        for snippet in snippets:
            found = text.find(snippet, position)
            if found < 0:
                return f"missing or out of order: {snippet!r}"
            position = found + len(snippet)
        return None

    return check


def _title_heading(artifacts: Artifacts) -> str | None:
    lines = artifacts.fetched_1.splitlines()
    if not lines or lines[0] != f"# {artifacts.title}":
        return f"first line is {lines[0]!r}" if lines else "empty page"
    if artifacts.fetched_1.count(f"# {artifacts.title}\n") != 1:
        return "title heading duplicated"
    return None


def _ignored_block_absent(artifacts: Artifacts) -> str | None:
    return "ignored block reached Confluence" if IGNORED_TEXT in artifacts.fetched_1 else None


def _publish_created(artifacts: Artifacts) -> str | None:
    result = artifacts.publish_1
    if result.get("method") != "rest" or not result.get("pageId"):
        return f"unexpected publish result: {result}"
    if result.get("title") != artifacts.title:
        return f"title {result.get('title')!r} != {artifacts.title!r}"
    return None


def _publish_diagrams(artifacts: Artifacts) -> str | None:
    count = artifacts.publish_1.get("diagrams")
    return None if count == len(DIAGRAM_IDS) else f"diagrams={count}, expected {len(DIAGRAM_IDS)}"


def _publish_attachments(artifacts: Artifacts) -> str | None:
    count = artifacts.publish_1.get("attachments", 0)
    minimum = len(DIAGRAM_IDS) + 2
    return None if count >= minimum else f"attachments={count}, expected >= {minimum}"


def _diagram(diagram_id: str, first_line: str) -> Callable[[Artifacts], str | None]:
    return _contains("fetched_1", f"```mermaid\n%% diagram-id: {diagram_id}\n{first_line}")


def _cached(artifacts: Artifacts, name: str) -> Path:
    return artifacts.run_dir / "fetched-1.md.assets" / name


def _image(artifacts: Artifacts) -> str | None:
    text = body(artifacts.fetched_1)
    if not re.search(rf"!\[{re.escape(IMAGE_NAME)}\]\(ASSETS/{re.escape(IMAGE_NAME)}\)\n<!-- media-size: width=\d+ height=\d+ display-width=48 layout=align-start -->", text):
        return "image reference with media-size (display-width=48, layout=align-start) not found"
    source = artifacts.run_dir / "assets" / IMAGE_NAME
    cached = _cached(artifacts, IMAGE_NAME)
    if not cached.is_file() or cached.read_bytes() != source.read_bytes():
        return "cached image missing or differs from source"
    return None


def _file(artifacts: Artifacts) -> str | None:
    if f"[{FILE_NAME}](ASSETS/{FILE_NAME})" not in body(artifacts.fetched_1):
        return "file link not found"
    cached = _cached(artifacts, FILE_NAME)
    if not cached.is_file() or cached.read_bytes() != (artifacts.run_dir / "assets" / FILE_NAME).read_bytes():
        return "cached file missing or differs from source"
    return None


def _anchor(artifact: str) -> Callable[[Artifacts], str | None]:
    def check(artifacts: Artifacts) -> str | None:
        return None if _ANCHOR_RE.search(getattr(artifacts, artifact)) else "inline-comment anchor not found"

    return check


def _comments_listed(artifacts: Artifacts) -> str | None:
    section = comments_section(artifacts.fetched_1)
    expected = ("## Comments", "### Page comment", 'anchored as `id="', INLINE_COMMENT_BODY, FOOTER_COMMENT_BODY, "<!-- adf:ignore:end -->")
    missing = [text for text in expected if text not in section]
    return f"comments section missing {missing[0]!r}" if missing else None


def _republish_in_place(artifacts: Artifacts) -> str | None:
    first, second = artifacts.publish_1, artifacts.publish_2
    if second.get("method") != "rest" or second.get("pageId") != first.get("pageId"):
        return f"update went to {second.get('pageId')!r}, expected {first.get('pageId')!r}"
    return None


def _no_detached_comments(artifacts: Artifacts) -> str | None:
    result = artifacts.publish_2
    for key in ("orphanedComments", "unknownCommentIds", "commentGuard"):
        if result.get(key):
            return f"{key}={result[key]}"
    return None


def _republish_diagrams(artifacts: Artifacts) -> str | None:
    count = artifacts.publish_2.get("diagrams")
    return None if count == len(DIAGRAM_IDS) else f"diagrams={count}, expected {len(DIAGRAM_IDS)}"


def _idempotent(artifacts: Artifacts) -> str | None:
    first, second = body(artifacts.fetched_1).splitlines(), body(artifacts.fetched_2).splitlines()
    for number, (a, b) in enumerate(zip(first, second), start=1):
        if a != b:
            return f"line {number}: {a!r} != {b!r}"
    return None if len(first) == len(second) else f"line count {len(first)} != {len(second)}"


F1 = ("fetched_1",)
CAPABILITIES: tuple[Capability, ...] = (
    Capability("P01", "Publish", "Page created over REST with the H1 as title", ("publish_1",), _publish_created),
    Capability("P02", "Publish", "Both mermaid diagrams rendered", ("publish_1",), _publish_diagrams),
    Capability("P03", "Publish", "Diagrams and local files uploaded as attachments", ("publish_1",), _publish_attachments),
    Capability("F01", "Fetch", "Title re-added once as `# <title>`", F1, _title_heading),
    Capability("F02", "Fetch", "`adf:ignore` block never published", F1, _ignored_block_absent),
    Capability("M01", "Structure", "TOC macro (`<!-- adf:toc -->`)", F1, _contains("fetched_1", "<!-- adf:toc -->")),
    Capability("M02", "Structure", "Headings level 2 to 6", F1, _contains("fetched_1", "## Inline Marks", "### Heading Level Three", "#### Heading Level Four", "##### Heading Level Five", "###### Heading Level Six")),
    Capability("M03", "Marks", "strong, em, code, link, strike", F1, _contains("fetched_1", "**strong text**", "*emphasis text*", "`inline code`", "[plain link](https://example.com/plain)", "~~struck text~~")),
    Capability("M04", "Marks", "Code span inside link", F1, _contains("fetched_1", "[`Foo.Bar`](https://example.com/code-link)")),
    Capability("M05", "Marks", "Strong + link merged on one node", F1, _contains("fetched_1", "[**bold link**](https://example.com/bold-link)")),
    Capability("M06", "Marks", "Partly marked link label keeps the link", F1, _contains("fetched_1", "[label with ](https://example.com/partial)[**bold part**](https://example.com/partial)[ inside](https://example.com/partial)")),
    Capability("M07", "Inline", "Emoji status lozenges, all six colors", F1, _contains("fetched_1", "⚪[Neutral] 🟣[Purple] 🔵[Blue] 🔴[Red] 🟡[Yellow] 🟢[In Progress]")),
    Capability("M08", "Inline", "Legacy `[STATUS:...]` input comes back as emoji status, default neutral", F1, _contains("fetched_1", "⚪[Legacy Default] 🟢[Legacy Green]")),
    Capability("L01", "Lists", "Nested bullet list", F1, _contains("fetched_1", "- bullet alpha\n- bullet beta\n  - nested bullet gamma\n    - deep bullet delta")),
    Capability("L02", "Lists", "Soft-wrapped list item folded into one line", F1, _contains("fetched_1", "- bullet epsilon with a soft wrapped continuation line")),
    Capability("L03", "Lists", "Ordered list keeps its start number", F1, _contains("fetched_1", "3. ordered three\n4. ordered four")),
    Capability("L04", "Lists", "Bullet nested in an ordered item", F1, _contains("fetched_1", "- mixed nested bullet")),
    Capability("L05", "Lists", "Table under a list item moved after the list", F1, _ordered("fetched_1", "- list item owning a table", "| Moved Col A | Moved Col B |", "| moved one | moved two |")),
    Capability("B01", "Blocks", "Blockquote", F1, _contains("fetched_1", "> Quoted line for the blockquote check.")),
    Capability("B02", "Blocks", "Panels info, note, warning, success, error", F1, _contains("fetched_1", "> [!INFO]\n> Info panel text.", "> [!NOTE]\n> Note panel text.", "> [!WARNING]\n> Warning panel text.", "> [!SUCCESS]\n> Success panel text.", "> [!ERROR]\n> Error panel text.")),
    Capability("B03", "Blocks", "Code blocks: python, bash, plaintext, no language", F1, _contains("fetched_1", "```python\ndef regression_python():\n    return 42\n```", "```bash\necho regression-bash\n```", "```\nplain fenced block without language\n```", "```plaintext\nplaintext fenced block\n```")),
    Capability("B04", "Blocks", "Horizontal rule", F1, _contains("fetched_1", "\n---\n")),
    Capability("B05", "Blocks", "Expand from `<details>` with nested content", F1, _contains("fetched_1", "<details>\n<summary>Expandable Section Title</summary>", "Hidden paragraph inside the expand.", "- hidden bullet two\n</details>")),
    Capability("B06", "Blocks", "Expand keeps its wide breakout width", F1, _contains("fetched_1", '<!-- adf:breakout mode="wide" width="760" -->\n<details>\n<summary>Wide Expandable Section</summary>')),
    Capability("B07", "Blocks", "Code block keeps its wide breakout width", F1, _contains("fetched_1", '<!-- adf:breakout mode="wide" width="1000" -->\n```python\nprint("wide code block")')),
    Capability("T01", "Tables", "Table with header row", F1, _contains("fetched_1", "| Header A | Header B |\n| --- | --- |\n| cell a1 | cell b1 |")),
    Capability("T02", "Tables", "`<br>` hard break inside a cell", F1, _contains("fetched_1", "| multi line<br>cell a2 | cell b2 |")),
    Capability("T03", "Tables", "Wide table layout", F1, _contains("fetched_1", "<!-- adf:wide-table -->\n\n| Wide Header A | Wide Header B | Wide Header C |")),
    Capability("T04", "Tables", "Table keeps layout and fixed width", F1, _contains("fetched_1", '<!-- adf:table layout="wide" width="960" -->\n\n| Sized Header A | Sized Header B |')),
    Capability("D01", "Diagrams", "Flowchart restored from its sidecar with its id", F1, _diagram("regression-flow", "flowchart TD")),
    Capability("D02", "Diagrams", "Sequence diagram restored from its sidecar with its id", F1, _diagram("regression-sequence", "sequenceDiagram")),
    Capability("A01", "Attachments", "Local image keeps natural size, display width, layout, and identical bytes", F1, _image),
    Capability("A02", "Attachments", "Local file round-trips as a link with identical bytes", F1, _file),
    Capability("C01", "Comments", "Inline-comment anchor wraps its selection", F1, _anchor("fetched_1")),
    Capability("C02", "Comments", "`## Comments` lists the anchored inline thread and the footer thread in an ignore block", F1, _comments_listed),
    Capability("R01", "Republish", "Fetched Markdown republishes in place", ("publish_1", "publish_2"), _republish_in_place),
    Capability("R02", "Republish", "Republish detaches no comment and reports no unknown id", ("publish_2",), _no_detached_comments),
    Capability("R03", "Republish", "Diagrams replaced in place on republish", ("publish_2",), _republish_diagrams),
    Capability("R04", "Republish", "Second fetch identical to the first (Confluence -> Markdown -> Confluence stable)", ("fetched_1", "fetched_2"), _idempotent),
    Capability("R05", "Republish", "Inline-comment anchor survives republish", ("fetched_2",), _anchor("fetched_2")),
)


def evaluate(artifacts: Artifacts) -> list[Outcome]:
    outcomes = []
    for capability in CAPABILITIES:
        absent = [name for name in capability.needs if getattr(artifacts, name) is None]
        if absent:
            outcomes.append(Outcome(capability, "skipped", f"artifact not produced: {', '.join(absent)}"))
            continue
        failure = capability.check(artifacts)
        outcomes.append(Outcome(capability, "fail" if failure else "pass", failure or "verified"))
    return outcomes
