from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml


REPO = Path(__file__).resolve().parents[3]
SKILL = (REPO / 'plugins/wf/skills/research/SKILL.md').read_text()
FRONTMATTER, SKILL_BODY = re.match(r'^---\n(.*?)\n---\n(.*)$', SKILL, re.S).groups()
HUNTER = (REPO / 'plugins/wf/agents/hunter.agent.md').read_text()
EVALS = Path(__file__).parent / 'evals'
ROUTES = {'rg', 'lsp', 'graphify', 'github', 'nuget'}


def section(title: str, text: str = HUNTER) -> str:
    start = re.search(rf'^#{{2,3}} {re.escape(title)}\n', text, re.M).end()
    end = re.compile(r'^#{2,3} ', re.M).search(text, start)
    return text[start:end.start() if end else None]


def table_rows(text: str) -> list[list[str]]:
    rows = [l.strip() for l in text.splitlines() if l.strip().startswith('|')]
    return [[c.strip() for c in r.strip('|').split('|')] for r in rows[2:]] if rows else []


def test_frontmatter_parses_and_description_is_safe():
    meta = yaml.safe_load(FRONTMATTER)
    description = meta['description']
    assert meta['name'] == 'research'
    assert len(description) <= 1024
    assert 'how does this work' in description
    assert 'inspect this system' in description
    for char in ('—', '–', ': ', ' #', '<', '>'):
        assert char not in description, char


def test_body_under_300_lines():
    assert len(SKILL_BODY.splitlines()) < 300


def test_hunter_owns_explore_and_loads_the_nuget_tactic():
    assert not (REPO / 'plugins/wf/skills/research/explore/explore.md').exists()
    request = section('Explore request', SKILL_BODY)
    assert 'verbatim directly to a `hunter` subagent' in request
    assert 'If Hunter is unavailable, report the blocked evidence request' in request
    assert '(../skills/research/how/nuget.md)' in section('Route the lookup')
    assert 'Hunter never spawns subagents' in HUNTER


def test_request_lists_shape_enum():
    line = next(l for l in section('Explore request', SKILL_BODY).splitlines() if l.startswith('- `[@shape]`'))
    assert re.search(r'`([^`]+)`;', line).group(1) == 'literal | symbol | relationship | nuget'


def test_route_the_lookup_precedes_tool_selection():
    assert HUNTER.index('### Route the lookup') < HUNTER.index('### Select tools by question shape')
    route = section('Route the lookup')
    assert 'route: rg | lsp | graphify | github' in route
    assert {re.match(r'`(\w+)`', row[-1]).group(1) for row in table_rows(route)} == ROUTES


def test_rg_rules():
    tools = section('Tools', HUNTER)
    for text in ('exit codes', '`1` no match', 'Only `command -v rg` decides presence',
                 '**MUST NOT** run recursive `grep`', 'rg … || grep …'):
        assert text in tools, text


@pytest.mark.parametrize('step,verdict', [
    ('`graphify reflect --if-stale`', 'skip'),
    ('`.vocab.txt`', 'never write'),
    ('`graphify-out/cache/`', 'allowed'),
])
def test_graphify_read_only_overrides(step, verdict):
    row = next(r for r in table_rows(section('Graphify', HUNTER)) if step in r[0])
    assert verdict in row[-1]


def test_graphify_cli_first_cache_exception_and_not_found():
    assert 'inline `graph.json` traversal only when the CLI is missing' in section('Graphify', HUNTER)
    assert '`graphify query | path | explain` updating `graphify-out/cache/`' in section('Read-only contract', HUNTER)
    read_only = section('Read-only contract')
    assert "brief's `@outputArtifact`" in read_only
    assert 'decompilation written only to the resolved NuGet package cache' in read_only
    verdict = section('Return the verdict')
    assert 'repeats the `route:` line' in verdict
    assert 'exactly `NOT FOUND`' in verdict


def test_eval_scenarios_cover_every_route():
    scenarios = json.loads((EVALS / 'scenarios.json').read_text())
    cases = scenarios['cases']
    assert {'rg_shell_literal', 'rg_shell_absent_literal', 'rg_backend_literal', 'graphify_relationship',
            'lsp_symbol', 'github_no_checkout', 'nuget_restored_package'} <= {c['id'] for c in cases}
    assert {c['expectedRoute'] for c in cases} == ROUTES
    pattern = re.compile(scenarios['routeLinePattern'])
    for case in cases:
        assert re.search(r'@shape: (literal|symbol|relationship|nuget)', case['request']), case['id']
        assert pattern.match(f"route: {case['expectedRoute']} — reason"), case['id']
