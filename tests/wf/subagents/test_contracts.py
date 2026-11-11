from __future__ import annotations

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


def test_swarm_preserves_caller_payloads_and_accounts_for_required_slices():
    swarm = (SKILLS / "subagents/swarm.md").read_text()
    for contract in (
        "share the complete input", "responsibility or evaluation dimension",
        "caller output contracts", "without dropping required slices",
        "original reports and corrections", "missing results as gaps",
        "actual model only when observable", "separate from caller-defined worker payloads",
    ):
        assert contract in swarm
    # Generic defaults and measurement/race contracts survive custom payloads.
    for default in (
        "`PASS`, `ISSUES` or `BLOCKED`", "retry malformed or incomplete reports once",
        "**first pass**", "**rank all**", "**best-of**",
        "method, sample count, unit and order", "each writer an isolated output",
        "A gap cannot count as a pass",
    ):
        assert default in swarm
    assert not re.search(r"\b(PR|initiative|bugs|quality-attributes|code-smells|REVIEW_COMMENT)\b", swarm)


def test_code_review_delegates_axes_without_owning_model_policy():
    root = SKILLS / "review"
    code = (root / "playbooks/code.md").read_text()
    assert re.findall(r"\*run `(subagents)` skill\b", code, flags=re.IGNORECASE) == ["subagents"]
    for contract in (
        "**Swarm**", "partition shape", "`swarm workers`",
        "fresh general-purpose skill-capable read-only worker",
        "complete change for its axis", "JSON unchanged",
        "initiative-description gate passed", "never as empty success",
        "substitute parent review when delegation is unavailable",
    ):
        assert contract in code
    assert re.findall(r"^   \| `([^`]+)` \|", code, flags=re.MULTILINE) == [
        "bugs", "quality-attributes", "code-smells", "initiative",
    ]
    assert "## Model selection" not in code
    assert not re.search(r"\b(claude-|gpt-|grok-|gemini-|random)", code)
    assert "reviewer-selection.md" not in code
    assert not (root / "references/reviewer-selection.md").exists()
    models = (SKILLS / "subagents/models.md").read_text()
    assert re.search(r"^\| swarm workers \|", models, flags=re.MULTILINE)


def test_review_accepts_pr_url_without_level_options():
    router = (SKILLS / "review/SKILL.md").read_text()
    code_row = next(line for line in router.splitlines() if line.startswith("| `code` |"))
    assert "level" not in code_row
    assert "ask which outcome" in router
    code = (SKILLS / "review/playbooks/code.md").read_text()
    assert not re.search(r"`(?:low|medium|high)`|\blegacy\b|\bretired\b", router + code)


def test_research_preserves_why_and_routes_system_evidence_to_hunter():
    skill = (SKILLS / "research/SKILL.md").read_text()
    for reference in ("how/how.md", "how/explorer-prompt.md", "how/explainer-prompt.md",
                      "why/why.md", "why/sources/atlassian.md"):
        assert f"]({reference})" in skill
        assert (SKILLS / "research" / reference).is_file()
    assert "`@whyDepth`" in skill
    assert "Why code anchor" in skill
    assert "## Routing" in skill
    how = (SKILLS / "research/how/how.md").read_text()
    assert "system/system-inspection.md" not in skill
    assert "Hunter" in how and "Explainer" in how
    assert "@outputPath" in skill and "@outputBase" in skill
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
        "research", "research", "testing-integrations", "subagents", "subagents", "writing-style",
    ]
    for action in ("Why code anchor", "**default Research**", "**Dispatch**", "**Arena**", "**Unslop only**"):
        assert action in impact
    assert "Prove every claim" in impact
    for name in ("blast-radius-worker-prompt.md", "blast-radius-report.md"):
        assert f"../references/{name}" in impact
        assert (root.parent / "references" / name).is_file()
    assert "MUST NOT" in assessment and "edit production code or tests" in assessment
    assert "Seam / assertion quality" in assessment
    assert "Every gap names input/setup, expected observable result, test level, and priority" in assessment


def test_pr_review_routes_share_diff_acquisition_and_preserve_posting_contracts():
    root = SKILLS / "review"
    for route in ("code", "hitl"):
        playbook = (root / f"playbooks/{route}.md").read_text()
        assert "*Follow `github` skill for pull requests and review evidence*" in playbook
        assert f"using Pull requests, Diff, {route.upper() if route == 'hitl' else route.title()} setup" in playbook
        assert "../../github/" not in playbook
        assert f"](../references/posting.md#{route})" in playbook

    github = SKILLS / "github"
    assert "](tactics/pull-requests.md)" in (github / "SKILL.md").read_text()
    assert "](../references/fetch-diff.md)" in (github / "tactics/pull-requests.md").read_text()
    diff = (github / "references/fetch-diff.md").read_text()
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
