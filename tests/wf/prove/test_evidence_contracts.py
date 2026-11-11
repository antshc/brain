from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import pytest
import yaml


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / 'plugins/wf/skills'
TESTING = REPO / 'plugins/wf/install/assets/testing-integrations'


def bundled_links(path: Path) -> Iterator[Path]:
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        parts = urlsplit(target)
        if not parts.scheme and parts.path.endswith('.md'):
            yield (path.parent / unquote(parts.path)).resolve()


@pytest.mark.parametrize('name', ['prove', 'challenge-this'])
def test_standalone_skill_resources_are_discoverable_and_local(name: str) -> None:
    root = SKILLS / name
    entry = root / 'SKILL.md'
    front = yaml.safe_load(entry.read_text().split('---', 2)[1])
    assert front['name'] == name
    assert not front.get('disable-model-invocation', False)
    assert len(front['description']) <= 300
    assert len(entry.read_text().splitlines()) < 300
    assert set(root.rglob('*.md')) - {entry} <= set(bundled_links(entry))
    for resource in root.rglob('*.md'):
        for target in bundled_links(resource):
            assert target.is_file(), (resource, target)
            assert target.is_relative_to(root), (resource, target)


def test_removed_entry_points_and_testing_kind_have_no_live_consumers() -> None:
    obsolete = ['experiment/SKILL.md', 'playbooks/prove.md',
                'playbooks/interrogate.md', 'playbooks/challenge-this.md',
                'interrogate/SKILL.md', 'kinds/experiment.md']
    assert not (SKILLS / 'experiment').exists()
    assert not (SKILLS / 'interrogate').exists()
    assert not (TESTING / 'kinds/experiment.md').exists()
    for path in list(SKILLS.rglob('*.md')) + list(TESTING.rglob('*.md')):
        content = path.read_text()
        assert not re.search(r'`experiment`\s+skill', content), path
        assert not any(target in content for target in obsolete), path


def test_execution_calls_are_one_way() -> None:
    integration = (SKILLS / 'prove/tactics/integration.md').read_text()
    adversary = (SKILLS / 'challenge-this/references/adversary-prompt.md').read_text()
    assert re.search(r'`testing-integrations` skill.*\*\*Select\*\*', integration)
    assert re.search(r'`testing-integrations` skill.*\*\*Run selected\*\*', integration)
    assert re.search(r'`prove` skill.*\*\*Execute\*\*', adversary)
    for resource in TESTING.rglob('*.md'):
        assert not re.search(r'\b(?:run|invoke|load|use)\s+`prove`\s+skill', resource.read_text(), re.I), resource
    assert not re.search(r'\b(?:run|invoke|load|use)\s+`challenge-this`\s+skill', (SKILLS / 'prove/SKILL.md').read_text(), re.I)


def test_testing_selection_and_execution_are_distinct_public_actions() -> None:
    entry = (TESTING / 'SKILL.md').read_text()
    headings = re.findall(r'^## (.+)$', entry, re.M)
    assert {'Select', 'Run selected', 'Cloud Safety', 'Report'} <= set(headings)
    routes = set(re.findall(r'^\| ([a-z-]+) \|', entry, re.M))
    assert {'component', 'functional-slice', 'local-runtime'} <= routes
    assert 'experiment' not in routes
