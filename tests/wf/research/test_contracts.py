from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / 'plugins/wf/skills'
ROOT = SKILLS / 'research'
RESEARCH = (ROOT / 'system/system-inspection.md').read_text()
HOW = (ROOT / 'how/how.md').read_text()
PROMPT = (ROOT / 'how/explorer-prompt.md').read_text()
EXPLAINER = (ROOT / 'how/explainer-prompt.md').read_text()
EXPLORE = (SKILLS / 'research/SKILL.md').read_text().split('## Explore request')[1].split('\n## ')[0]


def lookup_rows() -> list[list[str]]:
    table = RESEARCH.split('| Lookup | `@shape` | `@depth` |')[1].split('\n\n')[0]
    return [[c.strip().strip('`') for c in l.strip('|').split('|')] for l in table.strip().splitlines()[1:]]


def explore_enum(field: str) -> set[str]:
    line = next(l for l in EXPLORE.splitlines() if re.match(rf'- `\[?{field}\]?`', l))
    return set(re.search(r'`([^`]+)`(?:;|\.|$)', line.split(' — ', 1)[1]).group(1).split(' | '))


def test_lookup_shapes_match_explore_enum():
    rows = lookup_rows()
    assert rows
    assert {row[1] for row in rows} <= explore_enum('@shape')


def test_lookup_depths_match_explore_enum():
    assert explore_enum('@depth') == {'quick', 'medium', 'thorough'}
    assert {row[2] for row in lookup_rows()} <= explore_enum('@depth')


def test_request_lists_required_fields():
    request = RESEARCH.split('Pass each Explore request:')[1].split('| Lookup |')[0]
    for field in ('@work', '@shape', '@depth', '@target', '@outputShape'):
        assert f'`{field}`' in request, field


def test_depth_is_independent_of_the_primary_lens():
    for request, depth in (
        ('Narrow system question', 'Concise'),
        ('Complex system question', 'Detailed'),
        ('Explicit inspection or verification', 'Full'),
    ):
        assert f'| {request} | {depth} |' in RESEARCH
    assert 'A supplied axis selects the primary lens' in RESEARCH
    assert 'belongs in the same answer' in RESEARCH


def test_saved_system_reports_use_one_template():
    assert HOW.index('## Answer') < HOW.index('## How it works')
    for path in ('<slug>.md', '<slug>-chain.md', '<slug>-data.md'):
        assert f'docs/research/{path}' in HOW
    assert '[How](how.md) as the report contract' in EXPLAINER
    assert not list((ROOT / 'system').glob('*-template.md'))


def test_system_evidence_is_inline_and_names_blocked_runtime_checks():
    assert 'Explicit inspection and requests for a document take precedence' in EXPLORE
    for field in ('QUESTION', 'EXPLORATION_ANGLE', 'TARGETS_OR_REFS', 'DEPTH', 'LENS_AND_CHECKS'):
        assert f'{{{field}}}' in PROMPT
    assert 'Return evidence inline' in PROMPT
    assert 'claim, blocker, and exact next check' in PROMPT


def test_explainer_receives_findings_and_selected_inspection_guidance():
    assert '{EXPLORER_FINDINGS}' in EXPLAINER
    assert '{INSPECTION_GUIDANCE}' in EXPLAINER
    assert 'applicable lens guidance to choose a diagram' in EXPLAINER
    assert 'Return one Markdown draft inline' in EXPLAINER
    assert 'Apply only the supplied proof checks' in PROMPT
