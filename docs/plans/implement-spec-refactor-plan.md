# Implement Spec refactor plan

Target: `antshc/brain`, branch `feat/implement-spec-entry-flow`, directory
`plugins/wf/skills/implement-spec/`.

Proposed replacement body: [implement-spec-skill-body.md](implement-spec-skill-body.md).
The companion file contains the complete body; preserve the existing SKILL.md frontmatter.
Its reference links target the final skill directory and become valid when the refactor is implemented.

## Plan

1. Replace the SKILL.md body with the companion file's Inputs + 14-step flow.
   Omit the unsupported-mode rejection. Keep the body responsible for orchestration
   and reference loading; move detailed procedures into references.

2. Redistribute detailed instructions without losing existing safeguards:

   | Reference | Content |
   | --- | --- |
   | `references/breakdown.md` | Prepare Plan, Prepare Spec, planner launch preparation, breakdown validation |
   | `references/sequential.md` | Sequential execution, shared launch contract, implementer prompt/result checks, App Verification |
   | `references/parallel.md` | Execution settings, scope exploration, graph/conflict scheduling, parallel execution |
   | `references/github.md` | Constraints, graph validation, publication, frontier check, code review, closure gates, reporting/completeness |
   | `references/fetch-diff.md` | Diff preparation and Chore Pass |
   | New `references/worktrees.md` | Integration setup, parallel ticket worktrees, isolation, cleanup and preservation rules |

3. Update all links and section names. Load GitHub constraints before step 1,
   since preparation performs GitHub operations. The companion body includes this adjustment.

4. Update all four agent bodies (`planner.md`, `implementer.md`, `verifier.md`,
   `chore.md`): replace the hardcoded five-reference manifest with the expanded
   manifest containing `worktrees`. Preserve role-specific loading and authority
   limits; update the launch contract's path validation accordingly.

5. Remove duplicated procedures and stale references to old SKILL.md headings
   and step numbers. Reference procedures return control to the orchestrator;
   agents cannot launch agents. Worktree lifecycle instructions have one owner:
   `references/worktrees.md`; other references link to it.

6. Validate links, anchors, placeholders, manifest consistency, and instruction
   preservation. Walk through plan/spec inputs, both execution modes,
   HITL/blockers, verification skips/failures, unsafe cleanup, and closure gates.
   Confirm every original constraint, output requirement, completion criterion,
   and completeness-sweep instruction has a destination or an explicit requested removal.

## Acceptance

- SKILL.md remains an orchestration flow with inputs and phase-specific links.
- Worktree instructions reside in the separate reference.
- Every linked section exists after implementation.
- Agent handoffs use the expanded manifest consistently.
- Existing execution/publication authority, evidence checks, preservation rules,
  and draft-only closure gates remain intact except for the requested mode-rejection removal.

Status: proposal only; repository changes are not implemented by publishing these files.
