from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from atl_cli.page_diagrams import pipeline


@pytest.mark.parametrize('source', [
    '# Title\n\ntext\twith tab\n',
    '# Title\n\n<!-- adf:comment id="x" -->unclosed\n',
    '# Title\n\n<!-- adf:breakout mode="wide" -->\nparagraph\n',
    '# Title\n\n| a | b |\n| --- |\n',
    '# Title\n\n<!-- adf:lossy -->\nbody\n',
])
def test_guard_failure_precedes_remote_clients_and_mutations(tmp_path, monkeypatch, source):
    path = tmp_path / 'source.md'
    path.write_text(source)
    client = MagicMock(side_effect=AssertionError('remote client must not be reached'))
    monkeypatch.setattr(pipeline, 'get_confluence', client)
    monkeypatch.setattr(pipeline, 'load_renderer', lambda *_: 'png')
    monkeypatch.setattr(pipeline, 'load_swimlane_drawio_enabled', lambda *_: False)
    with pytest.raises((ValueError, RuntimeError)):
        pipeline.publish(str(path), str(tmp_path / 'cfg'), None, 'space', None, str(tmp_path / 'assets'), str(tmp_path / 'final.json'))
    client.assert_not_called()
    assert path.read_text() == source


def test_manifest_contains_body_before_server_readback(tmp_path, monkeypatch):
    path = tmp_path / 'source.md'
    path.write_text('# Title\n\n**Exact body**\n')
    monkeypatch.setattr(pipeline, 'load_renderer', lambda *_: 'png')
    monkeypatch.setattr(pipeline, 'load_swimlane_drawio_enabled', lambda *_: False)
    monkeypatch.setattr(pipeline, 'load_credentials', lambda *_: {})
    monkeypatch.setattr(pipeline, 'get_confluence', lambda *_: MagicMock())

    def create(client, space, title, adf, **kwargs):
        manifest = json.loads((tmp_path / 'final.manifest.json').read_text())
        assert manifest == {'title': title, 'adf': adf}
        return {'id': '1'}

    monkeypatch.setattr(pipeline, 'create_page_adf', create)
    result = pipeline.publish(str(path), 'cfg', None, 'space', None, str(tmp_path / 'assets'), str(tmp_path / 'final.json'))
    assert json.loads(open(result['manifestPath']).read())['adf']['content'][0]['content'][0]['marks'] == [{'type': 'strong'}]
