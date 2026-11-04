from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / 'plugins/wf/skills'
RESEARCH = (SKILLS / 'research/system/system-inspection.md').read_text()
EXPLORE = (SKILLS / 'explore-codebase/SKILL.md').read_text()


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
    request = RESEARCH.split('Pass each this Request:')[1].split('| Lookup |')[0]
    for field in ('@work', '@shape', '@depth', '@target', '@outputShape'):
        assert f'`{field}`' in request, field
