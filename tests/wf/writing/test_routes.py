from pathlib import Path


SKILLS = Path(__file__).resolve().parents[3] / 'plugins/wf/skills'
ROOT = SKILLS / 'writing'
ROUTES = ('guide', 'how-to', 'github', 'report', 'message', 'unslop', 'sharpen', 'rephrase')


def test_every_route_is_in_the_routing_table_and_its_references_exist():
    entry = (ROOT / 'SKILL.md').read_text()
    for route in ROUTES:
        assert f'| `{route}` |' in entry
    for link in ('references/github-text.md', 'references/messages.md',
                 'references/sharpen.md', 'references/rephrase.md'):
        assert f']({link})' in entry
        assert (ROOT / link).is_file()
    assert not (ROOT / 'references/docs-and-prs.md').exists()
    assert not (SKILLS / 'writing-style').exists()


def test_sharpen_and_rephrase_are_separate_routes():
    sharpen = (ROOT / 'references/sharpen.md').read_text()
    rephrase = (ROOT / 'references/rephrase.md').read_text()
    assert 'Make the task deeper, not bigger.' in sharpen
    assert 'prototype any choice an experiment can settle' in sharpen
    assert '| **Restate** |' not in sharpen
    assert 'Restate in your own words' in rephrase
    assert not (SKILLS / 'sharpen').exists()


def test_callers_let_writing_select_the_route():
    callers = (
        'git/references/commit-messages.md', 'github/tactics/pull-requests.md',
        'github/tactics/reviews.md', 'review/playbooks/blast-radius.md',
        'write-work/SKILL.md', 'write-document/SKILL.md',
    )
    for caller in callers:
        text = (SKILLS / caller).read_text()
        assert '`writing` skill' in text and 'select the applicable route' in text
        assert '**Unslop only**' not in text
        assert '**Write a PR description or commit message**' not in text
