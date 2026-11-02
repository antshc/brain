from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml


REPO = Path(__file__).resolve().parents[3]
SKILL = (REPO / 'plugins/wf/skills/explore-codebase/SKILL.md').read_text()
FRONTMATTER, BODY = re.match(r'^---\n(.*?)\n---\n(.*)$', SKILL, re.S).groups()
EVALS = Path(__file__).parent / 'evals'
ROUTES = {'rg', 'lsp', 'graphify', 'github'}


def section(title: str) -> str:
    start = re.search(rf'^#{{2,3}} {re.escape(title)}\n', BODY, re.M).end()
    end = re.compile(r'^#{2,3} ', re.M).search(BODY, start)
    return BODY[start:end.start() if end else None]


def table_rows(text: str) -> list[list[str]]:
    rows = [l.strip() for l in text.splitlines() if l.strip().startswith('|')]
    return [[c.strip() for c in r.strip('|').split('|')] for r in rows[2:]] if rows else []


def test_frontmatter_parses_and_description_is_safe():
    meta = yaml.safe_load(FRONTMATTER)
    description = meta['description']
    assert meta['name'] == 'explore-codebase'
    assert len(description) <= 1024
    assert '@work' in description
    for char in ('—', '–', ': ', ' #', '<', '>'):
        assert char not in description, char


def test_body_under_300_lines():
    assert len(BODY.splitlines()) < 300


def test_request_lists_shape_enum():
    line = next(l for l in section('Request').splitlines() if l.startswith('- `[@shape]`'))
    assert re.search(r'`([^`]+)`;', line).group(1) == 'literal | symbol | relationship'


def test_route_the_lookup_precedes_tool_selection():
    assert BODY.index('### Route the lookup') < BODY.index('### Select tools by question shape')
    route = section('Route the lookup')
    assert 'route: rg | lsp | graphify | github' in route
    assert {re.match(r'`(\w+)`', row[-1]).group(1) for row in table_rows(route)} == ROUTES


def test_rg_rules():
    tools = section('Select tools by question shape')
    for text in ('exit codes', '`1` no match', 'Only `command -v rg` decides presence',
                 '**MUST NOT** run recursive `grep`', 'rg … || grep …'):
        assert text in tools, text


@pytest.mark.parametrize('step,verdict', [
    ('`graphify reflect --if-stale`', 'skip'),
    ('`.vocab.txt`', 'never write'),
    ('`graphify-out/cache/`', 'allowed'),
])
def test_graphify_read_only_overrides(step, verdict):
    row = next(r for r in table_rows(section('Select tools by question shape')) if step in r[0])
    assert verdict in row[-1]


def test_graphify_cli_first_cache_exception_and_not_found():
    assert '`graphify` on `PATH` → query through `graphify query | path | explain`; inline `graph.json` traversal only when the CLI is missing' in BODY
    assert '`graphify query`/`path`/`explain` updating `graphify-out/cache/`' in section('Read-only contract')
    verdict = section('Return the verdict')
    assert 'repeats the `route:` line' in verdict
    assert 'exactly `NOT FOUND`' in verdict


def test_eval_scenarios_cover_every_route():
    scenarios = json.loads((EVALS / 'scenarios.json').read_text())
    cases = scenarios['cases']
    assert {'rg_shell_literal', 'rg_shell_absent_literal', 'rg_backend_literal', 'graphify_relationship',
            'lsp_symbol', 'github_no_checkout'} <= {c['id'] for c in cases}
    assert {c['expectedRoute'] for c in cases} == ROUTES
    pattern = re.compile(scenarios['routeLinePattern'])
    for case in cases:
        assert re.search(r'@shape: (literal|symbol|relationship)', case['request']), case['id']
        assert pattern.match(f"route: {case['expectedRoute']} — reason"), case['id']
