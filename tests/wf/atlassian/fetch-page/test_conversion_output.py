from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from atl_cli.fetch_page import assemble_page


def test_atomic_write_preserves_existing_file_if_replace_fails(tmp_path, monkeypatch):
    target = tmp_path / 'page.md'
    target.write_text('existing')

    def fail(*_):
        raise OSError('replace failed')

    monkeypatch.setattr(os, 'replace', fail)
    with pytest.raises(OSError, match='replace failed'):
        assemble_page.atomic_write_markdown(target, 'replacement')
    assert target.read_text() == 'existing'
    assert sorted(path.name for path in tmp_path.iterdir()) == ['page.md']


def test_fetch_lint_failure_keeps_existing_output(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'page.md'
    path.write_text('existing')
    monkeypatch.setattr(assemble_page, 'require_supported_library', lambda: None)
    monkeypatch.setattr(assemble_page, 'load_credentials', lambda *_: {'site': 'https://example.com'})
    monkeypatch.setattr(assemble_page, 'get_confluence', lambda *_: MagicMock())
    monkeypatch.setattr(assemble_page, 'fetch_page', lambda *_: ('Title', {'type': 'doc', 'content': []}))
    monkeypatch.setattr(assemble_page, 'assemble', lambda *_: '# Title\n\ntext\twith tab\n')
    with pytest.raises(SystemExit) as exception:
        assemble_page.main(['--page-id', '1', '--config', 'cfg', '--md-path', str(path), '--comments', 'skip'])
    assert exception.value.code == 1
    assert 'MD010' in capsys.readouterr().err
    assert path.read_text() == 'existing'
