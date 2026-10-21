from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import safe_path, sha256


def contract_digest(root: Path) -> str:
    """Pin all project Python contract code and adapters, with relative filenames."""
    files = sorted(path for path in root.rglob('*.py') if '.runs' not in path.parts and '__pycache__' not in path.parts)
    if not files:
        raise ValueError('Empty contract code tree')
    payload = [(path.relative_to(root).as_posix(), sha256(path.read_bytes())) for path in files]
    return sha256(json.dumps(payload, separators=(',', ':')).encode())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Capture:
    """Collector utility, invoked by the authorized workflow, never by evaluate()."""

    def __init__(self, root: Path, *, run_id: str, revision: str, build_revision: str,
                 contract_sha256: str, environment: str) -> None:
        root.mkdir(parents=True, exist_ok=False)
        self.root = root
        self.manifest: dict[str, Any] = {'runId': run_id, 'revision': revision, 'buildRevision': build_revision,
            'contractSha256': contract_sha256, 'environment': environment, 'dirty': False,
            'startedAt': _now(), 'artifacts': {}}
        self._finished = False

    def add(self, name: str, content: bytes, *, complete: bool = True) -> None:
        if self._finished or name in ('evidence.json', 'receipt.json'):
            raise ValueError('Capture closed or reserved artifact path')
        path = safe_path(self.root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as handle:
            handle.write(content)
        self.manifest['artifacts'][name] = {'sha256': sha256(content), 'complete': complete,
            'correlationId': self.manifest['runId'], 'capturedAt': _now()}

    def finish(self) -> str:
        if self._finished:
            raise ValueError('Capture already finalized')
        self.manifest['finishedAt'] = _now()
        raw = json.dumps(self.manifest, indent=2).encode()
        with (self.root / 'evidence.json').open('xb') as handle:
            handle.write(raw)
        self._finished = True
        return sha256(raw)
