from __future__ import annotations

from typing import Any, Protocol


class Cursor(Protocol):
    def execute(self, sql: str, parameters: tuple[str, ...]) -> Any: ...
    def fetchall(self) -> list[Any]: ...


class SqlServerVpgAdapter:
    """Example schema; adapt SQL here. Supply an isolated, read-only DB connection."""

    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    def get_resource(self, kind: str, key: str) -> dict[str, Any] | None:
        if kind != 'vpg':
            raise ValueError('Only VPG snapshots supported')
        self.cursor.execute('SELECT Id, Name FROM Vpg WHERE Id = ?', (key,))
        rows = self.cursor.fetchall()
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError('VPG key is not unique')
        identifier, name = rows[0]
        self.cursor.execute('SELECT Name FROM VpgVm WHERE VpgId = ?', (key,))
        return {'id': str(identifier), 'name': name, 'vms': [{'name': row[0]} for row in self.cursor.fetchall()]}


class PostgresVpgAdapter:
    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    def get_resource(self, kind: str, key: str) -> dict[str, Any] | None:
        if kind != 'vpg':
            raise ValueError('Only VPG snapshots supported')
        self.cursor.execute('SELECT id, name FROM vpg WHERE id = %s', (key,))
        rows = self.cursor.fetchall()
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError('VPG key is not unique')
        identifier, name = rows[0]
        self.cursor.execute('SELECT name FROM vpg_vm WHERE vpg_id = %s', (key,))
        return {'id': str(identifier), 'name': name, 'vms': [{'name': row[0]} for row in self.cursor.fetchall()]}
