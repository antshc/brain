import re
from pathlib import Path


SKILLS = Path(__file__).resolve().parents[3] / "plugins/wf/skills"
DESIGN = SKILLS / "design"


def test_design_is_the_only_entry_point_for_its_routes():
    router = (DESIGN / "SKILL.md").read_text()
    assert router.split("---", 2)[1].startswith("\nname: design\n")
    assert "disable-model-invocation: true" not in router
    assert list(DESIGN.rglob("SKILL.md")) == [DESIGN / "SKILL.md"]
    for mode in ("grill", "spec", "tickets", "wayfinder", "review"):
        assert f"](playbooks/{mode}.md)" in router
        assert not (DESIGN / f"playbooks/{mode}.md").read_text().startswith("---")
    for old_name in ("grill-design", "to-spec", "to-tickets", "wayfinder", "review-design"):
        assert not (SKILLS / old_name / "SKILL.md").exists()
    assert "Select `tickets`, `wayfinder`, or `review` only on an explicit user request" in router
    assert "ask which outcome" in router
    assert "continue the active route" in router


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
