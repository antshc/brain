from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import subprocess
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[3] / 'plugins/proof/skills/init-proof/templates/python/kit'
spec = importlib.util.spec_from_file_location('durable_kit', KIT / '__init__.py', submodule_search_locations=[str(KIT)])
assert spec and spec.loader
kit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = kit
spec.loader.exec_module(kit)


def saved(tmp_path, *, content=None):
    body = json.dumps(content if content is not None else {'orderNumber': 'ORD-1001', 'extra': 1}).encode()
    (tmp_path / 'resource.json').write_bytes(body)
    manifest = {'runId': 'run-1', 'revision': 'a' * 40, 'buildRevision': 'a' * 40,
                'contractSha256': 'b' * 64, 'environment': 'isolated', 'dirty': False,
                'startedAt': '2026-10-21T10:00:00Z', 'finishedAt': '2026-10-21T10:01:00Z',
                'artifacts': {'resource.json': {'sha256': hashlib.sha256(body).hexdigest(),
                    'complete': True, 'correlationId': 'run-1', 'capturedAt': '2026-10-21T10:00:30Z'}}}
    raw = json.dumps(manifest).encode()
    (tmp_path / 'evidence.json').write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def evaluate(tmp_path, digest, prove, checks=('name',)):
    return kit.evaluate(app='demo', run_dir=tmp_path, revision='a' * 40,
        contract_sha256='b' * 64, manifest_sha256=digest,
        contracts={'create': kit.Contract(prove, checks, ('resource.json',), ('api',))})


class TestDurableEvidence:
    """Feature: Durable Evidence Evaluation"""

    def test_subset_matching_is_typed_and_order_independent(self):
        assert kit.matches_fields({'x': {'y': 1, 'z': 2}}, {'x': {'y': 1}})
        assert kit.contains_item([{'id': 2}, {'id': 1}], {'id': 1})
        assert not kit.matches_fields({'x': False}, {'x': 0})
        assert not kit.matches_fields({}, {'x': None})
        assert kit.count_matches([1, 2, 3], lambda x: x > 1, equals=2)
        assert not kit.field_satisfies({}, 'x', lambda x: x is None)
        with pytest.raises(ValueError):
            kit.count_matches([], bool, min_count=True)

    def test_saved_evidence_passes_with_original_receipt(self, tmp_path):
        digest = saved(tmp_path)
        receipt = evaluate(tmp_path, digest, lambda k: k.check('name', k.evidence.json('resource.json')['orderNumber'], 'ORD-1001'))
        assert receipt.verdict == 'PASS'
        assert set(receipt.to_json()) == {'verdict', 'revision', 'app', 'at', 'checks', 'features', 'surfaces', 'pageErrors', 'next'}
        subprocess.run([sys.executable, '-c',
            "import sys; sys.path.insert(0, " + repr(str(KIT.parent)) + "); import kit; assert 'playwright.sync_api' not in sys.modules"], check=True)

    @pytest.mark.parametrize('mode', ['tamper', 'missing', 'duplicate', 'mismatch', 'manifest', 'traversal'])
    def test_gaps_error_and_observed_mismatch_fails(self, tmp_path, mode):
        digest = saved(tmp_path)
        def prove(k):
            if mode == 'missing':
                return
            k.check('name', k.evidence.json('resource.json')['orderNumber'], 'wrong' if mode == 'mismatch' else 'ORD-1001')
            if mode == 'duplicate':
                k.check('name', True, True)
            if mode == 'traversal':
                k.evidence.json('../resource.json')
        if mode == 'tamper':
            (tmp_path / 'resource.json').write_text('{}')
        receipt = evaluate(tmp_path, '0' * 64 if mode == 'manifest' else digest, prove)
        assert receipt.verdict == ('FAIL' if mode == 'mismatch' else 'ERROR')

    def test_required_logs_are_scoped_and_complete(self):
        from durable_kit.logs import JsonLinesAdapter, LogView
        records = JsonLinesAdapter().parse('{"event":"Created","correlationId":"old","severity":"Error"}\n')
        view = LogView(records, correlation_id='new')
        assert not view.event_exists('Created')
        assert view.no_errors()
        with pytest.raises(ValueError):
            JsonLinesAdapter().parse('{broken')

    def test_test_reports_normalize_failures_skips_and_namespaces(self):
        from durable_kit.test_results import JUnitAdapter, TrxAdapter, all_passed, required_present
        result = JUnitAdapter().parse('<testsuite tests="2" failures="1" skipped="0"><testcase name="ok"/><testcase name="bad"><failure>bad</failure></testcase></testsuite>')
        assert result.failed == 1 and not all_passed(result)
        assert required_present(result, ['ok', 'bad'])
        trx = '<TestRun xmlns="urn:test"><Results><UnitTestResult testId="one" outcome="Passed"/></Results><ResultSummary><Counters total="1" executed="1" passed="1" failed="0" notExecuted="0"/></ResultSummary></TestRun>'
        assert all_passed(TrxAdapter().parse(trx))
        with pytest.raises(ValueError):
            JUnitAdapter().parse('<testsuite tests="2"><testcase name="one"/></testsuite>')

    @pytest.mark.parametrize('field,value', [
        ('revision', 'c' * 40), ('buildRevision', 'c' * 40), ('contractSha256', 'c' * 64),
        ('dirty', True), ('runId', ''), ('environment', ''), ('finishedAt', '2026-10-20T10:00:00Z'),
    ])
    def test_provenance_gaps_never_pass(self, tmp_path, field, value):
        saved(tmp_path)
        path = tmp_path / 'evidence.json'
        manifest = json.loads(path.read_bytes())
        manifest[field] = value
        raw = json.dumps(manifest).encode()
        path.write_bytes(raw)
        receipt = evaluate(tmp_path, hashlib.sha256(raw).hexdigest(), lambda k: k.check('name', True, True))
        assert receipt.verdict == 'ERROR'

    @pytest.mark.parametrize('field,value', [('complete', False), ('correlationId', 'old'),
        ('capturedAt', '2026-10-20T10:00:00Z'), ('sha256', '0' * 64)])
    def test_invalid_capture_never_passes(self, tmp_path, field, value):
        saved(tmp_path)
        path = tmp_path / 'evidence.json'
        manifest = json.loads(path.read_bytes())
        manifest['artifacts']['resource.json'][field] = value
        raw = json.dumps(manifest).encode()
        path.write_bytes(raw)
        assert evaluate(tmp_path, hashlib.sha256(raw).hexdigest(), lambda k: k.check('name', True, True)).verdict == 'ERROR'

    @pytest.mark.parametrize('mode', ['pass', 'failure', 'skip', 'zero', 'wrong-sha', 'wrong-run', 'missing-id', 'malformed', 'hash'])
    def test_test_report_gates(self, tmp_path, mode):
        from durable_kit.evidence import Evidence
        from durable_kit.test_results import JUnitAdapter, check_results
        from durable_kit.capture import Capture
        from datetime import datetime, timezone
        capture = Capture(tmp_path / 'run', run_id='one', revision='a' * 40, build_revision='a' * 40,
                          contract_sha256='b' * 64, environment='test')
        start = datetime.now(timezone.utc).isoformat()
        child = '<failure>broken</failure>' if mode == 'failure' else '<skipped/>' if mode == 'skip' else ''
        xml = '<testsuite/>' if mode == 'zero' else f'<testsuite><testcase name="required">{child}</testcase></testsuite>'
        if mode == 'malformed':
            xml = '<testsuite>'
        capture.add('tests.xml', xml.encode())
        run = {'runId': 'old' if mode == 'wrong-run' else 'one', 'revision': 'c' * 40 if mode == 'wrong-sha' else 'a' * 40,
               'dirty': False, 'startedAt': start, 'finishedAt': datetime.now(timezone.utc).isoformat(),
               'command': 'existing-tests', 'reportSha256': '0' * 64 if mode == 'hash' else hashlib.sha256(xml.encode()).hexdigest()}
        capture.add('run.json', json.dumps(run).encode())
        digest = capture.finish()
        def prove(k):
            check_results(k, 'tests.xml', 'run.json', JUnitAdapter(),
                required_ids=('absent',) if mode == 'missing-id' else ('required',))
        receipt = kit.evaluate(app='demo', run_dir=tmp_path / 'run', revision='a' * 40,
            contract_sha256='b' * 64, manifest_sha256=digest,
            contracts={'test': kit.Contract(prove, ('tests: no failures', 'tests: expected skips'), ('tests.xml', 'run.json'))})
        assert receipt.verdict == ('PASS' if mode == 'pass' else 'FAIL' if mode in ('failure', 'skip') else 'ERROR')

    def test_cli_order_example_is_offline_and_preserves_history(self, tmp_path):
        import shutil
        from durable_kit.capture import Capture, contract_digest
        from datetime import datetime, timezone
        template = KIT.parent
        proof = tmp_path / 'proof'
        proof.mkdir()
        shutil.copytree(KIT, proof / 'kit', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copytree(template / 'app/tools', proof / 'tools')
        shutil.copytree(template / 'mole', tmp_path / 'mole', ignore=shutil.ignore_patterns('__pycache__'))
        (proof / '__init__.py').write_text('')
        digest = contract_digest(proof)
        capture = Capture(tmp_path / 'run', run_id='one', revision='a' * 40, build_revision='a' * 40,
                          contract_sha256=digest, environment='isolated')
        observations = {'api/get-order.json': {'id': 'id1', 'orderNumber': 'ORD-1001', 'items': [{'sku': 'SKU-COFFEE', 'quantity': 2, 'extra': True}]},
            'tasks/create-order.json': {'state': 'Succeeded', 'resourceId': 'id1'},
            'browser/order-list.json': {'reloaded': True, 'rows': [{'id': 'id1', 'orderNumber': 'ORD-1001'}]},
            'browser/request.json': {'method': 'POST', 'path': '/orders', 'body': {'items': [{'sku': 'SKU-COFFEE', 'quantity': 2}]}},
            'browser/console.json': {'errors': []}}
        for name, value in observations.items():
            capture.add(name, json.dumps(value).encode())
        capture.add('browser/order-list.png', b'fixture-image-is-supplementary')
        capture.add('logs/application.jsonl', b'{"event":"OrderCreated","severity":"Information","correlationId":"one","properties":{"orderNumber":"ORD-1001"}}\n')
        start = datetime.now(timezone.utc).isoformat()
        xml = b'<testsuite tests="1"><testcase classname="order" name="create"/></testsuite>'
        capture.add('tests/results.xml', xml)
        capture.add('tests/run.json', json.dumps({'runId': 'one', 'revision': 'a' * 40, 'dirty': False,
            'startedAt': start, 'finishedAt': datetime.now(timezone.utc).isoformat(), 'command': 'existing-tests',
            'reportSha256': hashlib.sha256(xml).hexdigest()}).encode())
        manifest_digest = capture.finish()
        runner = '''import sys, runpy

def audit(event, args):
    if event in ('subprocess.Popen', 'os.system', 'socket.connect', 'socket.bind'):
        raise AssertionError('Evaluator attempted live I/O: ' + event)
    if event == 'import' and args[0].startswith('playwright'):
        raise AssertionError('Evaluator imported browser runtime')
sys.addaudithook(audit)
runpy.run_module('mole', run_name='__main__')
'''
        command = [sys.executable, '-c', runner, 'evaluate', '--app', 'order', '--run', str(tmp_path / 'run'),
            '--revision', 'a' * 40, '--contract-sha256', digest, '--manifest-sha256', manifest_digest,
            '--contract-module', 'proof.tools.order_example']
        for _ in range(2):
            result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, check=True)
            assert json.loads(result.stdout)['verdict'] == 'PASS'
        assert len(list((tmp_path / 'run/receipts').glob('*.json'))) == 2
        (proof / 'tools/order_example.py').write_text('raise AssertionError("unapproved contract executed")')
        result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
        assert result.returncode == 2
        assert 'Local contract code differs' in json.loads(result.stdout)['error']

    def test_log_adapters_and_matchers(self):
        from durable_kit.logs import JsonLinesAdapter, OtelAdapter, TextAdapter, LogView
        otel = {'resourceLogs': [{'scopeLogs': [{'logRecords': [{'timeUnixNano': '1',
            'severityText': 'ERROR', 'traceId': 'run', 'body': {'stringValue': 'Created 2'},
            'attributes': [{'key': 'event.name', 'value': {'stringValue': 'Created'}},
                           {'key': 'count', 'value': {'intValue': '2'}}]}]}]}]}
        view = LogView(OtelAdapter().parse(json.dumps(otel)), correlation_id='run')
        assert view.fields_match('Created', {'count': 2})
        assert view.count('Created', equals=1)
        assert view.message_contains(r'Created \d+', regex=True)
        assert not view.no_errors()
        assert view.no_errors(('Created',))
        text = TextAdapter('run', lambda line: 'Error' if 'error' in line else 'Information')
        assert not LogView(text.parse('error: failed'), correlation_id='run').no_errors()
        serilog = '{"Level":"Information","RenderedMessage":"created","Properties":{"EventId":"Created","CorrelationId":"run"}}'
        assert LogView(JsonLinesAdapter().parse(serilog), correlation_id='run').event_exists('Created')
        with pytest.raises(ValueError):
            JsonLinesAdapter().parse('{"event":"Created"}')

    def test_duplicate_retries_and_invalid_xml_are_rejected(self):
        from durable_kit.test_results import JUnitAdapter, TrxAdapter, JsonAdapter
        with pytest.raises(ValueError):
            JUnitAdapter().parse('<testsuite><testcase name="one"/><testcase name="one"/></testsuite>')
        with pytest.raises(ValueError):
            JUnitAdapter().parse('<!DOCTYPE x><testsuite/>')
        with pytest.raises(ValueError):
            JUnitAdapter().parse('<testsuite><testcase name="one"><flakyFailure/></testcase></testsuite>')
        with pytest.raises(ValueError):
            TrxAdapter().parse('<TestRun><Results><UnitTestResult testId="one" outcome="Passed"/></Results><ResultSummary outcome="Failed"><Counters total="1" passed="1"/></ResultSummary></TestRun>')
        assert JsonAdapter().parse('{"tests":[{"id":"one","outcome":"passed"}]}').passed == 1
        with pytest.raises(ValueError):
            JsonAdapter().parse('{"tests":[{"id":"one","outcome":"unknown"}]}')

    def test_capture_is_immutable_and_project_tools_survive_scaffold(self, tmp_path):
        from durable_kit.capture import Capture
        capture = Capture(tmp_path / 'run', run_id='one', revision='a' * 40, build_revision='a' * 40,
                          contract_sha256='b' * 64, environment='isolated')
        capture.add('a.json', b'{}')
        with pytest.raises(FileExistsError):
            capture.add('a.json', b'{}')
        capture.finish()
        with pytest.raises(ValueError):
            capture.add('b.json', b'{}')
        with pytest.raises(ValueError):
            capture.finish()
        script = KIT.parents[2] / 'scripts/scaffold.py'
        command = [sys.executable, str(script), '--repo', str(tmp_path / 'repo'), '--language', 'python',
                   '--surfaces', 'api', '--app-name', 'test', '--no-install']
        subprocess.run(command, check=True, capture_output=True)
        custom = tmp_path / 'repo/proof/tools/contracts.py'
        custom.write_text('# project extension')
        subprocess.run(command, check=True, capture_output=True)
        assert custom.read_text() == '# project extension'
