# AI Diff Bug-Review Agent: Instructions & Best Practices (October 2026)

**Goal:** Build a read-only agent that detects concrete bugs and regressions **introduced by a code diff**, not a general style reviewer.

**Status:** Practice guide and copyable example, not a formal industry standard. Based on the source guidance linked below; prioritize applicable repository rules over these defaults.

## Core principles

1. **Defect-first.** Report problems the author would likely fix, not style preferences or generic improvement ideas.
2. **Diff-first, context-aware.** Inspect the entire selected change, then read callers, contracts, tests, configuration, and affected paths needed to establish behavior.
3. **Introduced-by-change gate.** Do not attribute pre-existing defects to the patch.
4. **Evidence before findings.** Require a concrete scenario, affected execution path, and causal explanation.
5. **High precision, complete coverage.** Reject speculation, but continue scanning after finding the first bug.
6. **Read-only review.** Inspect and report; do not edit, commit, push, or post comments unless explicitly authorized.
7. **Actionable output.** One issue per finding, precise changed-line location, impact, severity, and triggering conditions.

OpenAI's [Codex review rubric](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/review/rubric.md) and [sample review agent](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/review-agent/SKILL.md) are the most directly reusable references for the defect-reporting gate. GitHub and OWASP provide complementary instruction and security-review guidance.

## Instruction wording

| Intent | Prefer | Avoid |
| --- | --- | --- |
| Objective | Find concrete defects introduced by the reviewed diff. | Review this code carefully. |
| Scope | Inspect the complete requested diff and relevant surrounding behavior. | Check everything. |
| Regression | MUST verify that the change introduces each reported issue. | Find possible issues. |
| Proof | For each candidate, identify the triggering input or affected execution path. | Be accurate. |
| Signal | MUST NOT report speculative problems, pre-existing defects, or style nits. | Give comprehensive feedback. |
| Completeness | Continue inspecting the diff after the first finding. | Find the most important bug. |
| Reporting | State the trigger, incorrect result, impact, and narrow changed-line range. | Explain what's wrong. |
| No bugs | Return "No findings." after completing the review if nothing qualifies. | Always suggest improvements. |
| Failure | If the target cannot be inspected, report "Review incomplete" and the missing evidence. | Guess what changed. |

Use **MUST / MUST NOT** for true invariants; imperative sentences for steps; **SHOULD** for defaults. Add a short rationale to non-obvious constraints, especially where an agent might silently substitute a different procedure.

### Constraint → mechanism → rationale → failure behavior

> MUST verify every reported regression against an affected code path. MUST NOT infer that a changed signature breaks callers without checking those callers. Rationale: conjecture generates low-value review comments. If required files or evidence are unavailable, identify the unverified candidate separately; do not present it as a verified bug.

## Review workflow

1. **Resolve target.** Distinguish PR, commit, base branch, staged/unstaged worktree, or explicit diff. Use the merge-base for a branch change that would merge into a target branch; do not compare unrelated tips.
2. **Read instructions.** Read applicable repository-scoped review and coding instructions; apply narrower guidance to affected files.
3. **Inventory the change.** Read every changed hunk and identify behavior, interface, dependency, test, config, and migration surfaces.
4. **Trace affected paths.** Follow relevant callers/callees, state transitions, error paths, and external interfaces. Read beyond the diff where necessary.
5. **Generate candidates.** Check correctness, null/edge cases, errors, concurrency, security, compatibility, performance, resource lifetimes, and config/deployment impact.
6. **Verify candidates.** For each, establish: introduced by change; concrete trigger; demonstrated wrong behavior; likely worth fixing. Inspect relevant tests; run narrowly scoped checks only if authorized and safe.
7. **Deduplicate and rank.** Keep distinct root causes, one finding per actionable issue, highest impact first.
8. **Report.** Point at minimal relevant changed lines. Give an explicit incomplete-review outcome if scope or evidence was inaccessible.

Risk-sensitive reviews should pay extra attention to authentication, authorization, user input, secrets, deserialization, persistence, trust boundaries, dependencies, and CI/IaC configuration. These are applications of [OWASP Secure Code Review](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html), not a substitute for a dedicated security audit.

## Example: GitHub Copilot custom reviewer

Store as a custom agent profile at **.github/agents/bug-reviewer.agent.md**. This example is documentation only; it is **not installed** by this knowledge-base article.

~~~markdown
---
name: Bug Reviewer
description: Review code diffs for introduced bugs and regressions; report only actionable, evidence-backed findings.
tools: [read, search, execute]
---

# Objective

Find concrete defects introduced by the requested diff.
Optimize for high-confidence, actionable bug findings—not style feedback.

# Scope

- MUST establish the exact review target before inspecting it.
- MUST inspect the complete requested diff and relevant surrounding code.
- For branch reviews, compare against the merge-base with the target branch.
- For working-tree reviews, identify staged, unstaged, and untracked changes
  within the requested scope. Do not silently ignore any of these categories.
- MUST read applicable repository instructions and relevant call sites/tests.
- MUST continue reviewing after identifying the first candidate.

# Inspection

Check changed behavior for:
- Logic errors, broken invariants, invalid state transitions.
- Null/empty/boundary cases, errors, retries, and cancellation.
- Interface or compatibility regressions and affected callers.
- Races, resource lifetime, disposal, and transaction boundaries.
- Authentication, authorization, input validation, and data exposure.
- Material performance, reliability, and deployment regressions.

# Evidence gate

MUST report a finding only if:
1. The reviewed change introduced the defect.
2. A specific input, environment, or execution path triggers it.
3. The incorrect behavior and impact are supported by code evidence.
4. The author would likely fix it.

MUST NOT report:
- Speculative failures or assumed requirements.
- Pre-existing issues unrelated to the change.
- Intentional changes without demonstrable defects.
- Style/naming/formatting suggestions or duplicate root causes.
- Missing tests alone as proof of a bug.

Rationale: review quality depends on evidence, not finding count.
When evidence is missing, keep the candidate out of verified findings.

# Verification

- Trace relevant callers, contracts, and error paths before reporting.
- Inspect relevant tests and use focused, safe checks when authorized.
- Do not claim a test was run unless it actually ran.
- Do not infer that an unobserved path is broken merely because it changed.

# Findings

Order findings from highest to lowest priority:
- P0: Universal critical failure or release blocker.
- P1: Urgent, material defect.
- P2: Ordinary actionable defect.
- P3: Lower-impact defect still worth fixing.

For each finding:
- Use an imperative title prefixed [P0] through [P3].
- Identify file path and the smallest changed-line range.
- In one short paragraph, state the trigger, wrong behavior, and impact.
- Cite the code evidence; avoid excessive explanation.

If review is complete and nothing qualifies, return "No findings."
If target/evidence is unavailable, return "Review incomplete: ..." and
state what was not checked. Never imply full coverage when incomplete.
After findings, briefly state material unverified risks if any.

# Restrictions

- MUST NOT edit files, fix code, create commits, push, or post PR comments.
- MUST NOT execute commands that modify source, repository state,
  external services, or production data.
- MUST NOT invent findings to appear thorough.
~~~

**Tool-safety note:** The GitHub custom-agent tool aliases **read**, **search**, and **execute** are documented, but access to **execute** is not technically read-only. Use runtime sandbox permissions or remove **execute** if commands cannot be trusted. Running tests/builds can write generated files and caches even without source edits. See [GitHub custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration).

## Example findings

**Qualifying finding:**

> [P1] Preserve cancellation when retrying requests — src/client.py:84  
> When the caller cancels during backoff, this new broad exception handler retries rather than propagating cancellation, so a canceled operation can continue submitting requests.

**Rejected candidate:**

> The method now takes an optional argument; this might break some callers.

The latter lacks a verified affected caller and a demonstrated failure. Only promote it if tracing shows an actual break.

## Evaluation

Test the agent on historical patches with independently known bugs **and** clean patches.

| Metric | What to measure |
| --- | --- |
| Precision | Verified real findings / all reported findings |
| Recall | Known introduced bugs found / known introduced bugs |
| Actionability | Findings maintainers agree warrant changes |
| Noise | Style, speculative, duplicate, or pre-existing reports |
| Coverage | Diff surfaces actually inspected; missing context disclosed |
| Location quality | Finding points at the smallest relevant changed lines |

Use cases: one clean diff, one obvious regression, a bug in a caller outside the diff, an intentional breaking change, a pre-existing bug, a security-sensitive change, and a diff with unavailable context. **Optimize precision first**, then expand recall without increasing noise.

## Architecture choices

- **Small default prompt:** Keep the general reviewer focused on the defect/evidence/output contract.
- **Specialized references:** Load .NET, Python, SQL, cloud, or security checklists when applicable—not for every review.
- **Optional second-pass verification:** For high-risk or large changes, have another reviewer verify candidate findings independently and deduplicate before publishing. This is consistent with [Claude Code Review's multi-agent approach](https://support.claude.com/en/articles/14233555-set-up-code-review-for-claude-code); it is not a requirement for small diffs.
- **Human accountability:** AI review supplements tests, static analysis, and human review, especially for security-sensitive changes.

## Sources (checked October 2026)

- **[OpenAI — Codex review rubric](https://github.com/openai/codex/blob/main/codex-rs/prompts/templates/review/rubric.md).** Introduced-by-change, actionable evidence, severity, concise changed-line comments, no speculative findings.
- **[OpenAI — Review Agent sample](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/review-agent/SKILL.md).** Read-only diff review, merge-base selection, affected callers/tests, finding format.
- **[GitHub — Customizing Copilot code review](https://docs.github.com/en/copilot/tutorials/customize-code-review).** Short, explicit, review-focused instructions and iterative tuning.
- **[GitHub — Copilot custom-agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration).** Agent profile frontmatter and tool aliases.
- **[GitHub — Code review workflows](https://docs.github.com/en/copilot/tutorials/use-copilot-code-review-across-the-pull-request-lifecycle).** Reviews across PR lifecycle, follow-up reviews and focused skills.
- **[Anthropic — Set up Code Review for Claude Code](https://support.claude.com/en/articles/14233555-set-up-code-review-for-claude-code)** (September 2, 2026). Specialized parallel reviewers inspect diffs and surrounding code.
- **[OWASP — Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html).** Diff-based review, trust boundaries, data flow, authentication/authorization, security regressions.
- **[Brain — 20 Instruction Patterns](./instruction-patterns-october-2026.md).** Local pattern terminology for constraint, mechanism, rationale, verification and failure handling.
