from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / 'plugins/wf/skills/hunty'
SKILL = (ROOT / 'SKILL.md').read_text()
FRONTMATTER, BODY = re.match(r'^---\n(.*?)\n---\n(.*)$', SKILL, re.S).groups()
AGENT = (REPO / 'plugins/wf/agents/hunty.agent.md').read_text()
AGENT_META, AGENT_BODY = re.match(r'^---\n(.*?)\n---\n(.*)$', AGENT, re.S).groups()
EVALS = Path(__file__).parent / 'evals'
ROUTES = {'rg', 'lsp', 'graphify-path', 'graphify-find', 'nuget', 'unresolved'}


def section(title: str, text: str = BODY) -> str:
    start = re.search(rf'^#{{2,3}} {re.escape(title)}\n', text, re.M).end()
    end = re.compile(r'^#{2,3} ', re.M).search(text, start)
    return text[start:end.start() if end else None]


def table_rows(text: str) -> list[list[str]]:
    rows = [l.strip() for l in text.splitlines() if l.strip().startswith('|')]
    return [[c.strip() for c in r.strip('|').split('|')] for r in rows[2:]] if rows else []


def test_skill_frontmatter_parses_and_description_is_safe():
    meta = yaml.safe_load(FRONTMATTER)
    assert meta['name'] == 'hunty'
    assert len(meta['description']) <= 1024
    assert '→ `research`' in meta['description']
    for char in ('—', '–', ': ', ' #', '<', '>'):
        assert char not in meta['description'], char
    assert len(BODY.splitlines()) < 300


def test_agent_is_registered_read_only_pins_a_model_and_never_spawns():
    meta = yaml.safe_load(AGENT_META)
    assert meta['name'] == 'hunty'
    assert meta['model'] and 'tools' not in meta
    assert '**MUST NOT** spawn subagents' in AGENT_BODY
    assert 'Never load the `research` or `prove` skill' in AGENT_BODY
    assert '*Load and follow the `hunty` skill' in AGENT_BODY
    assert 'quick | medium | thorough' in AGENT_BODY
    agent_routes = {re.match(r'`([\w-]+)`', row[0]).group(1) for row in table_rows(section('Routes', AGENT_BODY))}
    assert agent_routes == ROUTES
    assert 'the routes as `@route`' in section('Workflow', AGENT_BODY)


def test_skill_forbids_nesting_and_takes_a_slim_brief():
    assert 'Never spawn subagents. Never load the `research` or `prove` skill' in BODY
    assert set(re.findall(r'^- `(@\w+)`', section('Brief'), re.M)) == {'@work', '@frame', '@thoroughness', '@route', '@hunty'}
    assert 'always explore thoroughly' in section('Rules')


def test_route_table_links_each_route_reference_directly():
    route = section('Route the lookup')
    assert 'route: rg | lsp | graphify-path | graphify-find | nuget | unresolved' in route
    rows = table_rows(route)
    assert {re.match(r'`([\w-]+)`', row[1]).group(1) for row in rows if row[1].startswith('`')} == ROUTES
    assert 'Honor a valid `@route`' in route
    links = {unquote(urlsplit(l).path) for l in re.findall(r'\]\(([^)]+)\)', route)}
    assert links == {f'references/{n}.md' for n in ('search', 'graph', 'graph-fallback', 'nuget')}
    assert {p.relative_to(ROOT).as_posix() for p in (ROOT / 'references').glob('*.md')} == links
    assert not (ROOT / 'references/routes').exists()


def test_references_never_load_another_file():
    for path in (ROOT / 'references').glob('*.md'):
        assert not re.findall(r'\]\(([^)#]+\.md)', path.read_text()), path.name


def test_read_only_contract_and_graph_overrides():
    read_only = section('Read-only contract')
    assert '`graphify query | path | explain` updating `graphify-out/cache/`' in read_only
    assert 'decompilation written only to the resolved NuGet package cache' in read_only
    assert 'clone' in read_only and 'fetch' in read_only
    graph = (ROOT / 'references/graph.md').read_text()
    fallback = (ROOT / 'references/graph-fallback.md').read_text()
    rules = section('Rules', graph)
    assert 'Never build, `--update`, re-cluster, `save-result`' in rules and 'never question text' in rules
    assert '@hunty/scripts/graph.py' in graph
    assert '`$GRAPH path <A> <B>`' in section('Route graphify-path', graph)
    assert 'Never save results back' in fallback
    for text in (graph, fallback):
        assert not re.search(r'save-result --|--outcome|reflect --if-stale', text)


def test_rg_gotchas():
    gotchas = section('Gotchas')
    assert '**MUST NOT** run recursive `grep`' in gotchas and 'rg … || grep …' in gotchas and 'rg -uu' in gotchas
    rg = section('Gotchas', (ROOT / 'references/search.md').read_text())
    assert 'exit `1` means no match' in rg and 'only `command -v rg` decides presence' in rg


def test_missing_checkout_blocks_lookup_without_remote_fallback():
    target = section('Resolve the target')
    assert 'checkout' in target and 'unresolved' in target
    row = next(row for row in table_rows(section('Route the lookup')) if 'no local checkout' in row[0])
    assert row[1].startswith('`unresolved`')
    assert 'github' not in section('Route the lookup').lower()


def test_completeness_sweep_runs_last_and_return_contract():
    sweep = section('Completeness sweep')
    assert 'Run last, after every search and before Return' in sweep
    assert 'Map each obligation to cited evidence' in sweep
    ret = section('Return')
    assert 'Repeat the `route:` line' in ret and 'exactly `NOT FOUND`' in ret
    assert 'Size follows the question, not a length limit' in ret


def test_eval_scenarios_cover_every_route():
    scenarios = json.loads((EVALS / 'scenarios.json').read_text())
    cases = scenarios['cases']
    assert {c['expectedRoute'] for c in cases} == ROUTES
    pattern = re.compile(scenarios['routeLinePattern'])
    for case in cases:
        assert case['request'].startswith('@work: '), case['id']
        assert pattern.match(f"route: {case['expectedRoute']} — reason"), case['id']
