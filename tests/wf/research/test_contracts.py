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
ROLES = {'whyy': ('why/why.md', 'Investigator brief'), 'weby': ('web/web.md', 'Brief')}
CODEBASE_AGENT = REPO / 'plugins/wf/agents/codebase.agent.md'
ROUTES = {'Wayfinder': ('wayfinder/wayfinder.md', ()), 'How': ('how/how.md', ('codebase',)), 'Why': ('why/why.md', ('whyy',)),
          'Web': ('web/web.md', ('weby',))}


def role_prompt(role: str) -> str:
    path, heading = ROLES[role]
    text = (ROOT / path).read_text()
    if heading is None:
        return text
    start = re.search(rf'^## {re.escape(heading)}\n', text, re.M).end()
    end = re.compile(r'^## ', re.M).search(text, start)
    return text[start:end.start() if end else None]



def local_markdown_links(path: Path) -> set[Path]:
    links = set()
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        parts = urlsplit(link)
        if not parts.scheme and parts.path.endswith('.md') and not re.search(r'[<>{}]', parts.path):
            links.add((path.parent / unquote(parts.path)).resolve())
    return links


def test_inspection_lookup_prefixes_and_slim_codebase_brief():
    table = INSPECTION.split('| Lookup | Task prefix |')[1].split('\n\n')[0]
    assert table.strip().splitlines()[1:]
    assert '@research' not in INSPECTION
    for path in ROOT.rglob('*.md'):
        assert '@shape' not in path.read_text(), path.relative_to(ROOT)


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
            assert f'`{agent}`' in rows[route], (route, agent)
    for removed in ('## Explore request', '## Constraints', '## Conditional resources', '## Gotchas',
                    '## Dispatch and delivery', '## Generic brief', '| Graphify |'):
        assert removed not in ENTRY, removed


def test_role_prompts_are_playbook_sections_with_model_roles_and_one_guard():
    models = (SKILLS / 'subagents/models.md').read_text()
    spawning = ENTRY.split('## Spawning agents')[1].split('\n## ')[0]
    assert not (ROOT / 'agents').exists()
    assert 'Research route worker: never load the research or prove skill or spawn subagents' in spawning
    for role, (path, heading) in ROLES.items():
        prompt = role_prompt(role)
        assert '{QUESTION}' in prompt, role
        assert f'`{role}`' in spawning and f']({path})' in spawning, role
        if heading:
            assert f'section {heading}' in spawning, role
        assert f'| {role} |' in models, role
    for retired in ('composy', 'cloudy'):
        assert f'| {retired} |' not in models, retired
    assert 'Only this skill spawns its route workers' in ENTRY
    assert '| codebase |' not in models
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
    assert 'Explore' not in delivery
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


def test_explorer_accepts_evidence_without_path_policy():
    for field in ('QUESTION', 'EXPLORATION_ANGLE', 'TARGETS_OR_REFS', 'DEPTH', 'LENS_AND_CHECKS'):
        assert f'{{{field}}}' in PROMPT
    assert not re.search(r'\{(?:OUTPUT_PATH|OUTPUT_ARTIFACT)\}', PROMPT)


def test_router_writes_how_explanation_without_worker():
    assert 'explainy' not in HOW + REPORT + ENTRY
    assert not re.search(r'\{[A-Z_]+\}', REPORT)


def test_how_eval_cases_cover_evidence_and_delivery_failures():
    scenarios = json.loads((Path(__file__).parent / 'evals/how-scenarios.json').read_text())
    cases = scenarios['cases']
    ids = [case['id'] for case in cases]
    assert len(ids) == len(set(ids))
    assert {'focused_session', 'discover_ownership', 'cross_repo_handoff', 'nuget_implementation',
            'terminal_and_access_gap', 'provider_runtime_unknown', 'data_engine_specific',
            'requested_destinations', 'default_session_destination',
            'conflicting_destinations', 'multiple_reports', 'why_web_session'} <= set(ids)
    assert all(case['request'] and case['checks'] for case in cases)


def test_lookups_bypass_research_through_the_registered_codebase_agent():
    assert not (ROOT / 'explore').exists() and not (ROOT / 'agents/codebase.md').exists()
    assert not re.search(r'\bExplore\b', ENTRY.split('## Routing')[1].split('\n## ')[0])
    assert 'is not a Research route: spawn the `codebase` agent' in ENTRY
    assert CODEBASE_AGENT.is_file()
    for caller in ('design/playbooks/grill.md', 'design/playbooks/sketch.md', 'design/playbooks/wayfinder.md', 'review/playbooks/hitl.md'):
        text = (SKILLS / caller).read_text()
        assert '`codebase` agent' in text and 'Explore route' not in text and 'Research Explore' not in text, caller


def test_playbooks_spawn_only_bundled_prompt_agents_through_the_recipe():
    spawning = ENTRY.split('## Spawning agents')[1].split('\n## ')[0]
    assert 'never a registered agent' in spawning
    assert '**`codebase`** is the wf plugin\'s registered agent' in spawning
    assert 'never an agent type or `agentName`; use it only as the role and the spawn\'s display name' in spawning
    assert 'Read the role\'s prompt in full' in spawning
    for path in ROOT.rglob('*.md'):
        for name in re.findall(r'[Ss]pawn(?:s| one)? `([a-z]+)`', path.read_text()):
            assert name == 'codebase' or name in ROLES, (path.relative_to(ROOT), name)
    assert not list((REPO / 'plugins/wf/agents').glob('hunt*')) and not (SKILLS / 'explore-codebase').exists()


def test_long_research_resources_open_with_contents():
    for path in ROOT.rglob('*.md'):
        text = path.read_text()
        if path.name != 'SKILL.md' and len(text.splitlines()) > 100:
            assert '\n## Contents\n' in text, path.relative_to(ROOT)


@pytest.mark.parametrize('playbook, resources', [
    ('why/why.md', ('why/source-control.md', 'why/atlassian.md')),
    ('web/web.md', ('web/aws.md', 'web/azure.md')),
])
def test_why_and_web_load_sources_only_by_trigger(playbook: str, resources: tuple[str, ...]):
    table = (ROOT / playbook).read_text().split('## Conditional resources')[1].split('\n## ')[0]
    for resource in resources:
        assert (ROOT / resource).is_file(), resource
        assert re.search(rf'^\| [^|]+ \| `{re.escape(resource)}`( \([A-Za-z]+\))? \|$', table, re.M), resource
