from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest
import yaml


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / 'plugins/wf/skills'
ROOT = SKILLS / 'research'
ENTRY = (ROOT / 'SKILL.md').read_text()
HOW = (ROOT / 'how/how.md').read_text()
INSPECTION = (ROOT / 'how/inspection.md').read_text()
REPORT = (ROOT / 'how/report.md').read_text()
PROMPT = (ROOT / 'how/explorer-prompt.md').read_text()
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
    table = INSPECTION.split('| Lookup | `@shape` | `@depth` | `@work` prefix |')[1].split('\n\n')[0]
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


def test_evidence_checklist_and_report_replace_explainer():
    for field in ('QUESTION', 'EXPLORATION_ANGLE', 'TARGETS_OR_REFS', 'DEPTH', 'LENS_AND_CHECKS'):
        assert f'{{{field}}}' in PROMPT
    assert not (ROOT / 'how/explainer-prompt.md').exists()
    assert '## Visualize' in REPORT
    assert 'Explainer' not in HOW + ENTRY + PROMPT
    assert not re.search(r'\{(?:OUTPUT_PATH|OUTPUT_ARTIFACT)\}', PROMPT)


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


def test_all_routes_execute_without_worker_dependencies():
    text = '\n'.join(path.read_text() for path in ROOT.rglob('*.md'))
    for stale in ('`subagents` skill', 'Spawn one synthesizer', 'Spawn Parallel Investigators',
                  'MUST** delegate source reading', 'send an Explore request directly to `hunter`',
                  'Explainer prompt', 'why investigators', 'why synthesizer'):
        assert stale not in text
    assert '**MUST NOT** spawn subagents' in ENTRY
    assert '## Read-only contract' in ENTRY


def test_explicit_routes_and_legacy_inputs_remain_available():
    route = next(line for line in ENTRY.splitlines() if line.startswith('- `@route`'))
    values = set(re.search(r'`(auto[^`]+)`', route).group(1).split(' | '))
    assert values == {'auto', 'explore', 'how', 'why', 'cloud', 'web', 'graphify'}
    assert 'Reject unknown routes, conflicting explicit route/mode/scope' in ENTRY
    for field in ('@question', '@work', '@target', '@shape', '@depth', '@whyDepth', '@researchScope'):
        assert field in ENTRY


def test_hunter_inherits_tools_and_preserves_final_report_write_boundary():
    hunter = (REPO / 'plugins/wf/agents/hunter.agent.md').read_text()
    metadata = yaml.safe_load(hunter.split('---', 2)[1])
    assert 'tools' not in metadata or metadata['tools'] == ['*']
    assert metadata['include-custom-instructions'] is True
    assert 'Read its full body' in hunter
    assert '@outputPath` alone never authorizes Hunter' in hunter
    assert 'caller to save' in ENTRY
    assert 'Only the brief\'s exact `@outputArtifact`' in ENTRY


def test_why_keeps_category_coverage_without_nested_roles():
    why = (ROOT / 'why/why.md').read_text()
    report = (ROOT / 'why/synthesizer-prompt.md').read_text()
    categories = ('Source control', 'Issue / ticket tracker', 'Long-form documents',
                  'Real-time team chat', 'Infrastructure observability',
                  'Error / exception tracking', 'Product analytics warehouse')
    for category in categories:
        assert category in why
        assert category in report
    assert '@whyDepth=anchor' in why
    assert 'stop before category investigation' in why
    assert 'null' in why
    assert 'Direct' in report and 'Inferred' in report and 'Speculative' in report


def test_direct_route_eval_cases_cover_selection_and_access_failures():
    data = json.loads((Path(__file__).parent / 'evals/how-scenarios.json').read_text())
    ids = {case['id'] for case in data['cases']}
    assert {'explicit_route', 'auto_route', 'invalid_route', 'conflicting_route',
            'why_anchor', 'why_full', 'hunter_save_boundary', 'missing_web_access',
            'single_checkout', 'cloud_sdk_direct', 'worktree_graph'} <= ids
    assert any('paired' in check.lower() for check in data['commonChecks'])
