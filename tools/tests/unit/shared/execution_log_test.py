#!/usr/bin/env python3
"""Unit tests for ExecutionLog.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import tempfile
from pathlib import Path

import pytest

from modules.github.shared.execution_log import ExecutionLog

_PR = "https://github.com/owner/repo/pull/1"


def make_log() -> tuple[ExecutionLog, Path]:
    """Return a fresh ExecutionLog backed by a temporary directory."""
    tmp = Path(tempfile.mkdtemp())
    return ExecutionLog(tmp, "owner/repo"), tmp


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
