from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[3]
AGENT_PATH = REPO / 'plugins/wf/agents/codebase.agent.md'
AGENT = AGENT_PATH.read_text()
META, BODY = re.match(r'^---\n(.*?)\n---\n(.*)$', AGENT, re.S).groups()


def section(title: str) -> str:
    start = re.search(rf'^## {re.escape(title)}\n', BODY, re.M).end()
    end = re.compile(r'^## ', re.M).search(BODY, start)
    return BODY[start:end.start() if end else None]


def test_agent_is_registered_with_model_preferences_and_safe_description():
    meta = yaml.safe_load(META)
    assert meta['name'] == 'codebase'
    assert isinstance(meta['model'], list) and meta['model']
    assert all(isinstance(model, str) and model for model in meta['model'])
    assert 'tools' not in meta
    assert len(meta['description']) <= 1024
    for char in ('—', '–', ': ', ' #', '<', '>'):
        assert char not in meta['description'], char
    assert not (REPO / 'plugins/wf/skills/explore-codebase').exists()
    assert not (REPO / 'plugins/wf/agents/hunty.agent.md').exists()


def test_agent_is_read_only_and_never_nests():
    rules = section('Rules')
    assert 'Read-only' in rules and 'clones, or fetches' in rules
    assert 'per-user `rg` or `ilspycmd` install when missing' in rules
    assert 'official sources without sudo' in rules and 'verify release checksums' in rules
    assert '**MUST NOT** spawn subagents' in rules
    assert 'Never load the `research` or `prove` skill' in rules
    assert 'quick | thorough' in rules and 'default `thorough`' in rules
    assert 'medium' not in AGENT


def test_agent_keeps_vscode_explore_base():
    for heading in ('Search Strategy', 'Speed Principles', 'Output'):
        assert f'## {heading}\n' in BODY, heading
    assert 'broad to narrow' in section('Search Strategy')


def test_targets_cover_deployables_multi_repo_and_missing_checkouts():
    targets = section('Targets and repos')
    assert 'Multi-repo' in targets and 'named worktree' in targets
    assert 'unresolved' in targets and 'Never substitute' in targets


def test_agent_uses_caller_scope_with_local_discovery_fallback():
    targets = section('Targets and repos')
    assert 'caller' in targets and 'source checkout/ref' in targets
    assert 'With no target, use the launch repository' in targets
    assert 'local startup or deployment evidence' in targets
    assert 'outside the supplied checkouts' in targets
    assert 'caller-supplied docs' in targets


def test_terminal_search_and_nuget_rules():
    search = section('Search Strategy')
    gotchas = section('Gotchas')
    assert 'rg -uu' in search and 'exit `1` = no match' in gotchas
    assert 'native' in search and 'glob' in search and '`rg --files`' in search
    assert all(tool in search for tool in ('go-to-definition', 'find-references', 'call hierarchy'))
    assert 'text search' in search and 'config wiring' in search
    assert '`rg -F`' in search and 'Cite every in-scope hit' in search
    assert 'no fixed-string mode or truncated results' in search and 'incomplete coverage' in search
    assert 'every searched root' in search
    assert '**MUST NOT** use recursive shell grep' in search and 'rg … || grep …' in search
    assert '`ilspycmd`' not in gotchas
    assert '## Shell search' not in BODY and '## Task prefixes' not in BODY
    assert 'Inaccessible source is a gap, not a terminal' in BODY
    nuget = section('NuGet')
    assert 'project.assets.json' in nuget and 'ilspycmd' in nuget
    assert '**XML documentation**' in nuget and '**decompiled implementation**' in nuget


def test_no_graphify_or_route_table():
    assert not re.search(r'graphify|graph\.py|@route|route: ', AGENT, re.I)
    assert '`NOT FOUND`' in section('Output')
