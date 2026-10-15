from __future__ import annotations

import io
import json
import runpy
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "plugins/wf/skills/index-docs/scripts/load_index.py"

INDEX = """# System Overview

## Building blocks

#### Deployables

<!-- rows: 1 -->

| Building block | Trigger condition | Summary | Location |
|---|---|---|---|
| **[Api](docs/building-blocks/api.md)** (api) | http endpoints, auth | Serves requests | `src/api` |

#### Terminal infrastructure boundaries *(optional, hand-authored)*

| Boundary | Responsibility | Navigation anchor |
|---|---|---|
| S3 | storage | bucket |

## Architecture Decision Records *(optional)*

<!-- rows: 2 -->

| Decision | Summary | Trigger condition & Default |
|----------|---------|-----------------------------|
| [Use DynamoDB](docs/adr/use-dynamodb.md) | Store state in DynamoDB. | **Trigger:** persistence, partition keys. **Default:** single-table design |
| Keep history | Append-only history \\| no deletes. | **Trigger:** audit trail. **Default:** append-only |

## Crosscutting Concepts *(optional)*

| Concept | Summary | Trigger condition & Default |
|---------|---------|-----------------------------|
| **[Ledger](docs/concepts/structure-ledger.md)** | Session state. | **Trigger:** resumable session |

```md
| Concept | Summary | Trigger condition & Default |
|---------|---------|-----------------------------|
| **[Fenced](docs/concepts/fenced.md)** | Ignored. | **Trigger:** never |
```
"""


class LoadIndexTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = runpy.run_path(str(SCRIPT))

    def load(self, text: str = INDEX) -> tuple[list[object], list[str]]:
        return self.module["load_index"](text)

    def run_cli(self, text: str, *args: str) -> tuple[int, dict[str, object]]:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ARCHITECTURE.md"
            path.write_text(text, encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = self.module["main"]([str(path), *args])
        return code, json.loads(stdout.getvalue())

    def test_loads_every_trigger_condition_table_and_row(self) -> None:
        tables, errors = self.load()
        self.assertEqual(errors, [])
        self.assertEqual(
            [(table.name, table.row_count) for table in tables],
            [("Deployables", 1), ("Architecture Decision Records", 2), ("Crosscutting Concepts", 1)],
        )

    def test_skips_tables_without_trigger_column_and_fenced_examples(self) -> None:
        tables, _ = self.load()
        titles = [row.title for table in tables for row in table.rows]
        self.assertNotIn("S3", titles)
        self.assertNotIn("Fenced", titles)

    def test_splits_trigger_and_default(self) -> None:
        tables, _ = self.load()
        adr = tables[1].rows[0]
        self.assertEqual(adr.title, "Use DynamoDB")
        self.assertEqual(adr.link, "docs/adr/use-dynamodb.md")
        self.assertEqual(adr.trigger, "persistence, partition keys")
        self.assertEqual(adr.default, "single-table design")
        self.assertEqual(adr.cells, {"Summary": "Store state in DynamoDB."})

    def test_omits_caller_named_columns(self) -> None:
        tables, _ = self.module["load_index"](INDEX, ["summary"])
        self.assertEqual(tables[1].rows[0].cells, {})
        self.assertEqual(tables[0].rows[0].cells, {"Location": "`src/api`"})

    def test_keeps_other_cells_and_unlinked_titles(self) -> None:
        tables, _ = self.load()
        deployable = tables[0].rows[0]
        self.assertEqual(deployable.trigger, "http endpoints, auth")
        self.assertIsNone(deployable.default)
        self.assertEqual(deployable.cells, {"Summary": "Serves requests", "Location": "`src/api`"})
        unlinked = tables[1].rows[1]
        self.assertEqual(unlinked.title, "Keep history")
        self.assertIsNone(unlinked.link)
        self.assertEqual(unlinked.cells["Summary"], "Append-only history | no deletes.")

    def test_trigger_without_default(self) -> None:
        tables, _ = self.load()
        concept = tables[2].rows[0]
        self.assertEqual(concept.trigger, "resumable session")
        self.assertIsNone(concept.default)

    def test_reads_row_markers(self) -> None:
        tables, _ = self.load()
        self.assertEqual([table.marker_count for table in tables], [1, 2, None])

    def test_marker_mismatch_is_an_error(self) -> None:
        text = INDEX.replace("<!-- rows: 2 -->", "<!-- rows: 3 -->")
        code, payload = self.run_cli(text)
        self.assertEqual(code, 1)
        self.assertEqual(len(payload["errors"]), 1)
        self.assertIn("rows marker says 3, table has 2", payload["errors"][0])

    def test_malformed_row_is_an_error(self) -> None:
        text = INDEX.replace("| **Trigger:** audit trail.", "| extra | **Trigger:** audit trail.")
        tables, errors = self.load(text)
        self.assertEqual(tables[1].row_count, 1)
        self.assertTrue(any("expected 3 cells, found 4" in error for error in errors))

    def test_cli_emits_counts_and_rows(self) -> None:
        code, payload = self.run_cli(INDEX)
        self.assertEqual(code, 0)
        self.assertEqual(payload["totalRows"], 4)
        self.assertEqual(payload["counts"]["Architecture Decision Records"], 2)
        self.assertEqual(len(payload["tables"]), 3)

    def test_cli_counts_only(self) -> None:
        code, payload = self.run_cli(INDEX, "--counts-only")
        self.assertEqual(code, 0)
        self.assertEqual(payload["tables"], [])
        self.assertEqual(payload["totalRows"], 4)

    def test_cli_omit_column(self) -> None:
        code, payload = self.run_cli(INDEX, "--omit-column", "Summary")
        self.assertEqual(code, 0)
        self.assertEqual(payload["tables"][2]["rows"][0]["cells"], {})

    def test_cli_table_filter_keeps_all_counts(self) -> None:
        code, payload = self.run_cli(INDEX, "--table", "Crosscutting Concepts")
        self.assertEqual(code, 0)
        self.assertEqual([table["name"] for table in payload["tables"]], ["Crosscutting Concepts"])
        self.assertEqual(len(payload["counts"]), 3)

    def test_cli_unknown_table_is_an_error(self) -> None:
        code, payload = self.run_cli(INDEX, "--table", "Nope")
        self.assertEqual(code, 1)
        self.assertIn("Table not found: Nope", payload["errors"])

    def test_cli_missing_file_exits_2(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = self.module["main"](["/nonexistent/ARCHITECTURE.md"])
        self.assertEqual(code, 2)
        self.assertIn("Cannot read", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
