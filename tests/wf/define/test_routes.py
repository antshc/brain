import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / 'plugins/wf/skills'
DEFINE = SKILLS / 'define'


def test_define_retains_research_and_hands_off_concepts():
    entry = (DEFINE / 'SKILL.md').read_text()
    research = (DEFINE / 'references/research.md').read_text()

    assert 'name: define\n' in entry
    assert '[Research](references/research.md)' in entry
    assert '[Questioning](references/questioning.md)' in entry
    assert 'docs/ongoing/{{destinationSlug}}-research-map.md' in research
    assert '[questioning.md](questioning.md)' in research
    assert 'route `define-concept`' in entry
    assert '`architecture-records` skill' in entry
    assert not (DEFINE / 'references/concept.md').exists()
    assert not (DEFINE / 'references/arc42-cross-cutting-concepts.md').exists()
    assert not (SKILLS / 'define-concept/SKILL.md').exists()


def test_sharpen_is_a_writing_style_route():
    reference = (SKILLS / 'writing-style/references/sharpen.md').read_text()
    writing_style = (SKILLS / 'writing-style/SKILL.md').read_text()

    assert '| **Deepen** |' in reference
    assert '| **Restate** |' in reference
    assert 'Make the task deeper, not bigger.' in reference
    assert '[references/sharpen.md](references/sharpen.md)' in writing_style
    assert not (SKILLS / 'sharpen').exists()


def test_define_local_markdown_links_resolve():
    for document in [DEFINE / 'SKILL.md', *(DEFINE / 'references').glob('*.md')]:
        for target in re.findall(r'\]\(([^)#]+\.md)\)', document.read_text()):
            assert (document.parent / target).is_file(), (document, target)
