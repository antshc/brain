from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Protocol

from .types import CheckFn
from .evidence import Evidence, EvidenceError, sha256, timestamp


@dataclass(frozen=True)
class TestCase:
    id: str
    outcome: str
    failure: str = ''


@dataclass(frozen=True)
class TestRunResult:
    cases: tuple[TestCase, ...]

    @property
    def passed(self) -> int:
        return sum(case.outcome == 'passed' for case in self.cases)

    @property
    def failed(self) -> int:
        return sum(case.outcome == 'failed' for case in self.cases)

    @property
    def skipped(self) -> int:
        return sum(case.outcome == 'skipped' for case in self.cases)

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def test_names(self) -> list[str]:
        return [case.id for case in self.cases]

    @property
    def failures(self) -> list[str]:
        return [case.failure or case.id for case in self.cases if case.outcome == 'failed']


def _result(cases: list[TestCase]) -> TestRunResult:
    if len({case.id for case in cases}) != len(cases):
        raise ValueError('Duplicate/retried test IDs require a project normalization policy')
    if any(not case.id or case.outcome not in ('passed', 'failed', 'skipped') for case in cases):
        raise ValueError('Invalid test ID/outcome')
    return TestRunResult(tuple(cases))


def _xml(text: str) -> ET.Element:
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('XML declarations/entities are not allowed')
    root = ET.fromstring(text)
    for node in root.iter():
        node.tag = node.tag.rsplit('}', 1)[-1]
    return root


def _counter(node: ET.Element, key: str, expected: int) -> None:
    raw = node.get(key)
    if raw is not None and (not raw.isdecimal() or int(raw) != expected):
        raise ValueError(f'Inconsistent test counter: {key}')


class JUnitAdapter:
    def parse(self, text: str) -> TestRunResult:
        root = _xml(text)
        if root.tag not in ('testsuite', 'testsuites'):
            raise ValueError('Not a JUnit report')
        cases = []
        for node in root.iter('testcase'):
            if any(child.tag in ('rerunFailure', 'rerunError', 'flakyFailure', 'flakyError') for child in node):
                raise ValueError('Retries require a project normalization policy')
            status = node.get('status', '').lower()
            if status and status not in ('run', 'passed', 'failed', 'skipped', 'notrun'):
                raise ValueError(f'Unknown JUnit status: {status}')
            failures = [child for child in node if child.tag in ('failure', 'error')]
            skipped = any(child.tag == 'skipped' for child in node) or status in ('skipped', 'notrun')
            if status == 'failed' and not failures:
                raise ValueError('Failed test missing failure details')
            outcome = 'failed' if failures else 'skipped' if skipped else 'passed'
            name = node.get('name', '')
            identity = f"{node.get('classname')}.{name}" if node.get('classname') else name
            cases.append(TestCase(identity, outcome, '; '.join(''.join(child.itertext()) for child in failures)))
        result = _result(cases)
        for suite in root.iter():
            if suite.tag in ('testsuite', 'testsuites'):
                nodes = list(suite.iter('testcase'))
                _counter(suite, 'tests', len(nodes))
                _counter(suite, 'failures', sum(any(c.tag == 'failure' for c in n) for n in nodes))
                _counter(suite, 'errors', sum(any(c.tag == 'error' for c in n) for n in nodes))
                _counter(suite, 'skipped', sum(any(c.tag == 'skipped' for c in n) or n.get('status') in ('skipped', 'notrun') for n in nodes))
        return result


class TrxAdapter:
    def parse(self, text: str) -> TestRunResult:
        root = _xml(text)
        if root.tag != 'TestRun':
            raise ValueError('Not a TRX report')
        aliases = {'Passed': 'passed', 'Failed': 'failed', 'Error': 'failed', 'Timeout': 'failed',
                   'Aborted': 'failed', 'NotExecuted': 'skipped', 'Inconclusive': 'skipped'}
        cases = []
        for node in root.iter('UnitTestResult'):
            outcome = aliases.get(node.get('outcome', ''))
            if outcome is None:
                raise ValueError('Unknown TRX outcome')
            cases.append(TestCase(node.get('testId', ''), outcome, ''.join(node.itertext()).strip()))
        result = _result(cases)
        summary = root.find('./ResultSummary')
        if summary is not None and summary.get('outcome') in ('Failed', 'Error', 'Aborted') and result.failed == 0:
            raise ValueError('TRX runner failed without test failure records')
        counters = root.find('./ResultSummary/Counters')
        if counters is None:
            raise ValueError('Missing TRX counters')
        _counter(counters, 'total', result.total)
        _counter(counters, 'passed', result.passed)
        _counter(counters, 'failed', sum(node.get('outcome') == 'Failed' for node in root.iter('UnitTestResult')))
        _counter(counters, 'notExecuted', sum(node.get('outcome') == 'NotExecuted' for node in root.iter('UnitTestResult')))
        _counter(counters, 'executed', result.total - sum(node.get('outcome') == 'NotExecuted' for node in root.iter('UnitTestResult')))
        return result


class ResultAdapter(Protocol):
    def parse(self, text: str) -> TestRunResult: ...


class JsonAdapter:
    """Schema: {"tests": [{"id": "suite.test", "outcome": "passed|failed|skipped", "failure": "..."}]}.

    Projects with other schemas implement ResultAdapter.
    """

    def parse(self, text: str) -> TestRunResult:
        data = json.loads(text)
        if not isinstance(data, dict) or not isinstance(data.get('tests'), list):
            raise ValueError('Missing JSON tests array')
        cases = []
        for item in data['tests']:
            if not isinstance(item, dict) or not all(isinstance(item.get(key), str) for key in ('id', 'outcome')):
                raise ValueError('Invalid JSON test entry')
            cases.append(TestCase(item['id'], item['outcome'], str(item.get('failure', ''))))
        return _result(cases)


def all_passed(result: TestRunResult) -> bool:
    return result.total > 0 and result.failed == 0 and result.skipped == 0


def minimum_executed(result: TestRunResult, minimum: int = 1) -> bool:
    if type(minimum) is not int or minimum < 1:
        raise ValueError('Minimum executed must be a positive integer')
    return result.passed + result.failed >= minimum


def required_present(result: TestRunResult, ids: list[str]) -> bool:
    return set(ids) <= set(result.test_names)


def no_unexpected_skips(result: TestRunResult, allowed: tuple[str, ...] = ()) -> bool:
    return all(case.id in allowed for case in result.cases if case.outcome == 'skipped')


def matches_revision(run: dict[str, Any], evidence: Evidence) -> bool:
    return run.get('revision') == evidence.revision and run.get('runId') == evidence.run_id and run.get('dirty') is False


def load_results(evidence: Evidence, report: str, run_manifest: str, adapter: ResultAdapter) -> TestRunResult:
    raw = evidence.read(report)
    run = evidence.json(run_manifest)
    if not isinstance(run, dict) or not matches_revision(run, evidence):
        raise EvidenceError('Test run identity/revision mismatch')
    start, end = timestamp(run.get('startedAt')), timestamp(run.get('finishedAt'))
    if not evidence.started_at <= start <= end <= evidence.finished_at:
        raise EvidenceError('Stale test execution')
    if not run.get('command') or run.get('reportSha256') != sha256(raw):
        raise EvidenceError('Test command/report hash missing or invalid')
    return adapter.parse(raw.decode('utf-8'))


class TestKit(Protocol):
    @property
    def evidence(self) -> Evidence: ...

    @property
    def check(self) -> CheckFn: ...


def check_results(kit: TestKit, report: str, run_manifest: str, adapter: ResultAdapter, *,
                  required_ids: tuple[str, ...], allowed_skips: tuple[str, ...] = ()) -> None:
    result = load_results(kit.evidence, report, run_manifest, adapter)
    if result.total == 0 or not required_present(result, list(required_ids)):
        raise EvidenceError('Required tests were not discovered/executed')
    if not minimum_executed(result) and no_unexpected_skips(result, allowed_skips):
        raise EvidenceError('No required tests executed')
    kit.check('tests: no failures', result.failed, 0, f'See {report}')
    kit.check('tests: expected skips', no_unexpected_skips(result, allowed_skips), True, f'See {report}')
