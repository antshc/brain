from pathlib import Path


REPO = Path(__file__).resolve().parents[3]


def test_suggest_is_bundled_with_wf():
    skill = REPO / 'plugins/wf/skills/suggest/SKILL.md'
    body = skill.read_text()
    assert 'name: suggest\n' in body
    assert 'disable-model-invocation: true' in body
    assert 'MUST NOT apply any suggestions' in body
    assert not (REPO / 'skills/productivity/suggest/SKILL.md').exists()


def test_install_and_skill_catalog_point_to_wf():
    readme = (REPO / 'README.md').read_text()
    wf_readme = (REPO / 'plugins/wf/README.md').read_text()
    assert '[suggest](plugins/wf/skills/suggest/SKILL.md)' in readme
    assert '`suggest`' in wf_readme
    assert 'engineering/suggest --agent' not in readme
