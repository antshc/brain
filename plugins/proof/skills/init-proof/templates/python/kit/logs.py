from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from .matchers import count_matches, matches_fields


@dataclass(frozen=True)
class LogRecord:
    timestamp: str | None
    severity: str
    event: str | None
    correlation_id: str | None
    properties: dict[str, Any]
    message: str
    source: str
    offset: int


class LogAdapter(Protocol):
    def parse(self, text: str, source: str = '') -> list[LogRecord]: ...


class JsonLinesAdapter:
    def parse(self, text: str, source: str = '') -> list[LogRecord]:
        records = []
        for number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            item = json.loads(line)
            if not isinstance(item, dict):
                raise ValueError(f'Log record must be an object: {source}:{number}')
            properties = item.get('properties', item.get('Properties', {}))
            if not isinstance(properties, dict):
                raise ValueError('Log properties must be an object')
            severity = item.get('severity', item.get('Level', item.get('severityText')))
            if not isinstance(severity, str) or not severity:
                raise ValueError('Missing log severity')
            records.append(LogRecord(item.get('timestamp', item.get('Timestamp')), severity,
                item.get('event', item.get('EventId', properties.get('EventId'))),
                item.get('correlationId', item.get('traceId', properties.get('CorrelationId'))), properties,
                str(item.get('message', item.get('RenderedMessage', item.get('body', '')))), source, number))
        return records


class TextAdapter:
    """The collector supplies scope for text sources without correlation fields."""

    def __init__(self, correlation_id: str, severity: Callable[[str], str]) -> None:
        self.correlation_id = correlation_id
        self.severity = severity

    def parse(self, text: str, source: str = '') -> list[LogRecord]:
        return [LogRecord(None, self.severity(line), None, self.correlation_id, {}, line, source, number)
                for number, line in enumerate(text.splitlines(), 1)]


class OtelAdapter:
    def parse(self, text: str, source: str = '') -> list[LogRecord]:
        """OTLP JSON resourceLogs/scopeLogs export, preserving typed attributes."""
        def value(item: dict[str, Any]) -> Any:
            for key in ('stringValue', 'boolValue', 'intValue', 'doubleValue'):
                if key in item:
                    raw = item[key]
                    return int(raw) if key == 'intValue' else raw
            raise ValueError('Unsupported OTel attribute type; supply a project adapter')

        result: list[LogRecord] = []
        document = json.loads(text)
        if not isinstance(document, dict) or 'resourceLogs' not in document:
            raise ValueError('Missing OTel resourceLogs')
        for resource in document['resourceLogs']:
            for scope in resource['scopeLogs']:
                for item in scope['logRecords']:
                    properties = {entry['key']: value(entry['value']) for entry in item.get('attributes', [])}
                    severity = item.get('severityText')
                    if not isinstance(severity, str) or not severity:
                        raise ValueError('Missing OTel severityText')
                    result.append(LogRecord(item.get('timeUnixNano'), severity, properties.get('event.name'),
                        item.get('traceId'), properties, str(value(item['body'])), source, len(result) + 1))
        return result


class LogView:
    """Use only with a complete capture validated through Evidence.text()."""

    def __init__(self, records: list[LogRecord], *, correlation_id: str) -> None:
        if not correlation_id:
            raise ValueError('Log scope is required')
        levels = {'trace', 'debug', 'info', 'information', 'warn', 'warning', 'error', 'fatal', 'critical'}
        if any(not isinstance(record.correlation_id, str) or not record.correlation_id
               or not isinstance(record.severity, str) or record.severity.lower() not in levels for record in records):
            raise ValueError('Log record has unknown severity or missing scope')
        self.records = [record for record in records if record.correlation_id == correlation_id]

    def event_exists(self, event: str, fields: dict[str, Any] | None = None) -> bool:
        return any(record.event == event and matches_fields(record.properties, fields or {}) for record in self.records)

    def fields_match(self, event: str, fields: dict[str, Any]) -> bool:
        return self.event_exists(event, fields)

    def no_errors(self, allowed_events: tuple[str, ...] = ()) -> bool:
        return not any(record.severity.lower() in ('error', 'fatal', 'critical')
                       and record.event not in allowed_events for record in self.records)

    def count(self, event: str, *, min_count: int | None = None,
              max_count: int | None = None, equals: int | None = None) -> bool:
        return count_matches(self.records, lambda record: record.event == event,
                             min_count=min_count, max_count=max_count, equals=equals)

    def message_contains(self, text: str, *, regex: bool = False) -> bool:
        return any(bool(re.search(text, record.message)) if regex else text in record.message for record in self.records)
