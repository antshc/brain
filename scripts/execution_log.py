"""Execution log for tracking PR processing attempts."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path


class ExecutionLog:
    def __init__(self, log_dir: Path, repo: str):
        slug = re.sub(r"[^A-Za-z0-9._-]", "-", repo)
        self._log_dir = log_dir / slug
        self._log: dict = {}
        self._init()

    def _log_path(self) -> Path:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._log_dir / f"execution-log-{today}.json"

    def _init(self) -> None:
        self._log_dir.mkdir(parents=True, exist_ok=True)
        path = self._log_path()
        if not path.exists():
            path.write_text("{}")
        self._log = json.loads(path.read_text())

    def _save(self) -> None:
        self._log_path().write_text(json.dumps(self._log, indent=2))

    def get_count(self, pr_url: str) -> int:
        return self._log.get(pr_url, {}).get("count", 0)

    def update(self, pr_url: str, thread_ids: list) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = self._log.get(pr_url, {})
        self._log[pr_url] = {
            "count": entry.get("count", 0) + 1,
            "last_threads": thread_ids,
            "last_run": ts,
        }
        self._save()

    def reset(self, pr_url: str) -> None:
        self._log.pop(pr_url, None)
        self._save()
