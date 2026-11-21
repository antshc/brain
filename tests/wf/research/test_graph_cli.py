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


@pytest.fixture
def impact_graph(tmp_path: Path) -> Path:
    nodes = [
        ('controller', 'OrderController', 'src/OrderController.cs'),
        ('handler', 'OrderHandler', 'src/OrderHandler.cs'),
        ('service', 'OrderService', 'src/OrderService.cs'),
        ('other_service', 'OrderService', 'src/LegacyOrderService.cs'),
        ('repository', 'OrderRepository', 'src/OrderRepository.cs'),
        ('config', 'OrderConfig', 'src/OrderConfig.cs'),
        ('generated', 'OrderGenerated', 'obj/OrderGenerated.cs'),
    ]
    edges = [
        ('controller', 'handler', 'calls'),
        ('handler', 'service', 'calls'),
        ('service', 'repository', 'calls'),
        ('config', 'service', 'references'),
        ('generated', 'service', 'calls'),
    ]
    path = tmp_path / 'graph.json'
    path.write_text(json.dumps({
        'directed': False,  # Graphify can serialize directed edges with this flag off.
        'nodes': [
            {'id': nid, 'label': label, 'source_file': source, 'source_location': 'L1'}
            for nid, label, source in nodes
        ],
        'edges': [
            {'source': src, 'target': dst, 'relation': rel, 'source_location': 'L12'}
            for src, dst, rel in edges
        ],
    }))
    return path


def test_affected_follows_reverse_edges_and_production_filters(impact_graph, capsys):
    code, out = run(capsys, impact_graph, 'affected', 'service')
    assert code == 0
    assert 'OrderHandler [calls] src/OrderHandler.cs:L12' in out
    assert 'OrderController [calls]' in out
    assert 'OrderConfig [references]' in out
    assert 'OrderRepository' not in out
    assert 'OrderGenerated' not in out
    assert [p.name for p in impact_graph.parent.iterdir()] == ['graph.json']


def test_affected_limits_depth_and_relations(impact_graph, capsys):
    code, out = run(capsys, impact_graph, 'affected', 'src/OrderService.cs::OrderService',
                    '--depth', '1', '--relation', 'calls', '--relation', 'imports')
    assert code == 0
    assert 'OrderHandler [calls]' in out
    assert 'OrderController' not in out
    assert 'OrderConfig' not in out
    assert 'Relations: calls, imports' in out


def test_affected_distinguishes_ambiguous_missing_and_empty(impact_graph, capsys):
    argv = ['--graph', str(impact_graph), 'affected']
    assert graph.main([*argv, 'OrderService']) == 5
    err = capsys.readouterr().err
    assert 'ambiguous symbol' in err
    assert 'service: OrderService' in err and 'other_service: OrderService' in err
    assert graph.main([*argv, 'AbsentService']) == 4
    assert "no node matches 'AbsentService'" in capsys.readouterr().err
    code, out = run(capsys, impact_graph, 'affected', 'other_service')
    assert code == 0
    assert 'No affected nodes found.' in out


def test_focused_path_preserves_dependency_direction(impact_graph, capsys):
    code, out = run(capsys, impact_graph, 'path', 'OrderController', 'OrderRepository', '--directed')
    assert code == 0
    assert out.startswith('Path (3 hops):')
    code, out = run(capsys, impact_graph, 'path', 'OrderRepository', 'OrderController', '--directed')
    assert code == 0
    assert out.startswith('No path between')


def test_focused_path_leaves_interface_binding_for_source_trace(graph_path, capsys):
    code, out = run(capsys, graph_path, 'path', 'OrdersController', 'IOrderJanitor', '--directed')
    assert code == 0
    assert out.startswith('Path (1 hops):')
    code, out = run(capsys, graph_path, 'path', 'OrdersController', 'OrderJanitor', '--directed')
    assert code == 0
    assert out.startswith('No path between')
    code, out = run(capsys, graph_path, 'affected', 'IOrderJanitor')
    assert code == 0
    assert 'OrdersController [references]' in out
    assert 'OrderJanitor [implements]' in out
