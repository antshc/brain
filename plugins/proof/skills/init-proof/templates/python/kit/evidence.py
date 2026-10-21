from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Protocol


class EvidenceError(ValueError):
    pass


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise EvidenceError('Missing timestamp')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise EvidenceError('Timestamp must include timezone')
    return result


def safe_path(root: Path, name: str) -> Path:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or '\\' in name:
        raise EvidenceError(f'Unsafe artifact path: {name}')
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()):
        raise EvidenceError(f'Artifact escapes run directory: {name}')
    return target


class DatabaseAdapter(Protocol):
    def get_resource(self, kind: str, key: str) -> dict[str, Any] | None: ...


class Evidence:
    """Validated bytes, cached once so evaluation cannot mix artifact versions.

    manifest_sha256 must come from a trusted collector/workflow channel, never from
    the untrusted run folder. Hashes detect changes; they do not authenticate an author.
    """

    def __init__(self, root: Path, *, revision: str, contract_sha256: str, manifest_sha256: str) -> None:
        self.root = root
        self._bytes: dict[str, bytes] = {}
        self.missing_optional: list[str] = []
        raw = safe_path(root, 'evidence.json').read_bytes()
        if not re.fullmatch('[0-9a-f]{64}', manifest_sha256) or sha256(raw) != manifest_sha256:
            raise EvidenceError('Manifest does not match trusted digest')
        manifest = json.loads(raw)
        if not isinstance(manifest, dict):
            raise EvidenceError('Manifest must be an object')
        if not re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}', revision):
            raise EvidenceError('Require full Git revision')
        if manifest.get('revision') != revision or manifest.get('buildRevision') != revision:
            raise EvidenceError('Evidence/build revision is stale')
        if not re.fullmatch('[0-9a-f]{64}', contract_sha256) or manifest.get('contractSha256') != contract_sha256:
            raise EvidenceError('Contract changed')
        if manifest.get('dirty') is not False:
            raise EvidenceError('Clean final revision required')
        run_id = manifest.get('runId')
        if not isinstance(run_id, str) or not run_id or not manifest.get('environment'):
            raise EvidenceError('Missing run/environment identity')
        self.run_id: str = run_id
        self.started_at = timestamp(manifest.get('startedAt'))
        self.finished_at = timestamp(manifest.get('finishedAt'))
        if self.finished_at < self.started_at:
            raise EvidenceError('Invalid capture interval')
        self.revision = revision
        artifacts = manifest.get('artifacts')
        if not isinstance(artifacts, dict):
            raise EvidenceError('Missing artifact index')
        self._artifacts: dict[str, Any] = artifacts

    def read(self, name: str) -> bytes:
        if name not in self._bytes:
            metadata = self._artifacts.get(name)
            if not isinstance(metadata, dict) or metadata.get('complete') is not True:
                raise EvidenceError(f'Missing/incomplete artifact: {name}')
            if metadata.get('correlationId') != self.run_id:
                raise EvidenceError(f'Wrong capture scope: {name}')
            captured = timestamp(metadata.get('capturedAt'))
            if not self.started_at <= captured <= self.finished_at:
                raise EvidenceError(f'Stale capture: {name}')
            raw = safe_path(self.root, name).read_bytes()
            if sha256(raw) != metadata.get('sha256'):
                raise EvidenceError(f'Artifact hash mismatch: {name}')
            self._bytes[name] = raw
        return self._bytes[name]

    def text(self, name: str) -> str:
        return self.read(name).decode('utf-8')

    def json(self, name: str) -> Any:
        return json.loads(self.read(name))

    def optional(self, name: str) -> bool:
        """Only absence is optional; a present but corrupt capture is still an error."""
        if name not in self._artifacts:
            if name not in self.missing_optional:
                self.missing_optional.append(name)
            return False
        self.read(name)
        return True
