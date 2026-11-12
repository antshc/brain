import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / 'plugins/wf/skills'
DEFINE = SKILLS / 'define'


def test_define_routes_have_one_shared_questioning_contract():
    entry = (DEFINE / 'SKILL.md').read_text()
    research = (DEFINE / 'references/research.md').read_text()
    concept = (DEFINE / 'references/concept.md').read_text()

    assert 'name: define\n' in entry
    assert '[Research](references/research.md)' in entry
    assert '[Concept](references/concept.md)' in entry
    assert '[Questioning](references/questioning.md)' in entry
    assert 'docs/ongoing/{{destinationSlug}}-research-map.md' in research
    assert 'doc-architecture' in concept
    assert '[questioning.md](questioning.md)' in research
    assert '[questioning.md](questioning.md)' in concept
    assert '[arc42-cross-cutting-concepts.md](arc42-cross-cutting-concepts.md)' in concept
    assert (DEFINE / 'references/questioning.md').is_file()
    assert (DEFINE / 'references/arc42-cross-cutting-concepts.md').is_file()
    assert not (SKILLS / 'define-research/SKILL.md').exists()
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
