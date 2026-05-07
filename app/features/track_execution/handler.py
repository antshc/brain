"""ExecutionLog: reads/writes per-PR attempt counts to cap retries."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from domain.execution_record import ExecutionRecord


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

    def update(self, pr_url: str, thread_ids: list[str]) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = self._log.get(pr_url, {})
        record = ExecutionRecord(
            pr_url=pr_url,
            count=entry.get("count", 0) + 1,
            last_run=ts,
            last_threads=thread_ids,
        )
        self._log[pr_url] = {
            "count": record.count,
            "last_run": record.last_run,
            "last_threads": record.last_threads,
        }
        self._save()

    def reset(self, pr_url: str) -> None:
        self._log.pop(pr_url, None)
        self._save()
