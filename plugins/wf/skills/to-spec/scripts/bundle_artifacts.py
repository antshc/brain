#!/usr/bin/env python3
"""Wrap every file of a design sketch as one GitHub issue artifact body, plus a sketch index.

    bundle_artifacts.py --sketch PATH --out-dir DIR [--max-chars N]

PATH is one sketch file or the sketch root directory. Writes one body file per artifact into DIR
(absent or empty) and `manifest.json`; prints the manifest on stdout. Content-agnostic: never
interprets file contents. Exit codes: 0 ok, 2 invalid input (binary file, name collision,
oversized HTML, non-empty DIR); errors go to stderr and nothing is written.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

INDEX_NAME = "Sketch index"
DEFAULT_MAX_CHARS = 60000
METADATA_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
SKIPPED_DIRS = {".git", "__pycache__", "node_modules"}
MARKDOWN_SUFFIXES = {".md", ".markdown"}
HTML_SUFFIXES = {".html", ".htm"}
LANGUAGES = {
    ".cs": "csharp", ".csx": "csharp", ".csproj": "xml", ".props": "xml", ".targets": "xml", ".xml": "xml",
    ".py": "python", ".ts": "typescript", ".tsx": "tsx", ".js": "javascript", ".jsx": "jsx", ".java": "java",
    ".kt": "kotlin", ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php", ".swift": "swift", ".scala": "scala",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp", ".sql": "sql", ".sh": "bash", ".ps1": "powershell",
    ".json": "json", ".jsonc": "jsonc", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".ini": "ini",
    ".tf": "hcl", ".hcl": "hcl", ".proto": "protobuf", ".graphql": "graphql", ".css": "css", ".scss": "scss",
    ".mmd": "mermaid", ".diff": "diff", ".patch": "diff",
}
NAME_DISALLOWED = re.compile(r"[^A-Za-z0-9._/ -]")


class BundleError(Exception):
    exit_code = 2


@dataclass(frozen=True)
class SketchFile:
    relative: str
    text: str
    suffix: str


@dataclass(frozen=True)
class Artifact:
    name: str
    type: str
    body: str
    source: str | None
    part: int
    parts: int


def is_metadata(path: Path) -> bool:
    # `name:Zone.Identifier` and similar alternate-data-stream copies carry no sketch content.
    return ":" in path.name or path.name in METADATA_NAMES


def collect(sketch: Path) -> tuple[list[SketchFile], list[dict[str, str]]]:
    if not sketch.exists():
        raise BundleError(f"sketch path not found: {sketch}")
    root = sketch.parent if sketch.is_file() else sketch
    candidates = [sketch] if sketch.is_file() else sorted(
        (p for p in sketch.rglob("*") if p.is_file() and not SKIPPED_DIRS & set(p.relative_to(sketch).parts)),
        key=lambda p: p.relative_to(sketch).as_posix(),
    )
    files: list[SketchFile] = []
    skipped: list[dict[str, str]] = []
    errors: list[str] = []
    for path in candidates:
        relative = path.relative_to(root).as_posix()
        if is_metadata(path):
            skipped.append({"path": relative, "reason": "metadata"})
            continue
        data = path.read_bytes()
        if b"\x00" in data:
            errors.append(f"binary file cannot become a text artifact: {relative}")
            continue
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            errors.append(f"file is not UTF-8 text: {relative}")
            continue
        if not text.strip():
            skipped.append({"path": relative, "reason": "empty"})
            continue
        files.append(SketchFile(relative, text, path.suffix.lower()))
    if errors:
        raise BundleError("; ".join(errors))
    if not files:
        raise BundleError(f"sketch has no text files: {sketch}")
    return files, skipped


def artifact_name(relative: str) -> str:
    return re.sub(r" {2,}", " ", NAME_DISALLOWED.sub("", relative)).strip(" /") or "file"


def fence_for(text: str) -> str:
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def split_lines(text: str, budget: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        while len(line) > budget:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:budget])
            line = line[budget:]
        if len(current) + len(line) > budget:
            chunks.append(current)
            current = ""
        current += line
    if current:
        chunks.append(current)
    return chunks


def render(file: SketchFile, chunk: str, part: int, parts: int) -> str:
    title = f"# `{file.relative}`" + (f" part {part} of {parts}" if parts > 1 else "")
    if file.suffix in MARKDOWN_SUFFIXES:
        return f"{title}\n\n{chunk.rstrip()}\n"
    fence = fence_for(chunk)
    language = LANGUAGES.get(file.suffix, "")
    return f"{title}\n\n{fence}{language}\n{chunk.rstrip()}\n{fence}\n"


def wrap(file: SketchFile, max_chars: int) -> list[Artifact]:
    name = artifact_name(file.relative)
    if file.suffix in HTML_SUFFIXES:
        if len(file.text) > max_chars:
            raise BundleError(f"HTML file exceeds {max_chars} characters and cannot be split: {file.relative}")
        return [Artifact(name, "embedded_html", file.text, file.relative, 1, 1)]
    overhead = len(file.relative) + 2 * len(fence_for(file.text)) + 64
    budget = max_chars - overhead
    if budget < 1:
        raise BundleError(f"--max-chars too small for {file.relative}")
    chunks = [file.text] if len(file.text) + overhead <= max_chars else split_lines(file.text, budget)
    parts = len(chunks)
    return [
        Artifact(f"{name} part {index} of {parts}" if parts > 1 else name, "generic", render(file, chunk, index, parts),
                 file.relative, index, parts)
        for index, chunk in enumerate(chunks, start=1)
    ]


def index_artifact(files: list[SketchFile], artifacts: list[Artifact]) -> Artifact:
    rows = []
    for file in files:
        names = [a.name for a in artifacts if a.source == file.relative]
        rows.append(f"| `{file.relative}` | {', '.join(f'`{name}`' for name in names)} |")
    body = "\n".join([
        f"# {INDEX_NAME}", "",
        "Selected design sketch. Each sketch file is one artifact on this issue; sketch paths mirror intended target locations.", "",
        "| Sketch path | Artifact |", "|---|---|", *rows, "",
    ])
    return Artifact(INDEX_NAME, "plan", body, None, 1, 1)


def bundle(sketch: Path, max_chars: int = DEFAULT_MAX_CHARS) -> tuple[list[Artifact], list[dict[str, str]]]:
    files, skipped = collect(sketch)
    artifacts = [artifact for file in files for artifact in wrap(file, max_chars)]
    index = index_artifact(files, artifacts)
    owners: dict[str, str | None] = {}
    for artifact in [index, *artifacts]:
        key = artifact.name.casefold()
        if key in owners and owners[key] != artifact.source:
            raise BundleError(f"artifact name collision {artifact.name!r}: {owners[key] or INDEX_NAME} and {artifact.source}")
        owners[key] = artifact.source
    return [index, *artifacts], skipped


def write(artifacts: list[Artifact], skipped: list[dict[str, str]], out_dir: Path) -> dict[str, object]:
    if out_dir.exists() and any(out_dir.iterdir()):
        raise BundleError(f"output directory is not empty: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for number, artifact in enumerate(artifacts, start=1):
        path = out_dir / f"{number:03d}{'.html' if artifact.type == 'embedded_html' else '.md'}"
        path.write_text(artifact.body, encoding="utf-8")
        entries.append({
            "name": artifact.name, "type": artifact.type, "file": str(path.resolve()), "source": artifact.source,
            "part": artifact.part, "parts": artifact.parts,
        })
    manifest: dict[str, object] = {"artifacts": entries, "skipped": skipped}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wrap design sketch files as issue artifact bodies.")
    parser.add_argument("--sketch", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    args = parser.parse_args(argv)
    try:
        artifacts, skipped = bundle(args.sketch, args.max_chars)
        manifest = write(artifacts, skipped, args.out_dir)
    except BundleError as exception:
        print(f"bundle_artifacts: {exception}", file=sys.stderr)
        return exception.exit_code
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
