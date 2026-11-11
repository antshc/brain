import re
from pathlib import Path


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
DESIGN = SKILLS / "design"


def test_design_is_the_only_entry_point_for_its_routes():
    router = (DESIGN / "SKILL.md").read_text()
    assert router.split("---", 2)[1].startswith("\nname: design\n")
    assert "disable-model-invocation: true" not in router
    assert list(DESIGN.rglob("SKILL.md")) == [DESIGN / "SKILL.md"]
    for mode in ("architect", "sketch", "deep-module", "grill", "spec", "tickets", "wayfinder", "review"):
        assert f"](playbooks/{mode}.md)" in router
        assert not (DESIGN / f"playbooks/{mode}.md").read_text().startswith("---")
    for old_name in ("architect", "grill-design", "to-spec", "to-tickets", "wayfinder", "review-design"):
        assert not (SKILLS / old_name / "SKILL.md").exists()
    assert "Select `tickets`, `wayfinder`, or `review` only on an explicit user request" in router
    assert "ask which outcome" in router
    assert "continue the active route" in router


def test_one_shared_code_sketch_contract():
    router = (DESIGN / "SKILL.md").read_text()
    sketch = (DESIGN / "playbooks/sketch.md").read_text()
    architect = (DESIGN / "playbooks/architect.md").read_text()
    runner = (DESIGN / "references/runner-prompt.md").read_text()
    contract = DESIGN / "references/sketch-contract.md"

    assert "Sketch](playbooks/sketch.md)" in router
    assert contract.is_file()
    assert "../references/sketch-contract.md" in sketch
    assert "../references/sketch-contract.md" in architect
    assert "sketch-contract.md" in runner
    assert "**Candidate**" in sketch
    assert "**Standalone**" in sketch
    assert "synthesis/" in sketch
    assert "sketch/" in contract.read_text()
    assert not any(p.is_file() for p in (SKILLS / "architect").rglob("*"))


def test_spec_accepts_both_design_packages():
    spec = (DESIGN / "playbooks/spec.md").read_text()
    assert "`design architect` or `design sketch`" in spec
    assert "synthesis/" in spec
    assert "scripts/bundle_artifacts.py" in spec


def test_all_design_reference_links_resolve():
    for markdown in DESIGN.rglob("*.md"):
        for target in re.findall(r"\]\((\.\.?/[^)\s]+)\)", markdown.read_text()):
            relative, _, anchor = target.partition("#")
            path = (markdown.parent / relative).resolve()
            assert path.is_relative_to(DESIGN), (markdown, target)
            assert path.is_file(), (markdown, target)
            if anchor:
                headings = re.findall(r"^#{1,6} (.+)$", path.read_text(), re.MULTILINE)
                assert anchor in {heading.lower().replace(" ", "-") for heading in headings}


def test_playbook_links_resolve_to_bundled_references_and_sections():
    for playbook in (DESIGN / "playbooks").glob("*.md"):
        for target in re.findall(r"\]\((\.\.?/[^)\s]+)\)", playbook.read_text()):
            relative, _, anchor = target.partition("#")
            path = (playbook.parent / relative).resolve()
            assert path.is_relative_to(DESIGN), target
            assert path.is_file(), target
            if anchor:
                headings = re.findall(r"^#{1,6} (.+)$", path.read_text(), re.MULTILINE)
                assert anchor in {heading.lower().replace(" ", "-") for heading in headings}
    for mode, section in (
        ("spec", "spec-publication"),
        ("tickets", "ticket-operations"),
        ("wayfinder", "wayfinder-operations"),
    ):
        assert f"](../references/github.md#{section})" in (DESIGN / f"playbooks/{mode}.md").read_text()
