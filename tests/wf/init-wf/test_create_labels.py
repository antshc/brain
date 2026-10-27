from __future__ import annotations

import runpy
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "plugins/wf/skills/init-wf/scripts/create_labels.py"
)


class CreateLabelsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = runpy.run_path(str(SCRIPT))
        self.labels = self.module["LABELS"]

    def check_setup(self, existing_names: list[str]) -> list[list[str]]:
        def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            self.assertTrue(kwargs["check"])
            if command[:3] == ["gh", "repo", "view"]:
                output = "owner/tracker\n"
            elif command[:3] == ["gh", "label", "list"]:
                self.assertIn("owner/tracker", command)
                output = "\n".join(existing_names)
            elif command[:3] == ["gh", "label", "create"]:
                self.assertIn("owner/tracker", command)
                output = ""
            else:
                raise AssertionError(f"Unexpected command: {command}")
            return subprocess.CompletedProcess(command, 0, stdout=output)

        with patch("subprocess.run", side_effect=run) as mocked_run:
            self.assertEqual(self.module["main"](), 0)
        return [
            call.args[0]
            for call in mocked_run.call_args_list
            if call.args[0][:3] == ["gh", "label", "create"]
        ]

    def test_creates_all_nine_baseline_labels(self) -> None:
        self.assertEqual(
            [name for name, _, _ in self.labels],
            [
                "hitl", "spec", "bug", "wayfinder:map",
                "wayfinder:research", "wayfinder:experiment",
                "wayfinder:grilling", "wayfinder:task",
                "wayfinder:contract-design",
            ],
        )
        created = self.check_setup([])
        self.assertEqual(
            created,
            [
                [
                    "gh", "label", "create", name,
                    "--repo", "owner/tracker",
                    "--color", color, "--description", description,
                ]
                for name, color, description in self.labels
            ],
        )

    def test_existing_labels_are_not_recreated(self) -> None:
        self.assertEqual(self.check_setup([name for name, _, _ in self.labels]), [])

    def test_only_missing_label_is_created(self) -> None:
        created = self.check_setup(
            [name for name, _, _ in self.labels if name != "bug"]
        )
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0][3], "bug")

    def test_repository_resolution_failure_stops_setup(self) -> None:
        failure = subprocess.CalledProcessError(1, ["gh", "repo", "view"])
        with patch("subprocess.run", side_effect=failure) as mocked_run:
            with self.assertRaises(subprocess.CalledProcessError):
                self.module["main"]()
        self.assertEqual(mocked_run.call_count, 1)

    def test_label_lookup_failure_does_not_create_labels(self) -> None:
        results = [
            subprocess.CompletedProcess([], 0, stdout="owner/tracker\n"),
            subprocess.CalledProcessError(1, ["gh", "label", "list"]),
        ]
        with patch("subprocess.run", side_effect=results) as mocked_run:
            with self.assertRaises(subprocess.CalledProcessError):
                self.module["main"]()
        self.assertEqual(mocked_run.call_count, 2)

    def test_creation_failure_stops_before_next_label(self) -> None:
        results = [
            subprocess.CompletedProcess([], 0, stdout="owner/tracker\n"),
            subprocess.CompletedProcess([], 0, stdout=""),
            subprocess.CalledProcessError(1, ["gh", "label", "create"]),
        ]
        with patch("subprocess.run", side_effect=results) as mocked_run:
            with self.assertRaises(subprocess.CalledProcessError):
                self.module["main"]()
        self.assertEqual(mocked_run.call_count, 3)
