from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / 'plugins/wf/skills'
ROOT = SKILLS / 'research'
ENTRY = (ROOT / 'SKILL.md').read_text()
HOW = (ROOT / 'how/how.md').read_text()
INSPECTION = (ROOT / 'how/inspection.md').read_text()
REPORT = (ROOT / 'how/report.md').read_text()
PROMPT = (ROOT / 'how/explorer-prompt.md').read_text()
EXPLAINER = (ROOT / 'agents/explainy.md').read_text()
AGENTS = ('hunty', 'explainy', 'whyy', 'composy', 'cloudy', 'weby')
ROUTES = {'Wayfinder': ('wayfinder/wayfinder.md', ()), 'Explore': ('explore/explore.md', ('hunty',)), 'How': ('how/how.md', ('hunty', 'explainy')), 'Why': ('why/why.md', ('whyy', 'composy')),
          'Cloud': ('cloud/cloud.md', ('cloudy',)), 'Web': ('web/web.md', ('weby',))}


def local_markdown_links(path: Path) -> set[Path]:
    links = set()
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        parts = urlsplit(link)
        if not parts.scheme and parts.path.endswith('.md') and not re.search(r'[<>{}]', parts.path):
            links.add((path.parent / unquote(parts.path)).resolve())
    return links


def test_inspection_lookup_prefixes_and_slim_hunty_brief():
    table = INSPECTION.split('| Lookup | `@work` prefix |')[1].split('\n\n')[0]
    assert table.strip().splitlines()[1:]
    hunty = (ROOT / 'agents/hunty.md').read_text()
    assert set(re.findall(r'^- `(@\w+)`', hunty.split('## Brief')[1].split('\n## ')[0], re.M)) == {'@work', '@frame', '@research'}
    for removed in ('@depth', '@shape', '@target', '@outputShape', '@inputs'):
        assert removed not in hunty, removed
    for path in ROOT.rglob('*.md'):
        assert '@shape' not in path.read_text(), path.relative_to(ROOT)
    assert 'Always explore thoroughly' in hunty


def test_report_is_separate_from_the_how_procedure():
    assert REPORT.index('## Answer') < REPORT.index('## How it works')
    assert '## Workflow' in HOW
    assert 'how/how.md' in ENTRY and 'how/report.md' in ENTRY
    assert not (ROOT / 'system').exists()


def test_router_maps_each_route_to_its_playbook_and_agent_prompts():
    table = ENTRY.split('## Routing')[1].split('\n## ')[0]
    rows = {row.split('|')[1].strip(): row for row in table.splitlines() if row.startswith('| ') and '---' not in row}
    assert set(rows) - {'Route'} == set(ROUTES)
    for route, (playbook, agents) in ROUTES.items():
        assert f']({playbook})' in rows[route], route
        for agent in agents:
            assert f'[{agent}](agents/{agent}.md)' in rows[route] or f'`{agent}`' in rows[route], (route, agent)
    for removed in ('## Explore request', '## Constraints', '## Conditional resources', '## Gotchas',
                    '## Dispatch and delivery', '## Generic brief', '| Graphify |'):
        assert removed not in ENTRY, removed


def test_agent_prompts_never_nest_and_have_model_roles():
    models = (SKILLS / 'subagents/models.md').read_text()
    assert set(path.stem for path in (ROOT / 'agents').glob('*.md')) == set(AGENTS)
    for agent in AGENTS:
        prompt = (ROOT / f'agents/{agent}.md').read_text()
        assert not prompt.startswith('---'), agent
        assert 'Never spawn subagents. Never load the `research` skill.' in prompt, agent
        assert f'| {agent} |' in models, agent
    assert 'Only this skill spawns research agents' in ENTRY
    assert '*Load and follow the `subagents` skill to select the model and effort for a named subagent role*' in ENTRY


def test_no_skill_spawns_retired_hunter_or_subagents_dispatch():
    plugin = REPO / 'plugins/wf'
    for path in plugin.rglob('*.md'):
        text = path.read_text()
        assert not re.search(r'`hunter`|\bHunter\b', text), path.relative_to(REPO)
        assert 'Explore request' not in text, path.relative_to(REPO)
        assert not re.search(r"`subagents` skill to dispatch", text), path.relative_to(REPO)
    assert not (plugin / 'skills/subagents/swarm.md').exists()


def test_every_bundled_markdown_resource_is_reachable_directly_from_entry():
    entry_links = local_markdown_links(ROOT / 'SKILL.md')
    resources = set(ROOT.rglob('*.md')) - {ROOT / 'SKILL.md'}
    assert resources <= entry_links
    for path in ROOT.rglob('*.md'):
        for linked in local_markdown_links(path):
            assert linked.is_file(), f'{path.relative_to(ROOT)} -> {linked}'
            assert linked.is_relative_to(ROOT), f'cross-skill resource: {linked}'


def test_research_routes_have_no_default_artifact_locations():
    for path in ROOT.rglob('*.md'):
        if path.relative_to(ROOT).parts[0] == 'wayfinder':
            continue
        content = path.read_text()
        for obsolete in ('docs/research/', '<slug>-chain.md', '<slug>-data.md', '<slug>-<provider>.md'):
            assert obsolete not in content, f'{path.relative_to(ROOT)}: {obsolete}'


def test_request_is_the_only_input_and_reports_default_to_the_session():
    request = ENTRY.split('## Request')[1].split('\n## ')[0]
    assert set(re.findall(r'`(@\w+)`', request)) == set()
    for removed in ('@mode', '@whyDepth', '@researchScope', '@outputPath', '@outputBase', '@outputShape', '## Inputs'):
        assert removed not in ENTRY, removed
    delivery = ENTRY.split('## Delivery')[1].split('\n## ')[0]
    assert '`<session>/files/research/<question-slug>.md`' in delivery
    assert 'Return only the report pointers, never the findings inline' in delivery
    assert 'read each in full before using its findings' in delivery
    assert '- Explore → return `hunty` verdicts inline' in delivery
    assert 'Request names a location → save there instead' in delivery


@pytest.mark.parametrize('relative_path', [
    'design/playbooks/architect.md',
    'design/playbooks/wayfinder.md',
    'design/references/evidence-routing.md',
    'review/playbooks/blast-radius.md',
    'review/playbooks/hitl.md',
    'install/assets/factory-mode/SKILL.md',
    'design/playbooks/grill.md',
])
def test_research_callers_name_destinations_in_the_request(relative_path: str):
    root = SKILLS if not relative_path.startswith('install/') else REPO / 'plugins/wf'
    caller = (root / relative_path).read_text()
    for removed in ('@mode', '@whyDepth', '@researchScope'):
        assert removed not in caller, (relative_path, removed)
    assert '.md' in caller


@pytest.mark.parametrize('relative_path', [
    'write/playbooks/toi.md',
    'write/playbooks/bug.md',
    'architecture-records/SKILL.md',
    'architecture-records/playbooks/concept.md',
    'architecture-records/playbooks/define-concept.md',
])
def test_lookup_callers_spawn_explore_directly(relative_path: str):
    caller = (SKILLS / relative_path).read_text()
    assert 'built-in `explore` subagent' in caller
    assert '`research` skill' not in caller


def test_explorer_and_explainy_accept_evidence_without_path_policy():
    for field in ('QUESTION', 'EXPLORATION_ANGLE', 'TARGETS_OR_REFS', 'DEPTH', 'LENS_AND_CHECKS'):
        assert f'{{{field}}}' in PROMPT
    assert '{EXPLORER_FINDINGS}' in EXPLAINER
    assert '{OUTPUT_SHAPE}' in EXPLAINER
    assert not re.search(r'\{(?:OUTPUT_PATH|OUTPUT_ARTIFACT)\}', PROMPT + EXPLAINER)


def test_how_eval_cases_cover_evidence_and_delivery_failures():
    scenarios = json.loads((Path(__file__).parent / 'evals/how-scenarios.json').read_text())
    cases = scenarios['cases']
    ids = [case['id'] for case in cases]
    assert len(ids) == len(set(ids))
    assert {'focused_session', 'discover_ownership', 'cross_repo_handoff', 'nuget_implementation',
            'terminal_and_access_gap', 'provider_runtime_unknown', 'data_engine_specific',
            'requested_destinations', 'default_session_destination',
            'conflicting_destinations', 'multiple_reports', 'why_cloud_web_session'} <= set(ids)
    assert all(case['request'] and case['checks'] for case in cases)


def test_explore_route_returns_hunty_verdicts_inline():
    explore = (ROOT / 'explore/explore.md').read_text()
    assert 'Spawn one `hunty` per lookup' in explore
    assert 'No explanation report, no file' in explore
    assert 'unabridged' in explore
    assert 'Size follows the question, not a length limit' in (ROOT / 'agents/hunty.md').read_text()
    assert '- Explore → return `hunty` verdicts inline to the requester; no file.' in ENTRY
    assert 'using the Explore route' in (SKILLS / 'design/playbooks/grill.md').read_text()


def test_playbooks_spawn_only_bundled_prompt_agents_through_the_recipe():
    spawning = ENTRY.split('## Spawning agents')[1].split('\n## ')[0]
    assert 'never a registered agent' in spawning
    assert 'never an agent type or `agentName`; use it only as the spawn\'s display name' in spawning
    assert 'Read `agents/<name>.md` in full' in spawning
    for path in ROOT.rglob('*.md'):
        for name in re.findall(r'[Ss]pawn(?:s| one)? `([a-z]+)`', path.read_text()):
            assert (ROOT / f'agents/{name}.md').is_file(), (path.relative_to(ROOT), name)
    assert not list((REPO / 'plugins/wf/agents').glob('hunt*'))


def test_long_research_resources_open_with_contents():
    for path in ROOT.rglob('*.md'):
        text = path.read_text()
        if path.name != 'SKILL.md' and len(text.splitlines()) > 100:
            assert '\n## Contents\n' in text, path.relative_to(ROOT)
