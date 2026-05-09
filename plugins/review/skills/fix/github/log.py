"""Structured JSON logging to stderr."""

import json
import sys
from datetime import datetime, timezone


def log_json(level: str, message: str, **extra: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = {"timestamp": ts, "level": level, "message": message, **extra}
    print(json.dumps(entry), file=sys.stderr)
