# Artifact rules

Shared rules for work item routes (`story`, `task`, `bug`) and document routes (`spec`, `hld`, `toi`, `research`, `bottom-line`, `root-cause`, `doc`). These routes own structure, rendering, incremental updates and document checks. Callers own discovery, design decisions, decomposition, evidence dispatch, approvals, worktrees, integration and publication. `design tasks` selects a task breakdown; `write task` renders one supplied task.

## Execution

1. **Operation.** Select `draft` (new), `update` (existing) or `normalize` (requirements wording only). `normalize` applies only to `story`, `task`, `bug`, `spec`, `hld` and `toi`; an explicit normalize request for another route returns a scope gap without changing content or evidence. Standalone requirements without an artifact type, including `write normalize`, use `spec normalize`; preserve the supplied fragment's structure. Done when operation, scope and caller constraints are known.
2. **Load.** Read the selected playbook and the router's Artifact resources for its trigger fully; for `normalize`, load the requirements resources only. Done when all inputs for the next action are loaded.
3. **Execute.** For `normalize`, apply Requirements rules and return. Otherwise execute the playbook. Use supplied context and permitted local reads; return missing evidence or decisions to the caller. Do not independently dispatch research or proof, decompose work, publish, commit or manage worktrees. Read-only exploration remains permitted for existing Bug and TOI routes. Report routes (`research`, `bottom-line`, `root-cause`) use supplied evidence only; missing evidence returns as a gap without probes, cause confirmation or inferred facts. Done when the artifact or an explicit incomplete result is returned.

## Requirements rules

Apply the Requirements and Requirements terms resources to authored behavioral text:

| Route | Normalize | Preserve exactly |
|---|---|---|
| `story` | Story outcomes and acceptance criteria | Supplied Feature and slice descriptions, technical notes |
| `task` | Task acceptance criteria | Technical scope, structural relocation constraints |
| `bug` | Expected behavior and definition of fixed | Reproduction steps, actual observations, evidence |
| `spec`, `hld` | Requirements, business rules, constraints and edge cases | HLD responsibilities, decisions and technical contracts |
| `toi` | Statements of required behavior | Descriptions of implemented behavior |

Normalize at the existing level using the domain glossary. Preserve authoritative verbatim text. Report leaked implementation in such text as a source conflict; do not silently rewrite it. Keep technical decisions, structural relocation constraints, contracts, reproduction steps, observations and evidence exact. Document-specific rendering may derive criteria from rules and edge cases while retaining their source relationships.

For `normalize`, return the supplied text's structure with corrected wording and a correction note; skip full-template rendering, contract and diagram generation and unrelated edits. No leaks → report no corrections.

For report routes, retain source claims, confidence, observations and citations exactly; Requirements rules and contract deltas do not apply. Research executes the already-loaded Bottom line procedure in this session, then resumes Research; never reload this skill.

## Output contract

Return the selected route's artifact. Use an explicit output path when supplied; HLD and TOI define defaults. Save drafts only within caller authorization; otherwise print the body. `root-cause` is print-only even when a destination is supplied: return the report inline and report the unsatisfied save request separately. Research returns the report body to its caller, which owns the delivery path and save. Return update summaries, source conflicts and missing evidence separately from publishable content. Keep exact-body-only route outputs free of wrapper prose; report blockers to the caller separately. Writing notes and gaps stay outside publishable content.

Mark unsupported facts Unknown or Pending as the route requires. Incomplete content is a draft, not readiness or publication success.

## Completion criteria

- Every requested artifact follows its selected route and canonical template, or the normalize operation preserves the supplied structure.
- Behavioral text passes Requirements rules; protected source text and technical evidence retain their required fidelity.
- No unsupported decisions, invented facts, authoring directives or unintended placeholders remain; required structural markers survive.
- Research includes each supplied subject, evidence status, remaining work, next steps and references; its bottom line adds no unsupported certainty. Root-cause output requires a confirmed hypothesis and evidence-row citations for every mechanism claim.
- Updates preserve unaffected content and report conflicts and gaps. No publication or workflow authority is inferred from drafting.
