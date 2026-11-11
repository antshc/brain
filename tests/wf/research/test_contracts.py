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
EXPLAINER = (ROOT / 'how/explainer-prompt.md').read_text()
EXPLORE = ENTRY.split('## Explore request')[1].split('\n## ')[0]


def local_markdown_links(path: Path) -> set[Path]:
    links = set()
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        parts = urlsplit(link)
        if not parts.scheme and parts.path.endswith('.md'):
            links.add((path.parent / unquote(parts.path)).resolve())
    return links


def explore_enum(field: str) -> set[str]:
    line = next(line for line in EXPLORE.splitlines() if re.match(rf'- `\[?{field}\]?`', line))
    return set(re.search(r'`([^`]+)`(?:;|\.|$)', line.split(' — ', 1)[1]).group(1).split(' | '))


def test_inspection_lookup_hints_remain_compatible_with_hunter():
    table = INSPECTION.split('| Lookup | `@shape` | `@depth` |')[1].split('\n\n')[0]
    rows = [[cell.strip().strip('`') for cell in line.strip('|').split('|')]
            for line in table.strip().splitlines()[1:]]
    assert rows
    assert {row[1] for row in rows} <= explore_enum('@shape')
    assert {row[2] for row in rows} <= explore_enum('@depth')
    assert explore_enum('@depth') == {'quick', 'medium', 'thorough'}


def test_report_is_separate_from_the_how_procedure():
    assert REPORT.index('## Answer') < REPORT.index('## How it works')
    assert '## Workflow' in HOW
    assert 'how/how.md' in ENTRY and 'how/report.md' in ENTRY
    assert not (ROOT / 'system').exists()
    assert not (ROOT / 'explore').exists()


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
        content = path.read_text()
        for obsolete in ('docs/research/', '<slug>-chain.md', '<slug>-data.md', '<slug>-<provider>.md'):
            assert obsolete not in content, f'{path.relative_to(ROOT)}: {obsolete}'
    for field in ('@outputPath', '@outputBase', '@outputShape'):
        assert f'`{field}`' in ENTRY


@pytest.mark.parametrize('relative_path', [
    'design/playbooks/architect.md',
    'design/playbooks/wayfinder.md',
    'design/references/evidence-routing.md',
    'define/references/research.md',
    'prove/SKILL.md',
    'review/playbooks/blast-radius.md',
    'review/playbooks/hitl.md',
])
def test_saved_report_callers_supply_explicit_destinations(relative_path: str):
    caller = (SKILLS / relative_path).read_text()
    assert '@outputPath' in caller
    assert '@outputBase' in caller


def test_explorer_and_explainer_accept_evidence_without_path_policy():
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
    assert {'focused_inline', 'discover_ownership', 'cross_repo_handoff', 'nuget_implementation',
            'terminal_and_access_gap', 'provider_runtime_unknown', 'data_engine_specific',
            'architect_wayfinder_destinations', 'missing_save_destination',
            'conflicting_destinations', 'multiple_reports', 'why_cloud_web_inline'} <= set(ids)
    assert all(case['request'] and case['checks'] for case in cases)
