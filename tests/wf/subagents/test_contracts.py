import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
SKILLS = REPO / "plugins/wf/skills"


def test_subagents_owns_arena_swarm_and_model_roles():
    skill = (SKILLS / "subagents/SKILL.md").read_text()
    for reference in ("arena.md", "swarm.md", "models.md"):
        assert f"]({reference})" in skill
        assert (SKILLS / "subagents" / reference).is_file()
    for old_path in ("models.md", "arena/subagents.md", "arena/arena.md", "how", "why"):
        assert not (SKILLS / "architect" / old_path).exists()


def test_research_routes_how_and_why_before_standard_inspection():
    skill = (SKILLS / "research/SKILL.md").read_text()
    for reference in ("how/how.md", "why/why.md", "why/sources/atlassian.md"):
        assert f"]({reference})" in skill
        assert (SKILLS / "research" / reference).is_file()
    assert "`@whyDepth`" in skill
    assert skill.index("## Entry routes") < skill.index("## Workflow")


def test_review_fix_routes_to_progressively_disclosed_procedures():
    root = REPO / "plugins/wf/skills/review-fix"
    skill = (root / "SKILL.md").read_text()
    impact = (root / "references/impact-analysis.md").read_text()
    assessment = (root / "references/test-assessment.md").read_text()

    assert "name: review-fix" in skill
    assert "Read each selected reference completely" in skill
    for reference in ("impact-analysis.md", "test-assessment.md"):
        assert f"](references/{reference})" in skill
    for retired in ("blast-radius", "test-gaps"):
        assert not (REPO / "plugins/wf/skills" / retired / "SKILL.md").exists()

    assert re.findall(r"\*run `([a-z-]+)` skill\b", impact, flags=re.IGNORECASE) == [
        "research", "research", "subagents", "writing-style",
    ]
    for action in ("Why code anchor", "**How**", "**Arena**", "**Unslop only**"):
        assert action in impact
    assert "Write a script or test that runs the real code, run it" in impact
    assert "MUST NOT" in assessment and "edit production code or tests" in assessment
    assert "Seam / assertion quality" in assessment
    assert "Every gap names input/setup, expected observable result, test level, and priority" in assessment
