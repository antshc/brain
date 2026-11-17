from pathlib import Path


SKILLS = Path(__file__).resolve().parents[3] / 'plugins/wf/skills'


def test_sharpen_is_a_writing_style_route():
    reference = (SKILLS / 'writing-style/references/sharpen.md').read_text()
    writing_style = (SKILLS / 'writing-style/SKILL.md').read_text()

    assert '| **Deepen** |' in reference
    assert '| **Restate** |' in reference
    assert 'Make the task deeper, not bigger.' in reference
    assert '[references/sharpen.md](references/sharpen.md)' in writing_style
    assert not (SKILLS / 'sharpen').exists()
