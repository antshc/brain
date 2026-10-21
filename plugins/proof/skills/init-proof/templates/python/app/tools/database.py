from __future__ import annotations

from typing import Any, Protocol


class Cursor(Protocol):
    def execute(self, sql: str, parameters: tuple[str, ...]) -> Any: ...
    def fetchall(self) -> list[Any]: ...


class SqlServerOrderAdapter:
    """Example schema; adapt SQL here. Supply an isolated, read-only DB connection."""

    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    def get_resource(self, kind: str, key: str) -> dict[str, Any] | None:
        if kind != 'order':
            raise ValueError('Only order snapshots supported')
        self.cursor.execute('SELECT Id, OrderNumber FROM Orders WHERE Id = ?', (key,))
        rows = self.cursor.fetchall()
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError('Order key is not unique')
        identifier, number = rows[0]
        self.cursor.execute('SELECT Sku, Quantity FROM OrderItems WHERE OrderId = ?', (key,))
        return {'id': str(identifier), 'orderNumber': number,
                'items': [{'sku': row[0], 'quantity': row[1]} for row in self.cursor.fetchall()]}


class PostgresOrderAdapter:
    def __init__(self, cursor: Cursor) -> None:
        self.cursor = cursor

    def get_resource(self, kind: str, key: str) -> dict[str, Any] | None:
        if kind != 'order':
            raise ValueError('Only order snapshots supported')
        self.cursor.execute('SELECT id, order_number FROM orders WHERE id = %s', (key,))
        rows = self.cursor.fetchall()
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError('Order key is not unique')
        identifier, number = rows[0]
        self.cursor.execute('SELECT sku, quantity FROM order_items WHERE order_id = %s', (key,))
        return {'id': str(identifier), 'orderNumber': number,
                'items': [{'sku': row[0], 'quantity': row[1]} for row in self.cursor.fetchall()]}
