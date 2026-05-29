#!/usr/bin/env python3
"""Unit tests for ExecutionLog.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from afk.shared.execution_log import ExecutionLog

_PR = "https://github.com/owner/repo/pull/1"


def make_log(log_name: str = "fix-prs") -> tuple[ExecutionLog, Path]:
    """Return a fresh ExecutionLog backed by a temporary directory."""
    tmp = Path(tempfile.mkdtemp())
    return ExecutionLog(tmp, "owner/repo", log_name), tmp


class TestExecutionLog:
    """Feature: Execution Log"""

    def test_new_pr_has_zero_execution_count(self):
        # Scenario: New PR has zero execution count
        log, _ = make_log()
        assert log.get_count(_PR) == 0

    def test_count_increments_after_update(self):
        # Scenario: Count increments after update
        log, _ = make_log()
        log.update(_PR, ["T1"])
        assert log.get_count(_PR) == 1

    def test_multiple_updates_increment_count(self):
        # Scenario: Multiple updates increment count
        log, _ = make_log()
        log.update(_PR, ["T1"])
        log.update(_PR, ["T1"])
        assert log.get_count(_PR) == 2

    def test_reset_clears_execution_count(self):
        # Scenario: Reset clears execution count
        log, _ = make_log()
        log.update(_PR, ["T1"])
        log.update(_PR, ["T1"])
        log.update(_PR, ["T1"])
        log.reset(_PR)
        assert log.get_count(_PR) == 0

    def test_reset_on_non_existent_pr_does_not_error(self):
        # Scenario: Reset on non-existent PR does not error
        log, _ = make_log()
        log.reset(_PR)  # should not raise

    def test_writes_per_workflow_file_name(self):
        # Scenario: Separate workflow logs write to separate files
        log, tmp = make_log("dev")
        log.update(_PR, ["T1"])
        assert len(list(tmp.glob("dev-execution-log-*.json"))) == 1
        assert len(list(tmp.glob("fix-prs-execution-log-*.json"))) == 0

    def test_counts_are_isolated_across_workflow_logs(self):
        # Scenario: Counts are isolated for different log_name values
        tmp = Path(tempfile.mkdtemp())
        dev_log = ExecutionLog(tmp, "owner/repo", "dev")
        fix_log = ExecutionLog(tmp, "owner/repo", "fix-prs")
        dev_log.update(_PR, [14])
        assert dev_log.get_count(_PR) == 1
        assert fix_log.get_count(_PR) == 0

    def test_persists_array_record_schema(self):
        # Scenario: Persisted schema is array records with task and last_items
        log, tmp = make_log("fix-prs")
        log.update(_PR, ["T1", "T2"])
        path = next(tmp.glob("fix-prs-execution-log-*.json"))
        payload = json.loads(path.read_text())
        assert isinstance(payload, list)
        assert payload[0]["task"] == _PR
        assert payload[0]["count"] == 1
        assert payload[0]["last_items"] == ["T1", "T2"]

    def test_old_object_format_fails_fast(self):
        # Scenario: Old object format is not supported
        tmp = Path(tempfile.mkdtemp())
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        (tmp / f"fix-prs-execution-log-{today}.json").write_text("{}")
        with pytest.raises(ValueError, match="JSON array"):
            ExecutionLog(tmp, "owner/repo", "fix-prs")
