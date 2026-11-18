from pathlib import Path
import re


SKILLS = Path(__file__).resolve().parents[3] / 'plugins/wf/skills'
ROOT = SKILLS / 'write'
PROSE_ROUTES = ('guide', 'steps', 'github', 'findings', 'message', 'unslop', 'sharpen', 'rephrase')
ARTIFACT_ROUTES = ('story', 'task', 'bug', 'spec', 'hld', 'toi', 'research', 'bottom-line', 'root-cause', 'doc')


def test_every_route_is_in_the_routing_table_and_its_references_exist():
    entry = (ROOT / 'SKILL.md').read_text()
    for route in PROSE_ROUTES + ARTIFACT_ROUTES:
        assert f'| `{route}` |' in entry
    for retired in ('how-to', 'report', 'documentation'):
        assert f'| `{retired}` |' not in entry
    for link in ('references/github-text.md', 'references/messages.md',
                 'references/sharpen.md', 'references/rephrase.md', 'references/artifacts.md'):
        assert f']({link})' in entry
        assert (ROOT / link).is_file()
    assert not (ROOT / 'references/docs-and-prs.md').exists()
    assert not (SKILLS / 'writing-style').exists()


def test_one_writing_skill_owns_every_route():
    for retired in ('write-work', 'write-document', 'draft-artifact'):
        assert not (SKILLS / retired).exists()
    front = (ROOT / 'SKILL.md').read_text().split('---', 2)[1]
    assert 'Not for code or tests' in ' '.join(front.split())


def test_resources_are_local_and_directly_disclosed():
    entry = (ROOT / 'SKILL.md').read_text()
    linked = {target.split('#', 1)[0] for target in re.findall(r'\]\(([^)]+)\)', entry)}
    resources = {path.relative_to(ROOT).as_posix() for folder in ('playbooks', 'references', 'templates')
                 for path in (ROOT / folder).glob('*.md')}
    assert resources <= linked
    for target in linked:
        assert (ROOT / target).resolve().is_relative_to(ROOT.resolve())
        assert (ROOT / target).is_file()
    assert {path.stem for path in (ROOT / 'playbooks').glob('*.md')} == set(ARTIFACT_ROUTES)


def test_sharpen_and_rephrase_are_separate_routes():
    sharpen = (ROOT / 'references/sharpen.md').read_text()
    rephrase = (ROOT / 'references/rephrase.md').read_text()
    assert 'Make the task deeper, not bigger.' in sharpen
    assert 'prototype any choice an experiment can settle' in sharpen
    assert '| **Restate** |' not in sharpen
    assert 'Restate in your own words' in rephrase
    assert not (SKILLS / 'sharpen').exists()


def test_artifact_routes_refine_prose_without_reloading_the_skill():
    entry = (ROOT / 'SKILL.md').read_text()
    doc = (ROOT / 'playbooks/doc.md').read_text()
    assert 'MUST NOT** reload this skill' in entry
    assert 'An artifact route stays active while it applies a prose route internally' in entry
    assert '`write` skill' not in doc
    for route in ('`guide`', '`steps`'):
        assert route in doc
    assert "router's Internal hand-offs" in doc


def test_callers_let_write_select_the_route():
    callers = (
        'git/references/commit-messages.md', 'github/tactics/pull-requests.md',
        'github/tactics/reviews.md', 'review/playbooks/blast-radius.md',
    )
    for caller in callers:
        text = (SKILLS / caller).read_text()
        assert '`write` skill' in text and 'select the applicable route' in text
        assert '**Unslop only**' not in text
        assert '**Write a PR description or commit message**' not in text
