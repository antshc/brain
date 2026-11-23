"""Route twg page and work-item body commands to the skill's Markdown <-> ADF commands.

A twg command is overridden only when it reads or writes a Markdown body (Markdown is the
default when no format is given, except for `jira workitem comment create|update`, which need an explicit
`--body-format markdown`); any other format, targeted `--edits`, or structured output
(`-o json`, `--select`, ...) returns `None` and passes through to twg unchanged. An overridden
command with a flag the Markdown path cannot honour raises `OverrideError` instead of silently
falling back to twg's lossy Markdown.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MARKDOWN_FORMATS = (None, "md", "markdown")
ALIASES = {"-o": "--output", "-s": "--site", "-y": "--yes"}
STRUCTURED_OUTPUT = {"--output", "--output-summary", "--select", "--agent-fields", "--output-shape", "--usage-counts"}
WORKITEM_GET_PASSTHROUGH = {"--fields", "--field", "--full", "--comments", "--remote-links", "--variables-json", "--batch-concurrency", "--strict"}
ISSUE_KEY = re.compile(r"^[A-Z][A-Z0-9_]*-\d+$")
PAGE_PATH = re.compile(r"/pages/(?:edit-v2/)?(\d+)")
BROWSE_PATH = re.compile(r"/browse/([A-Z][A-Z0-9_]*-\d+)")


class OverrideError(Exception):
    """The command selects the Markdown path but carries something it cannot honour."""


class ResolveError(Exception):
    """A twg lookup needed to resolve a page reference failed."""


Resolver = Callable[[list[str]], dict]


@dataclass(frozen=True)
class Context:
    workdir: Path
    resolve: Resolver


@dataclass(frozen=True)
class Delegate:
    """An atl command run in place of the twg command."""

    command: str
    argv: list[str]
    publishes: bool = False
    follow_up: list[str] = field(default_factory=list)
    output_file: str | None = None


@dataclass(frozen=True)
class TwgCall:
    """A twg command run with rewritten arguments in place of the original."""

    argv: list[str]


@dataclass
class Parsed:
    values: dict[str, list[str]] = field(default_factory=dict)
    flags: set[str] = field(default_factory=set)
    rest: list[str] = field(default_factory=list)

    def get(self, name: str) -> str | None:
        found = self.values.get(name)
        return found[-1] if found else None

    def all(self, name: str) -> list[str]:
        return self.values.get(name, [])


def _option_name(token: str) -> str:
    name = token.split("=", 1)[0] if token.startswith("--") else token
    return ALIASES.get(name, name)


def parse(args: list[str], values: set[str], flags: set[str] | frozenset[str] = frozenset()) -> Parsed:
    """Extract the known options; everything else stays in `rest`, in order."""
    parsed = Parsed()
    index = 0
    while index < len(args):
        token = args[index]
        name = _option_name(token)
        inline = token.startswith("--") and "=" in token
        if name in values:
            if inline:
                value = token.split("=", 1)[1]
            elif index + 1 < len(args):
                index += 1
                value = args[index]
            else:
                raise OverrideError(f"{name} needs a value")
            parsed.values.setdefault(name, []).append(value)
        elif name in flags and not inline:
            parsed.flags.add(name)
        else:
            parsed.rest.append(token)
        index += 1
    return parsed


def _has_option(args: list[str], names: set[str]) -> bool:
    return any(token.startswith("-") and _option_name(token) in names for token in args)


def _positionals(parsed: Parsed, hint: str) -> list[str]:
    unsupported = [token for token in parsed.rest if token.startswith("-")]
    if unsupported:
        raise OverrideError(f"{unsupported[0]} is not supported on the Markdown path; {hint}")
    return parsed.rest


def _site_url(site: str) -> str:
    site = site.strip().rstrip("/")
    if "://" in site:
        return site
    return f"https://{site}" if "." in site else f"https://{site}.atlassian.net"


def _origin(url: str) -> str:
    parts = urlparse(url)
    return f"{parts.scheme}://{parts.netloc}"


def _page_ref(reference: str, context: Context, *, reference_space: str | None, site: str | None) -> tuple[str, str | None]:
    """A page id and, for a URL, its site; tiny links, titles, and ARIs resolve through twg."""
    if reference.isdigit():
        return reference, None
    if reference.startswith(("http://", "https://")):
        parts = urlparse(reference)
        match = PAGE_PATH.search(parts.path)
        page_id = match.group(1) if match else (parse_qs(parts.query).get("pageId") or [None])[0]
        if page_id and page_id.isdigit():
            return page_id, _origin(reference)
    lookup = ["confluence", "content", "get", reference, "--detail", "summary"]
    if reference_space:
        lookup += ["--reference-space", reference_space]
    if site:
        lookup += ["--site", site]
    payload = context.resolve(lookup)
    page_id = str((payload.get("data") or {}).get("id", ""))
    if not page_id.isdigit():
        raise ResolveError(f"could not resolve a page id from {reference!r}")
    return page_id, _origin(reference) if reference.startswith(("http://", "https://")) else None


def _issue_ref(reference: str) -> tuple[str, str | None]:
    if ISSUE_KEY.match(reference):
        return reference, None
    if reference.startswith(("http://", "https://")):
        parts = urlparse(reference)
        match = BROWSE_PATH.search(parts.path)
        key = match.group(1) if match else (parse_qs(parts.query).get("selectedIssue") or [""])[0]
        if ISSUE_KEY.match(key):
            return key, _origin(reference)
    raise OverrideError(f"{reference!r} is not a work-item key or browse URL; pass the key, or use --native")


def _numeric_id(value: str, option: str) -> str:
    if value.isdigit():
        return value
    match = PAGE_PATH.search(urlparse(value).path) if value.startswith(("http://", "https://")) else None
    if match:
        return match.group(1)
    raise OverrideError(f"{option} needs a numeric id or page URL on the Markdown path, got {value!r}")


def _body_file(parsed: Parsed, inline: str, file_option: str, context: Context, name: str) -> str | None:
    if parsed.get(file_option):
        return parsed.get(file_option)
    body = parsed.get(inline)
    if body is None:
        return None
    path = context.workdir / name
    path.write_text(body, encoding="utf-8")
    return str(path)


def _fields_file(value: str | None, context: Context) -> list[str]:
    if value is None:
        return []
    if not value.lstrip().startswith("{"):
        return ["--fields-json", value]
    try:
        fields = json.loads(value)
    except json.JSONDecodeError as exception:
        raise OverrideError(f"--fields-json is not a JSON object: {exception.msg}") from None
    path = context.workdir / "fields.json"
    path.write_text(json.dumps(fields), encoding="utf-8")
    return ["--fields-json", str(path)]


def _optional(option: str, value: str | None) -> list[str]:
    return [option, value] if value is not None else []


def _require_output_file(parsed: Parsed, what: str) -> str:
    output_file = parsed.get("--output-file")
    if not output_file:
        raise OverrideError(f"--output-file <path.md> is required for a Markdown {what} read; Markdown and its assets are written there")
    return output_file


def confluence_content_get(args: list[str], context: Context) -> Delegate | None:
    if _has_option(args, STRUCTURED_OUTPUT):
        return None
    parsed = parse(
        args,
        values={"--detail", "--format", "--id", "--output-file", "--site", "--reference-space", "--assets-dir", "--attachments", "--comments"},
        flags={"--body-only", "--yes"},
    )
    if parsed.get("--format") not in MARKDOWN_FORMATS or parsed.get("--detail") not in (None, "full"):
        return None
    references = _positionals(parsed, "use --format html or --native") + parsed.all("--id")
    if len(references) != 1:
        raise OverrideError("a Markdown page read takes exactly one page; run one command per page")
    output_file = _require_output_file(parsed, "page")
    site = parsed.get("--site")
    page_id, url_site = _page_ref(references[0], context, reference_space=parsed.get("--reference-space"), site=site)
    site_url = _site_url(site) if site else url_site
    return Delegate(
        "fetch-page",
        ["--page-id", page_id, "--md-path", output_file]
        + _optional("--site", site_url)
        + _optional("--assets-dir", parsed.get("--assets-dir"))
        + _optional("--attachments", parsed.get("--attachments"))
        + _optional("--comments", parsed.get("--comments")),
    )


def confluence_content_create(args: list[str], context: Context) -> Delegate | None:
    parsed = parse(
        args,
        values={"--space-id", "--parent-id", "--content-type", "--title", "--body", "--body-file", "--format", "--output-file", "--output", "--assets-dir"},
        flags={"--yes", "--ack-body-formats"},
    )
    has_body = parsed.get("--body") is not None or parsed.get("--body-file") is not None
    if parsed.get("--content-type") != "page" or not has_body or parsed.get("--format") not in MARKDOWN_FORMATS:
        return None
    _positionals(parsed, "use --format html or --native")
    if parsed.rest:
        raise OverrideError(f"unexpected argument {parsed.rest[0]!r} on the Markdown page create")
    space_id = parsed.get("--space-id")
    if not space_id or not space_id.isdigit():
        raise OverrideError("--space-id needs the numeric space id on the Markdown path; resolve a key with `confluence space list --keys <key>`")
    md_path = _body_file(parsed, "--body", "--body-file", context, "body.md")
    parent = parsed.get("--parent-id")
    return Delegate(
        "publish-page",
        ["run", "--md-path", md_path, "--space-id", space_id]
        + _optional("--parent-id", _numeric_id(parent, "--parent-id") if parent else None)
        + _optional("--title", parsed.get("--title"))
        + _optional("--assets-dir", parsed.get("--assets-dir")),
        publishes=True,
        output_file=parsed.get("--output-file"),
    )


def confluence_content_update(args: list[str], context: Context) -> Delegate | None:
    parsed = parse(
        args,
        values={"--id", "--snapshot-token", "--title", "--body", "--body-file", "--format", "--output-file", "--output", "--assets-dir", "--parent-id"},
        flags={"--yes", "--ack-body-formats"},
    )
    has_body = parsed.get("--body") is not None or parsed.get("--body-file") is not None
    if not has_body or parsed.get("--format") not in MARKDOWN_FORMATS:
        return None
    references = _positionals(parsed, "use --format html or --native") + parsed.all("--id")
    if len(references) != 1:
        raise OverrideError("a Markdown page update takes exactly one page")
    page_id, _ = _page_ref(references[0], context, reference_space=None, site=None)
    md_path = _body_file(parsed, "--body", "--body-file", context, "body.md")
    parent = parsed.get("--parent-id")
    return Delegate(
        "publish-page",
        ["run", "--md-path", md_path, "--page-id", page_id]
        + _optional("--parent-id", _numeric_id(parent, "--parent-id") if parent else None)
        + _optional("--title", parsed.get("--title"))
        + _optional("--assets-dir", parsed.get("--assets-dir")),
        publishes=True,
        output_file=parsed.get("--output-file"),
    )


def jira_workitem_get(args: list[str], context: Context) -> Delegate | None:
    if _has_option(args, STRUCTURED_OUTPUT | WORKITEM_GET_PASSTHROUGH):
        return None
    parsed = parse(
        args,
        values={"--issue-id", "--key", "--format", "--output-file", "--site", "--assets-dir", "--attachments"},
        flags={"--yes"},
    )
    if parsed.get("--format") not in MARKDOWN_FORMATS:
        return None
    references = _positionals(parsed, "use --native") + parsed.all("--issue-id") + parsed.all("--key")
    if len(references) != 1:
        raise OverrideError("a Markdown work-item read takes exactly one key; run one command per item")
    output_file = _require_output_file(parsed, "work-item")
    key, url_site = _issue_ref(references[0])
    site = parsed.get("--site")
    return Delegate(
        "fetch-work",
        ["--issue-key", key, "--md-path", output_file]
        + _optional("--site", _site_url(site) if site else url_site)
        + _optional("--assets-dir", parsed.get("--assets-dir"))
        + _optional("--attachments", parsed.get("--attachments")),
    )


WORKITEM_WRITE_VALUES = {
    "--summary",
    "--description",
    "--description-file",
    "--description-format",
    "--fields-json",
    "--attach",
    "--output-file",
    "--output",
}


def _description(parsed: Parsed, context: Context) -> str | None:
    if parsed.get("--description-format") not in MARKDOWN_FORMATS:
        return None
    return _body_file(parsed, "--description", "--description-file", context, "description.md")


def jira_workitem_create(args: list[str], context: Context) -> Delegate | None:
    parsed = parse(args, values=WORKITEM_WRITE_VALUES | {"--space", "--type", "--parent"}, flags={"--yes"})
    md_path = _description(parsed, context)
    if md_path is None:
        return None
    missing = [option for option in ("--space", "--type", "--summary") if not parsed.get(option)]
    if missing:
        raise OverrideError(f"{', '.join(missing)} required to create a work item")
    return Delegate(
        "publish-work",
        ["create", "--project", parsed.get("--space"), "--issue-type", parsed.get("--type"), "--summary", parsed.get("--summary"), "--markdown", md_path]
        + _optional("--parent", parsed.get("--parent"))
        + _fields_file(parsed.get("--fields-json"), context)
        + [token for path in parsed.all("--attach") for token in ("--attach", path)],
        publishes=True,
        follow_up=parsed.rest,
        output_file=parsed.get("--output-file"),
    )


def jira_workitem_update(args: list[str], context: Context) -> Delegate | None:
    parsed = parse(args, values=WORKITEM_WRITE_VALUES | {"--id"}, flags={"--yes"})
    md_path = _description(parsed, context)
    if md_path is None:
        return None
    if not parsed.get("--id"):
        raise OverrideError("--id <KEY> required to update a work item")
    key, _ = _issue_ref(parsed.get("--id"))
    return Delegate(
        "publish-work",
        ["update", "--key", key, "--markdown", md_path]
        + _optional("--summary", parsed.get("--summary"))
        + _fields_file(parsed.get("--fields-json"), context)
        + [token for path in parsed.all("--attach") for token in ("--attach", path)],
        publishes=True,
        follow_up=parsed.rest,
        output_file=parsed.get("--output-file"),
    )


COMMENT_COMMANDS = {("jira", "workitem", "comment", "create"), ("jira", "workitem", "comment", "update")}


def _comment_with_attachments(action: str, args: list[str], context: Context) -> Delegate:
    parsed = parse(args, values={"--issue-id", "--id", "--body", "--body-file", "--body-format", "--attach", "--output", "--output-file"})
    _positionals(parsed, "post the comment without --attach to use it")
    if parsed.rest:
        raise OverrideError(f"unexpected argument {parsed.rest[0]!r} on a comment with attachments")
    if parsed.get("--body-format") not in ("md", "markdown"):
        raise OverrideError("--attach needs --body-format markdown; the comment is built as Markdown with the files shown inline")
    if parsed.get("--output") not in (None, "json"):
        raise OverrideError("a comment with attachments prints JSON; drop --output or use -o json")
    if parsed.get("--body") is not None and parsed.get("--body-file") is not None:
        raise OverrideError("use either --body or --body-file, not both")
    md_path = _body_file(parsed, "--body", "--body-file", context, "comment.md")
    if md_path is None:
        raise OverrideError("--body or --body-file is required with --attach")
    if not parsed.get("--issue-id"):
        raise OverrideError("--issue-id <KEY> is required with --attach")
    key, _ = _issue_ref(parsed.get("--issue-id"))
    comment_id = parsed.get("--id")
    if action == "update" and not comment_id:
        raise OverrideError("--id <commentId> is required to update a comment")
    if action == "create" and comment_id:
        raise OverrideError("--id only applies to comment update")
    return Delegate(
        "publish-work",
        ["comment", "--key", key, "--markdown", md_path]
        + _optional("--comment-id", comment_id)
        + [token for path in parsed.all("--attach") for token in ("--attach", path)],
        publishes=True,
        output_file=parsed.get("--output-file"),
    )


def jira_comment_write(command: list[str], args: list[str], context: Context) -> Delegate | TwgCall | None:
    """twg takes comment Markdown only through `--body` plus `--body-format markdown`; `--body-file`
    is read here and forwarded inline. Other `--body` formats run on twg unchanged. `--attach` is not
    a twg flag: it publishes through `publish-work comment`, which shows each file inline."""
    if _has_option(args, {"--attach"}):
        return _comment_with_attachments(command[3], args, context)
    parsed = parse(args, values={"--body", "--body-file", "--body-format"})
    body_file, body, body_format = parsed.get("--body-file"), parsed.get("--body"), parsed.get("--body-format")
    is_markdown = body_format in ("md", "markdown")
    if body_file is None and not (body is not None and is_markdown):
        return None
    if body_file is not None and body is not None:
        raise OverrideError("use either --body or --body-file, not both")
    if not is_markdown:
        raise OverrideError("--body-file needs --body-format markdown; twg has no --body-file, so the file is sent as an inline Markdown --body")
    if body_file is not None:
        try:
            body = Path(body_file).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exception:
            raise OverrideError(f"cannot read --body-file {body_file}: {type(exception).__name__}") from None
    if not body.strip():
        raise OverrideError("the comment body is empty")
    return TwgCall([*command, *parsed.rest, "--body", body, "--body-format", "markdown"])


ROUTES: dict[tuple[str, str, str], Callable[[list[str], Context], Delegate | None]] = {
    ("confluence", "content", "get"): confluence_content_get,
    ("confluence", "content", "create"): confluence_content_create,
    ("confluence", "content", "update"): confluence_content_update,
    ("jira", "workitem", "get"): jira_workitem_get,
    ("jira", "workitem", "create"): jira_workitem_create,
    ("jira", "workitem", "update"): jira_workitem_update,
}


def plan(args: list[str], context: Context) -> Delegate | TwgCall | None:
    """The command replacing `args`, or `None` to pass `args` through to twg."""
    if tuple(args[:4]) in COMMENT_COMMANDS:
        return None if any(token in ("-h", "--help") for token in args) else jira_comment_write(args[:4], args[4:], context)
    handler = ROUTES.get(tuple(args[:3]))
    if handler is None or any(token in ("-h", "--help") for token in args):
        return None
    return handler(args[3:], context)
