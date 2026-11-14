from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[3] / 'plugins/wf/skills/research/scripts'
sys.path.insert(0, str(SCRIPTS))

import graph  # noqa: E402

GRAPH = {
    'directed': True,
    'built_at_commit': 'abc123',
    'nodes': [
        {'id': 'c', 'label': 'OrdersController', 'source_file': 'workspace/shop/src/OrdersController.cs', 'source_location': 'L5', 'file_type': 'code'},
        {'id': 'i', 'label': 'IOrderJanitor', 'source_file': 'workspace/shop/src/IOrderJanitor.cs', 'source_location': 'L1', 'file_type': 'code'},
        {'id': 'j', 'label': 'OrderJanitor', 'source_file': 'workspace/shop/src/OrderJanitor.cs', 'source_location': 'L9', 'file_type': 'code'},
        {'id': 't', 'label': 'ShipmentTask', 'source_file': 'workspace/shop/bin/ShipmentTask.cs', 'source_location': 'L2', 'file_type': 'code'},
    ],
    'links': [
        {'source': 'c', 'target': 'i', 'relation': 'references', 'context': 'field', 'confidence': 'EXTRACTED'},
        {'source': 'j', 'target': 'i', 'relation': 'implements', 'confidence': 'EXTRACTED'},
        {'source': 'j', 'target': 't', 'relation': 'calls', 'context': 'call', 'confidence': 'INFERRED'},
    ],
}


@pytest.fixture
def graph_path(tmp_path: Path) -> Path:
    path = tmp_path / 'graphify-out/graph.json'
    path.parent.mkdir()
    path.write_text(json.dumps(GRAPH))
    return path


def run(capsys: pytest.CaptureFixture[str], graph_path: Path, *args: str) -> tuple[int, str]:
    code = graph.main(['--graph', str(graph_path), *args])
    return code, capsys.readouterr().out


def test_check_reports_missing_graph(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    assert graph.main(['--graph', str(tmp_path / 'none.json'), 'check']) == 1
    assert 'No graph found' in capsys.readouterr().err


def test_check_reports_unknown_freshness_and_noise(graph_path: Path, capsys: pytest.CaptureFixture[str]):
    code, out = run(capsys, graph_path, 'check')
    assert code == 0
    assert 'built_at_commit: abc123 | freshness: unknown' in out
    assert 'bin/ (1)' in out


def test_vocab_splits_camel_case_without_writing(graph_path: Path, capsys: pytest.CaptureFixture[str]):
    _, out = run(capsys, graph_path, 'vocab')
    assert {'orders', 'controller', 'janitor', 'shipment'} <= set(out.splitlines())
    assert sorted(p.name for p in graph_path.parent.iterdir()) == ['graph.json']


def test_slice_follows_direction_and_filters(graph_path: Path, capsys: pytest.CaptureFixture[str]):
    _, out = run(capsys, graph_path, 'slice', 'IOrderJanitor', '--direction', 'in', '--relation', 'implements')
    assert 'NODE depth=1 OrderJanitor' in out and 'OrdersController' not in out


def test_raw_path_is_directed_unless_undirected(graph_path: Path, capsys: pytest.CaptureFixture[str]):
    _, out = run(capsys, graph_path, 'raw-path', 'OrdersController', 'ShipmentTask')
    assert out.startswith('No path found')
    _, out = run(capsys, graph_path, 'raw-path', 'OrdersController', 'ShipmentTask', '--undirected')
    assert 'Shortest path (3 hops)' in out


def test_traverse_filters_context(graph_path: Path, capsys: pytest.CaptureFixture[str]):
    _, out = run(capsys, graph_path, 'traverse', 'OrderJanitor', '--context', 'call')
    assert "Start: ['OrderJanitor']" in out
    assert 'EDGE OrderJanitor --calls' in out and 'implements' not in out
