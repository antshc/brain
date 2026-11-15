from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / 'plugins/wf/skills/architecture-records'


def local_links(path: Path) -> set[Path]:
    targets = set()
    content = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
    for target in re.findall(r'\]\(([^)]+)\)', content):
        parsed = urlsplit(target)
        if not parsed.scheme and parsed.path.endswith(('.md', '.py')) and '{' not in parsed.path:
            targets.add((path.parent / unquote(parsed.path)).resolve())
    return targets


def test_route_selectors_retain_recording_contracts_and_expose_new_routes():
    entry = (ROOT / 'SKILL.md').read_text()
    front = yaml.safe_load(entry.split('---')[1])
    assert front['name'] == ROOT.name
    assert len(front['description']) <= 300
    assert not (ROOT.parent / 'record-architecture').exists()
    routes = entry.split('## Routes\n')[1].split('\n## ')[0]
    rows = dict(re.findall(r'^\| `([^`]+)` \| ([^\n]+)', routes, re.M))
    assert set(rows) == {'define-concept', 'adr', 'building-block', 'deployment-view', 'term',
                         'concept-body', 'concept-record', 'decision-bullet', 'initialize', 'index', 'doctor'}
    for route, row in rows.items():
        if route != 'decision-bullet':
            assert re.search(r'\]\(playbooks/[^)]+\.md\)', row), route
    assert 'playbooks/concept.md' in rows['concept-body']
    assert 'playbooks/concept.md' in rows['concept-record']


def test_all_executable_resources_are_directly_disclosed_and_skill_local():
    entry_links = local_links(ROOT / 'SKILL.md')
    resources = {path.resolve() for folder in ('playbooks', 'references', 'templates', 'scripts')
                 for path in (ROOT / folder).rglob('*') if path.suffix in {'.md', '.py'}}
    assert resources <= entry_links
    for path in (ROOT / 'SKILL.md', *ROOT.rglob('*.md')):
        if path.name == 'README.md':
            continue
        for linked in local_links(path):
            if path.parent.name == 'templates' and linked.name in {'ARCHITECTURE.md', 'GLOSSARY.md', 'DEPLOYMENT.md'}:
                continue
            assert linked.is_file(), (path, linked)
            assert linked.is_relative_to(ROOT.resolve()), (path, linked)
        if path != ROOT / 'SKILL.md':
            assert not re.search(r'Load and follow the `architecture-records` skill', path.read_text()), path


def test_index_actions_and_render_only_selectors_remain_distinct():
    entry = (ROOT / 'SKILL.md').read_text()
    actions = entry.split('## Index actions')[1].split('## Resource map')[0]
    assert set(re.findall(r'^\| `([^`]+)` \|', actions, re.M)) == {
        'load', 'scan', 'trigger', 'ensure-section', 'sync-row', 'sync-deployment'}
    assert '`rowAction`' in actions
    assert '`concept-body` and `decision-bullet` MUST NOT write files' in entry
    assert 'reuses a compliant supplied body' in entry
    assert 'mode' in entry


def test_concept_discovery_resources_move_without_changing_research_questioning():
    assert (ROOT / 'references/arc42-cross-cutting-concepts.md').is_file()
    assert (ROOT / 'references/questioning.md').read_bytes() == (
        ROOT.parent / 'define/references/questioning.md').read_bytes()
    concept = (ROOT / 'playbooks/define-concept.md').read_text()
    assert 'user-confirmed' in concept
    assert 'no second permission prompt' in concept
    assert 'concept-body' in concept and 'concept-record' in concept
