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


def test_blast_radius_calls_only_its_existing_procedures_and_proves_directly():
    skill = (REPO / "plugins/review/skills/blast-radius/SKILL.md").read_text()
    assert re.findall(r"\*run `([a-z-]+)` skill\b", skill, flags=re.IGNORECASE) == [
        "research", "research", "subagents", "writing-style",
    ]
    for action in ("Why code anchor", "**How**", "**Arena**", "**Unslop only**"):
        assert action in skill
    assert "Write a script or test that runs the real code, run it" in skill
