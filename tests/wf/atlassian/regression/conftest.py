from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[4] / "plugins" / "wf" / "skills" / "atlassian"
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
ATL_PY = SKILL_DIR / "scripts" / "atl.py"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from capabilities import (  # noqa: E402
    FOOTER_COMMENT_BODY,
    INLINE_ANCHOR_TEXT,
    INLINE_COMMENT_BODY,
)
from atl_cli.map_markdown import adf_to_md_tolerant, append_conversion_issues  # noqa: E402
from regression import build_degraded_adf, init_run  # noqa: E402

_IGNORED_RE = re.compile(r"<!-- adf:ignore:start -->.*?<!-- adf:ignore:end -->\n*", re.DOTALL)


def _convert(command: str, text: str) -> str:
    return subprocess.run(
        [sys.executable, str(ATL_PY), "map-markdown", command], input=text, capture_output=True, text=True, check=True
    ).stdout


def simulate_fetch(page_md: str, fetch_number: int) -> str:
    """What `publish-page` then `fetch-page` return for the fixture, built from the real
    `map-markdown-adf` round trip plus fetch-page's documented substitutions (mermaid fence from
    the sidecar, cached attachment links, inline anchor from the twg comment, `## Comments`)."""
    published = _IGNORED_RE.sub("", page_md)
    # Media-size belongs to the full media pipeline, not the pure text converter.
    media_sizes = re.findall(r"(!\[[^\]]+\]\([^)]+\))\n(<!-- media-size:.*?-->)", published)
    published = re.sub(r"^<!-- media-size:.*?-->\n?", "", published, flags=re.MULTILINE)
    diagrams = re.findall(r"```mermaid\n.*?\n```", published, re.DOTALL)
    for index, diagram in enumerate(diagrams):
        published = published.replace(diagram, f"ATL-DIAGRAM-{index}")
    images = re.findall(r"!\[[^\]]+\]\([^)]+\)", published)
    for index, image in enumerate(images):
        published = published.replace(image, f"ATL-IMAGE-{index}")
    markdown = _convert("adf-to-md", _convert("md-to-adf", published))
    for index, diagram in enumerate(diagrams):
        markdown = markdown.replace(f"ATL-DIAGRAM-{index}", diagram)
    for index, image in enumerate(images):
        markdown = markdown.replace(f"ATL-IMAGE-{index}", image)
    for image, size in media_sizes:
        markdown = markdown.replace(image, image + "\n" + size)
    markdown = markdown.replace("```\n%% diagram-id:", "```mermaid\n%% diagram-id:")
    markdown = markdown.replace("](assets/", f"](fetched-{fetch_number}.md.assets/")
    markdown = markdown.replace(") <!-- media-size:", ")\n<!-- media-size:")
    markdown = markdown.replace(
        INLINE_ANCHOR_TEXT, f'<!-- adf:comment id="anchor-1" -->{INLINE_ANCHOR_TEXT}<!-- /adf:comment -->'
    )
    comments = "\n".join(
        [
            "<!-- adf:ignore:start -->",
            "## Comments",
            "",
            "Read-only snapshot.",
            "",
            f'### Inline on "{INLINE_ANCHOR_TEXT}" — open, anchored as `id="anchor-1"`',
            "",
            f"- **Tester** (2026-10-31): {INLINE_COMMENT_BODY}",
            "",
            "### Page comment",
            "",
            f"- **Tester** (2026-10-31): {FOOTER_COMMENT_BODY}",
            "<!-- adf:ignore:end -->",
        ]
    )
    return f"{markdown.rstrip()}\n\n{comments}\n"


@pytest.fixture
def simulated_run(tmp_path) -> Path:
    """A complete run directory whose artifacts mirror a healthy live run."""
    run = init_run("TEST", tmp_path, now=datetime(2026, 10, 31, tzinfo=timezone.utc))
    run_dir = Path(run["runDir"])
    page_md = (run_dir / "page.md").read_text(encoding="utf-8")
    publish = {"method": "rest", "pageId": "42", "title": run["title"], "diagrams": 2, "attachments": 6, "renderer": "png"}
    for number in (1, 2):
        (run_dir / f"publish-{number}.json").write_text(json.dumps(publish), encoding="utf-8")
        (run_dir / f"fetched-{number}.md").write_text(simulate_fetch(page_md, number), encoding="utf-8")
        shutil.copytree(run_dir / "assets", run_dir / f"fetched-{number}.md.assets")

    degraded_adf = build_degraded_adf({"type": "doc", "version": 1, "content": []}, "regression-user")
    degraded_markdown, issues = adf_to_md_tolerant(degraded_adf, guarded=True)
    degraded = append_conversion_issues(degraded_markdown, issues)
    (run_dir / "fetched-degraded.md").write_text(degraded, encoding="utf-8")
    (run_dir / "fetch-degraded.err").write_text(
        "warning: 1 conversion error(s) tagged with adf:error in fetched-degraded.md\n",
        encoding="utf-8",
    )
    (run_dir / "publish-degraded.err").write_text(
        "error: line 1: unresolved conversion error (adf:error); restore the content and remove the tag\n",
        encoding="utf-8",
    )
    return run_dir
