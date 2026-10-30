from __future__ import annotations

import runpy
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "plugins/wf/skills/show-me-your-work/scripts/log.py"
)
FIXED = datetime(2026, 5, 24, 9, 2, tzinfo=timezone.utc)


class LogRowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = runpy.run_path(str(SCRIPT))
        self.directory = tempfile.TemporaryDirectory()
        self.logfile = Path(self.directory.name) / "nested" / "decisions.tsv"

    def tearDown(self) -> None:
        self.directory.cleanup()

    def append(self, cells: list[str]) -> None:
        self.module["append_row"](self.logfile, cells, now=lambda: FIXED)

    def test_first_row_writes_header_and_creates_parent(self) -> None:
        self.append(["frame", "sized the work", "know scope", "commit abc", "ok"])
        lines = self.logfile.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "ts\tphase\tdecision\twhy\tevidence\tresult")
        self.assertEqual(lines[1], "2026-05-24T09:02:00Z\tframe\tsized the work\tknow scope\tcommit abc\tok")

    def test_later_rows_append_without_repeating_header(self) -> None:
        self.append(["a", "b", "c", "d", "e"])
        self.append(["f", "g", "h", "i", "j"])
        lines = self.logfile.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(sum(line.startswith("ts\t") for line in lines), 1)

    def test_cells_stay_single_line(self) -> None:
        self.append(["p", "two\nlines", "tab\there", "cr\rx", "r"])
        row = self.logfile.read_text(encoding="utf-8").splitlines()[1].split("\t")
        self.assertEqual(row[2:5], ["two lines", "tab here", "cr x"])

    def test_formula_cells_are_quoted(self) -> None:
        self.append(["=SUM(A1)", "+1", "-x", "@cmd", "plain"])
        row = self.logfile.read_text(encoding="utf-8").splitlines()[1].split("\t")
        self.assertEqual(row[1:], ["'=SUM(A1)", "'+1", "'-x", "'@cmd", "plain"])

    def test_wrong_cell_count_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.append(["only", "four", "cells", "here"])

    def test_cli_appends_row(self) -> None:
        exit_code = self.module["main"]([str(self.logfile), "p", "d", "w", "e", "r"])
        self.assertEqual(exit_code, 0)
        self.assertTrue(self.logfile.read_text(encoding="utf-8").splitlines()[1].endswith("\tp\td\tw\te\tr"))


if __name__ == "__main__":
    unittest.main()
