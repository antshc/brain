from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml


REPO = Path(__file__).resolve().parents[3]
SKILL = (REPO / 'plugins/wf/skills/research/SKILL.md').read_text()
FRONTMATTER, SKILL_BODY = re.match(r'^---\n(.*?)\n---\n(.*)$', SKILL, re.S).groups()
HUNTY = (REPO / 'plugins/wf/skills/research/agents/hunty.md').read_text()
EVALS = Path(__file__).parent / 'evals'
ROUTES = {'rg', 'lsp', 'graphify-path', 'graphify-find', 'nuget', 'unresolved'}


def section(title: str, text: str = HUNTY) -> str:
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
    assert 'trace this flow' in description
    assert 'find callers of X' in description
    for char in ('—', '–', ': ', ' #', '<', '>'):
        assert char not in description, char


def test_body_under_300_lines():
    assert len(SKILL_BODY.splitlines()) < 300


def test_hunty_is_a_research_prompt_that_loads_the_nuget_tactic():
    assert not (REPO / 'plugins/wf/agents/hunter.agent.md').exists()
    assert '## Explore request' not in SKILL_BODY
    assert '`@research/how/nuget.md`' in section('Tools')
    assert 'Never spawn subagents or call the agent-launch tool. Never load the `research` or `prove` skill' in HUNTY
    assert not HUNTY.startswith('---')


def test_sections_and_route_table():
    order = ['## Brief', '## Read-only contract', '## Resolve the target', '## Route the lookup', '## Tools', '## Gotchas', '## Completeness sweep', '## Return']
    assert [HUNTY.index(h) for h in order] == sorted(HUNTY.index(h) for h in order)
    assert '## Graphify' not in HUNTY and '## Return the verdict' not in HUNTY
    route = section('Route the lookup')
    assert 'route: rg | lsp | graphify-path | graphify-find | nuget | unresolved' in route
    assert {re.match(r'`([\w-]+)`', row[-1]).group(1) for row in table_rows(route)} == ROUTES


def test_rg_gotchas():
    gotchas = section('Gotchas')
    for text in ('exit `1` means no match', 'only `command -v rg` decides presence',
                 '**MUST NOT** run recursive `grep`', 'rg … || grep …', 'rg -uu'):
        assert text in gotchas, text


def test_graphify_is_a_tool_with_read_only_overrides():
    tools = section('Tools')
    assert '**Graphify**' in tools and '**NuGet**' in tools
    assert 'skip `graphify reflect --if-stale`' in tools
    assert 'never `save-result`, `--update`' in tools
    assert '`graph.py raw-path | explain | traverse` only when both are missing' in tools
    assert '`path <A> <B>` before any `query` or `rg`' in tools
    assert '**MUST NOT** pass question text to `graphify query`' in section('Gotchas')
    read_only = section('Read-only contract')
    assert '`graphify query | path | explain` updating `graphify-out/cache/`' in read_only
    assert 'decompilation written only to the resolved NuGet package cache' in read_only
    ret = section('Return')
    assert 'Repeat the `route:` line' in ret
    assert 'exactly `NOT FOUND`' in ret


def test_eval_scenarios_cover_every_route():
    scenarios = json.loads((EVALS / 'scenarios.json').read_text())
    cases = scenarios['cases']
    assert {'rg_shell_literal', 'rg_shell_absent_literal', 'rg_backend_literal', 'graphify_path_flow', 'graphify_find_unknown',
            'lsp_symbol', 'missing_local_checkout', 'nuget_restored_package'} <= {c['id'] for c in cases}
    assert {c['expectedRoute'] for c in cases} == ROUTES
    pattern = re.compile(scenarios['routeLinePattern'])
    for case in cases:
        assert case['request'].startswith('@work: '), case['id']
        assert pattern.match(f"route: {case['expectedRoute']} — reason"), case['id']


def test_missing_checkout_blocks_lookup_without_remote_fallback():
    target = section('Resolve the target')
    assert 'checkout' in target and 'unresolved' in target
    route = section('Route the lookup')
    row = next(row for row in table_rows(route) if 'no local checkout' in row[0])
    assert row[-1].startswith('`unresolved`')
    assert 'github' not in route.lower()
    read_only = section('Read-only contract')
    assert 'clone' in read_only and 'fetch' in read_only
    assert 'GitHub Repository tactic' not in HUNTY


def test_completeness_sweep_runs_last_and_maps_every_obligation():
    sweep = section('Completeness sweep')
    assert 'Run last, after every search and before Return' in sweep
    assert 'Re-read `@work`' in sweep
    assert 'Map each obligation to cited evidence' in sweep
    assert 'Return only when every obligation has evidence or an explicit mark' in sweep
