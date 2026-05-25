#!/usr/bin/env python3
"""Unit tests for the dev CLI entry point.

Mapped to TEST_PLAN.md — every class docstring names the Feature,
every method name is the Scenario in snake_case.
When a test or scenario changes, update both sides to stay in sync.
"""

import argparse
import logging
from datetime import date
from pathlib import Path

import pytest

import afk.features.dev.cli as dev_cli


class TestDevCli:
    """Feature: Dev CLI"""

    def test_parser_applies_default_arguments_for_valid_repository(self):
        # Scenario: Parser applies default arguments for valid repository
        args = dev_cli._build_parser().parse_args(["--github_repo_board", "owner/repo"])

        assert args.github_repo_board == "owner/repo"
        assert args.max_executions == dev_cli.DEFAULT_MAX_EXECUTIONS
        assert args.agent == "copiloty"
        assert args.prompt == "/ralph:dev"
        assert args.log_dir == Path("/var/log/ralph")

    def test_parser_accepts_custom_arguments(self):
        # Scenario: Parser accepts custom arguments
        args = dev_cli._build_parser().parse_args([
            "--github_repo_board", "owner/repo",
            "--max_executions", "7",
            "--agent", "other-agent",
            "--prompt", "/custom:dev",
            "--log-dir", "custom-logs",
        ])

        assert args.github_repo_board == "owner/repo"
        assert args.max_executions == 7
        assert args.agent == "other-agent"
        assert args.prompt == "/custom:dev"
        assert args.log_dir == Path("custom-logs")

    def test_parser_accepts_no_arguments(self):
        # Scenario: Parser accepts no arguments (github_repo_board is optional)
        args = dev_cli._build_parser().parse_args([])

        assert args.github_repo_board is None

    def test_github_repo_validator_rejects_invalid_repository_format(self):
        # Scenario: GitHub repo validator rejects invalid repository format
        with pytest.raises(argparse.ArgumentTypeError, match="Expected owner/repo"):
            dev_cli._github_repo("owner-repo")

    def test_repo_dir_validator_rejects_missing_directory(self):
        # Scenario: Repo dir validator rejects missing directory
        with pytest.raises(argparse.ArgumentTypeError, match="repo-dir does not exist"):
            dev_cli._repo_dir("__missing_repo_dir__")

    def test_main_delegates_to_handler_with_info_logging(self, monkeypatch):
        # Scenario: Main delegates to handler with info logging
        args = argparse.Namespace(
            github_repo_board="owner/repo",
            max_executions=7,
            agent="other-agent",
            prompt="/custom:dev",
            log_dir=Path("dev-logs"),
        )
        mkdir_calls = []
        captured_basic_config = {}
        captured_dev_call = {}

        class FakeParser:
            def parse_args(self):
                return args

        def fake_mkdir(self, parents=False, exist_ok=False):
            mkdir_calls.append((self, parents, exist_ok))

        monkeypatch.delenv("AFK_DEBUG", raising=False)
        monkeypatch.setattr(dev_cli, "_build_parser", lambda: FakeParser())
        monkeypatch.setattr(Path, "mkdir", fake_mkdir)
        monkeypatch.setattr(dev_cli.logging, "FileHandler", lambda path, mode="a": ("file", path, mode))
        monkeypatch.setattr(dev_cli.logging, "StreamHandler", lambda: ("stream",))
        monkeypatch.setattr(dev_cli.logging, "basicConfig", lambda **kwargs: captured_basic_config.update(kwargs))
        monkeypatch.setattr(
            dev_cli,
            "dev",
            lambda github_repo, log_dir, max_executions, prompt, agent_name: captured_dev_call.update(
                github_repo=github_repo,
                log_dir=log_dir,
                max_executions=max_executions,
                prompt=prompt,
                agent_name=agent_name,
            ),
        )

        result = dev_cli.main()

        assert result is None
        assert mkdir_calls == [(args.log_dir, True, True)]
        assert captured_basic_config == {
            "level": logging.INFO,
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "handlers": [
                ("file", args.log_dir / f"dev-{date.today()}.log", "a"),
                ("stream",),
            ],
        }
        assert captured_dev_call == {
            "github_repo": "owner/repo",
            "log_dir": args.log_dir,
            "max_executions": 7,
            "prompt": "/custom:dev",
            "agent_name": "other-agent",
        }

    def test_main_uses_debug_logging_when_afk_debug_is_set(self, monkeypatch):
        # Scenario: Main uses debug logging when AFK_DEBUG is set
        args = argparse.Namespace(
            github_repo_board="owner/repo",
            max_executions=dev_cli.DEFAULT_MAX_EXECUTIONS,
            agent="copiloty",
            prompt="/ralph:dev",
            log_dir=Path("dev-logs"),
        )
        captured_basic_config = {}

        class FakeParser:
            def parse_args(self):
                return args

        monkeypatch.setenv("AFK_DEBUG", "1")
        monkeypatch.setattr(dev_cli, "_build_parser", lambda: FakeParser())
        monkeypatch.setattr(Path, "mkdir", lambda self, parents=False, exist_ok=False: None)
        monkeypatch.setattr(dev_cli.logging, "FileHandler", lambda path, mode="a": ("file", path, mode))
        monkeypatch.setattr(dev_cli.logging, "StreamHandler", lambda: ("stream",))
        monkeypatch.setattr(dev_cli.logging, "basicConfig", lambda **kwargs: captured_basic_config.update(kwargs))
        monkeypatch.setattr(dev_cli, "dev", lambda *args, **kwargs: None)

        dev_cli.main()

        assert captured_basic_config["level"] == logging.DEBUG
