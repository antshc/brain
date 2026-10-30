from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

HEADER = ("ts", "phase", "decision", "why", "evidence", "result")
FORMULA_PREFIXES = ("=", "+", "-", "@")


def clean(value: str) -> str:
    single_line = value.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    # Spreadsheets execute cells starting with these; quote so generated evidence stays inert.
    if single_line.startswith(FORMULA_PREFIXES):
        return f"'{single_line}"
    return single_line


def append_row(
    logfile: Path,
    cells: list[str],
    *,
    now: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> str:
    if len(cells) != len(HEADER) - 1:
        raise ValueError(f"expected {len(HEADER) - 1} cells, got {len(cells)}")
    logfile.parent.mkdir(parents=True, exist_ok=True)
    timestamp = now().strftime("%Y-%m-%dT%H:%M:%SZ")
    row = "\t".join([timestamp, *(clean(cell) for cell in cells)])
    with logfile.open("a", encoding="utf-8") as handle:
        if handle.tell() == 0:
            handle.write("\t".join(HEADER) + "\n")
        handle.write(row + "\n")
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append one row to a show-me-your-work decision log (TSV).")
    parser.add_argument("logfile", type=Path)
    for column in HEADER[1:]:
        parser.add_argument(column)
    args = parser.parse_args(argv)
    try:
        append_row(args.logfile, [getattr(args, column) for column in HEADER[1:]])
    except OSError as exception:
        print(f"log.py: {exception}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
