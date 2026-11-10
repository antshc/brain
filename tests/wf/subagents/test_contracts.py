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


def test_research_preserves_why_and_routes_system_evidence_to_hunter():
    skill = (SKILLS / "research/SKILL.md").read_text()
    for reference in ("how/how.md", "how/explorer-prompt.md", "why/why.md", "why/sources/atlassian.md"):
        assert f"]({reference})" in skill
        assert (SKILLS / "research" / reference).is_file()
    assert "`@whyDepth`" in skill
    assert "Why code anchor" in skill
    assert skill.index("## Entry routes") < skill.index("## Workflow")
    system = skill.split("## System research")[1].split("\n## ")[0]
    assert "as `@work` directly to Hunter" in system
    assert "save one cited Markdown document using How" in system
    dispatch = (SKILLS / "subagents/SKILL.md").read_text()
    assert "Send Explore requests verbatim to `hunter`" in dispatch
    assert "report the blocked evidence request and continue independent work" in dispatch


def test_review_loads_playbooks_by_route():
    root = SKILLS / "review"
    skill = (root / "SKILL.md").read_text()
    playbooks = ("architecture", "blast-radius", "comments", "code", "hitl", "tests-gap")

    assert "name: review\n" in skill
    assert "Read only the selected playbook" in skill
    assert "ask which outcome" in skill
    for route in playbooks:
        assert f"| `{route}` |" in skill
        assert f"](playbooks/{route}.md)" in skill
        assert (root / f"playbooks/{route}.md").is_file()
    for retired in (
        "address-pr", "blast-radius", "review-architecture", "review-feat",
        "review-fix", "review-hitl", "test-gaps",
    ):
        assert not (SKILLS / retired / "SKILL.md").exists()


def test_review_impact_and_tests_keep_their_analysis_contracts():
    root = SKILLS / "review/playbooks"
    impact = (root / "blast-radius.md").read_text()
    assessment = (root / "tests-gap.md").read_text()
    assert re.findall(r"\*run `([a-z-]+)` skill\b", impact, flags=re.IGNORECASE) == [
        "research", "research", "subagents", "writing-style",
    ]
    for action in ("Why code anchor", "**default Research**", "**Arena**", "**Unslop only**"):
        assert action in impact
    assert "Write a script or test that runs the real code, run it" in impact
    assert "MUST NOT" in assessment and "edit production code or tests" in assessment
    assert "Seam / assertion quality" in assessment
    assert "Every gap names input/setup, expected observable result, test level, and priority" in assessment


def test_pr_review_routes_share_diff_acquisition_and_preserve_posting_contracts():
    root = SKILLS / "review"
    for route in ("code", "hitl"):
        playbook = (root / f"playbooks/{route}.md").read_text()
        assert f"](../../github/references/fetch-diff.md#{route})" in playbook
        assert f"](../references/posting.md#{route})" in playbook

    diff = (SKILLS / "github/references/fetch-diff.md").read_text()
    assert diff.count("## Build the per-file diff") == 1
    assert "fresh detached review worktree" in diff
    assert "GH_TOOL pr checkout" in diff
    assert "_manifest.tsv" in diff
    hitl = (root / "playbooks/hitl.md").read_text()
    assert hitl.index("**3. Human approval**") < hitl.index("On approval (1 or 2): follow [Posting]")
    posting = (root / "references/posting.md").read_text()
    assert "Require explicit human approval" in posting
    assert "current PR head and base" in posting
    comments = (root / "playbooks/comments.md").read_text()
    assert 'GH_TOOL review discussion' in comments
    assert (SKILLS / "github/tactics/reviews.md").is_file()
    assert all(path.is_file() for path in (root / "references").iterdir())
