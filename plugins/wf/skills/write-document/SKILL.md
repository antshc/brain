---
name: write-document
description: >-
  Write and update specs, HLDs, TOI documents, research reports, root-cause reports and bottom lines. Use for 'write a spec', 'write a research report' or 'write the bottom line'. Not for work items → `write-work`. Not for investigation → `research`. Not for diagnosis → `diagnosing-bugs`.
argument-hint: "spec | hld | toi | research | bottom-line | root-cause"
---

# Write a document

Own specification, HLD, TOI, research report, bottom-line and root-cause report structure, rendering, incremental updates and document checks. Callers own discovery, design decisions, decomposition, evidence dispatch, approvals, worktrees, integration and publication.

## Routing

| Route | Select for | Playbook | Output |
|---|---|---|---|
| `spec` | A specification or PRD from supplied requirements and decisions | [Spec](playbooks/spec.md) | Specification body |
| `hld` | A high-level design from supplied evidence and resolved decisions | [HLD](playbooks/hld.md) | New or incrementally updated HLD |
| `toi` | A developed feature's technical Transfer of Information (TOI) | [TOI](playbooks/toi.md) | TOI document |
| `research` | A full research report from supplied findings and evidence | [Research](playbooks/research.md) | Research report with a bottom line |
| `bottom-line` | A standalone conclusion, key finding or recommended action | [Bottom line](playbooks/bottom-line.md) | One decision-oriented bullet per subject |
| `root-cause` | A root-cause report from a supplied diagnosis log and confirmed evidence | [Root cause](playbooks/root-cause.md) | Root-cause report printed inline |

## Execution

1. Honor an explicit route; otherwise infer the artifact type. Work-item requests return to the caller with `write-work` as owner; new investigation belongs to `research`, new diagnosis to `diagnosing-bugs`. Ambiguous type → ask and wait. Replies continue the active route unless redirected. Combined requests → author in dependency order, then request order for independent artifacts. Done when each requested artifact has a route.
2. Select `draft` (new), `update` (existing) or `normalize` (requirements wording only). `normalize` applies only to `spec`, `hld` and `toi`; an explicit report-route normalize request returns a scope gap without changing evidence. Standalone requirements without an artifact type, including `write-document normalize`, use `spec normalize`; preserve the supplied fragment's structure. Done when operation, scope and caller constraints are known.
3. Read the selected playbook and its required resources fully; for `normalize`, load local requirements resources only, omitting template-only resources; load conditional resources only when triggered. Resolve paths from this skill directory. Done when all inputs for the next action are loaded.
4. For `normalize`, apply Requirements rules and return. Otherwise execute the route. Use supplied context and permitted local reads; return missing evidence or decisions to the caller. Do not independently dispatch research/proof, decompose work, publish, commit or manage worktrees. Existing TOI read-only exploration remains permitted. For report routes, use supplied evidence only; missing evidence returns as a gap without probes, cause confirmation or inferred facts. Done when the artifact or an explicit incomplete result is returned.

## Requirements rules

For `spec`, `hld`, standalone `normalize`, and TOI statements of required behavior, read this skill's [Requirements](references/requirements.md) and [Requirements terms](references/requirements-terms.md). Normalize authored requirements, business rules, constraints and edge cases at their existing level using the domain glossary. Preserve descriptions of implemented TOI behavior, HLD responsibilities, decisions and technical contracts.

Preserve authoritative verbatim text. Report leaked implementation in such text as a source conflict; do not silently rewrite it. Keep technical decisions, structural relocation constraints, contracts, reproduction steps, observations and evidence exact. Document-specific rendering may derive criteria from rules/edge cases while retaining their source relationships.

For `normalize`, return the supplied text's structure with corrected wording and a correction note; skip full-template rendering, contract/diagram generation and unrelated edits. No leaks → report no corrections.

## Conditional resources

| Trigger | Resource |
|---|---|
| `spec` draft/update | [Spec template](templates/spec-template.md) |
| `hld` draft/update, including evolving drafts | [HLD template](templates/hld-template.md), [Decision bullets](references/decision-bullet.md), [HLD updates](references/hld-updates.md) |
| `toi` draft/update | [TOI template](templates/toi-template.md) |
| `research` draft/update | [Research template](templates/research-template.md), [Bottom line procedure](playbooks/bottom-line.md), [Bottom line template](templates/bottom-line-template.md), [Report language](references/report-language.md) |
| `bottom-line` draft/update | [Bottom line template](templates/bottom-line-template.md), [Report language](references/report-language.md) |
| `root-cause` draft/update | [Root-cause template](templates/root-cause-template.md) |

For report routes, retain source claims, confidence, observations and citations exactly; Requirements rules and generated contract deltas do not apply. Research executes the already-loaded Bottom line procedure in this session, then resumes Research; never recursively load this skill.

Changed contracts in `spec`, `hld` or `toi` → *Load and follow the `doc-contracts` skill to write an API, database, resource, or GUI contract delta* using the route's listed kinds and inputs. Missing contract facts return as gaps; never hand-write a delta.

Required diagrams in `spec`, `hld` or `toi` → *Load and follow the `doc-diagram` skill to create Mermaid architecture or behavior diagrams* using the selected route's view and source facts. Missing decisions/evidence return as gaps.

General prose refinement for `spec`, `hld` or `toi` when needed → *Load and follow the `write` skill to refine the spec, HLD, or TOI prose; select the applicable route.* Keep the artifact template and protected text.

## Output contract

Return the selected route's artifact. Use an explicit output path when supplied; HLD and TOI define defaults. Save drafts only within caller authorization; otherwise print the body. `root-cause` is print-only even when a destination is supplied: return the report inline and report the unsatisfied save request separately. Research returns the report body to its caller, which owns the delivery path and save. Return update summaries, source conflicts and missing evidence separately from publishable content. Keep exact-body-only route outputs free of wrapper prose; report blockers to the caller separately.

Mark unsupported facts Unknown or Pending as the route requires. Incomplete content is a draft, not readiness or publication success.

## Completion criteria

- Every requested artifact follows its selected route and canonical template, or the normalize operation preserves the supplied structure.
- Behavioral text passes local requirements rules; protected source text and technical evidence retain their required fidelity.
- No unsupported decisions, invented facts, authoring directives or unintended placeholders remain; required structural markers survive.
- Research includes each supplied subject, evidence status, remaining work, next steps and references; its bottom line adds no unsupported certainty. Root-cause output requires a confirmed hypothesis and evidence-row citations for every mechanism claim.
- Updates preserve unaffected content and report conflicts/gaps. No publication or workflow authority is inferred from drafting.
