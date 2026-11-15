"""`publish-page verify`: read-back check after a publish. Re-fetch the page through the
`fetch-page` command, in-process, into a separate verify directory, then assert the anchor-span count and the presence/absence of
phrases. Prints every check by name; exits 1 when any fails, 2 when the re-fetch fails.
Deletes nothing — the caller removes working files only after a pass.

Usage:
    atl.py publish-page verify --page-id <id> --config <configPath> --expect-anchors <n> \
        [--present <file>] [--absent <file>] [--verify-dir <dir>]

`--present`/`--absent` files hold one phrase per non-empty line. Phrases match the fetched
body with comment spans and `adf:ignore` sections removed and whitespace collapsed.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

from .conversion_guard import GuardError, compare_documents
_IGNORED_RE = re.compile(r"<!-- adf:ignore:start -->.*?<!-- adf:ignore:end -->", re.DOTALL)
_ANCHOR_RE = re.compile(r'<!--\s*adf:comment\s+id="[^"]+"\s*-->')
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


class FetchFailed(Exception):
    """The re-fetch exited non-zero; the message is `fetch-page`'s own sanitized stderr."""


def _plain(text: str) -> str:
    return " ".join(_HTML_COMMENT_RE.sub("", text).split())


def check_markdown(markdown: str, expect_anchors: int, present: list[str], absent: list[str]) -> list[Check]:
    body = _IGNORED_RE.sub("", markdown)
    found = len(_ANCHOR_RE.findall(body))
    plain = _plain(body)
    checks = [Check("anchor-count", found == expect_anchors, f"expected {expect_anchors}, found {found}")]
    checks += [Check(f'present: "{p}"', _plain(p) in plain, "") for p in present]
    checks += [Check(f'absent: "{a}"', _plain(a) not in plain, "") for a in absent]
    return checks


def read_phrases(path: str | None) -> list[str]:
    if not path:
        return []
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def fetch_markdown(page_id: str, config: str, md_path: Path) -> str:
    from .fetch_page.assemble_page import main as fetch_page_main

    md_path.parent.mkdir(parents=True, exist_ok=True)
    stderr = io.StringIO()
    argv = ["--page-id", page_id, "--config", config, "--md-path", str(md_path), "--attachments", "skip", "--comments", "skip"]
    try:
        with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
            fetch_page_main(argv)
    except SystemExit as exception:
        if exception.code not in (None, 0):
            message = exception.code if isinstance(exception.code, str) else stderr.getvalue().strip()
            raise FetchFailed(message or "fetch-page exited non-zero") from None
    return md_path.read_text(encoding="utf-8")


def fetch_raw_page(page_id: str, config: str) -> tuple[str, dict]:
    from .config import load_credentials, require_supported_library
    from .confluence_client import get_confluence
    from .fetch_page.assemble_page import fetch_page, PageFetchError

    require_supported_library()
    credentials = load_credentials(config)
    if credentials is None:
        raise FetchFailed("missing Atlassian credentials")
    try:
        return fetch_page(get_confluence(credentials), page_id)
    except PageFetchError as exception:
        raise FetchFailed(str(exception)) from None


def main(
    argv: list[str] | None = None, *, fetch: Callable[[str, str, Path], str] = fetch_markdown,
    fetch_raw: Callable[[str, str], tuple[str, dict]] = fetch_raw_page, prog: str | None = None
) -> int:
    parser = argparse.ArgumentParser(prog=prog, description="Re-fetch a published page and assert anchors and phrases.")
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--config", required=True, help="`.atlassian.json.user` path (`configPath` from `preflight-atlassian`)")
    parser.add_argument("--expect-anchors", required=True, type=int, help="Expected number of adf:comment spans")
    parser.add_argument("--present", help="File with phrases that must be present, one per line")
    parser.add_argument("--absent", help="File with phrases that must be absent, one per line")
    parser.add_argument("--verify-dir", default="verify", help="Directory for the re-fetched page (default: ./verify)")
    parser.add_argument("--expected-manifest", help="Expected title and ADF manifest from publish-page run")
    args = parser.parse_args(argv)

    present, absent = read_phrases(args.present), read_phrases(args.absent)
    try:
        markdown = fetch(args.page_id, args.config, Path(args.verify_dir) / "page.md")
    except FetchFailed as exception:
        print(f"FAIL re-fetch: {exception}", file=sys.stderr)
        return 2

    checks = check_markdown(markdown, args.expect_anchors, present, absent)
    if args.expected_manifest:
        try:
            expected = json.loads(Path(args.expected_manifest).read_text(encoding="utf-8"))
            title, actual_adf = fetch_raw(args.page_id, args.config)
            verify_dir = Path(args.verify_dir)
            verify_dir.mkdir(parents=True, exist_ok=True)
            (verify_dir / "raw-adf.json").write_text(json.dumps({"title": title, "adf": actual_adf}, indent=2) + "\n", encoding="utf-8")
            checks.append(Check("title", title == expected["title"], ""))
            compare_documents(expected["adf"], actual_adf, transport=True)
            checks.append(Check("semantic-body", True, ""))
        except GuardError as exception:
            checks.append(Check("semantic-body", False, str(exception)))
        except (FetchFailed, OSError, ValueError, KeyError) as exception:
            print(f"FAIL semantic-read-back: {type(exception).__name__}", file=sys.stderr)
            return 2
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"{status} {check.name}" + (f" ({check.detail})" if check.detail else ""))
    failed = [check for check in checks if not check.passed]
    print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    return 1 if failed else 0
