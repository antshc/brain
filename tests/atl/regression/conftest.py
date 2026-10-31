from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ATL_DIR = Path(__file__).resolve().parents[3] / "plugins" / "atl"
SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
CONVERTER = ATL_DIR / "skills" / "map-markdown-adf" / "scripts" / "map_markdown_adf.py"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from capabilities import FOOTER_COMMENT_BODY, INLINE_ANCHOR_TEXT, INLINE_COMMENT_BODY  # noqa: E402
from regression import init_run  # noqa: E402

_IGNORED_RE = re.compile(r"<!-- adf:ignore:start -->.*?<!-- adf:ignore:end -->\n*", re.DOTALL)


def _convert(command: str, text: str) -> str:
    return subprocess.run(
        [sys.executable, str(CONVERTER), command], input=text, capture_output=True, text=True, check=True
    ).stdout


def simulate_fetch(page_md: str, fetch_number: int) -> str:
    """What `publish-page` then `fetch-page` return for the fixture, built from the real
    `map-markdown-adf` round trip plus fetch-page's documented substitutions (mermaid fence from
    the sidecar, cached attachment links, inline anchor from the twg comment, `## Comments`)."""
    published = _IGNORED_RE.sub("", page_md)
    markdown = _convert("adf-to-md", _convert("md-to-adf", published))
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
    return run_dir
