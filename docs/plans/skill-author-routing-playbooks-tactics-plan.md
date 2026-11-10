# Skill Author routing, playbooks, and tactics plan

Status: proposed. Date: 2026-11-10.

## Goal

Extend `skills/productivity/skill-author` so it can design and generate simple skills or complex skills with a router in `SKILL.md`, route-specific playbooks, and reusable conditional tactics. Preserve the existing Grill → Draft → Shrink process and avoid empty folders or unnecessary abstraction.

## Current state

- `skill-author/SKILL.md` selects Grill, Agent, Shrink, or Write and loads playbooks from `playbooks/`.
- `templates/SKILL.template.md` supports inline Workflow, Loop, Tactics, and Reference blocks, but has no explicit multi-route router block or external playbook/tactic templates.
- `playbooks/grill.md` collects purpose, callers, triggers, steps/tactics, and resources; it does not explicitly inventory routes and their playbooks.
- `playbooks/draft.md` discloses detailed reference content but does not define when to generate `playbooks/` or `tactics/`.
- `playbooks/shrink.md` preserves behavior and pointers, but does not explicitly verify route-to-playbook and tactic-trigger coverage.
- Existing `design` and `review` skills use `playbooks/` for routed procedures. Design's verification/external-source tactics currently live in `references/`.
- `.github/instructions/agent-skills.instructions.md` recognizes kind folders and direct links; it needs explicit guidance for `playbooks/` and `tactics/`.

## Vocabulary and ownership

| Term | Meaning | Placement |
| --- | --- | --- |
| **Router** | Selection logic for outcomes or execution variants within an activated skill. | `SKILL.md` |
| **Route** | One selectable outcome or execution path, with trigger and output contract. | A row/decision in `SKILL.md`, not a separate folder |
| **Playbook** | End-to-end task procedure, including inputs, decisions, steps, failures, and completion criteria. | `playbooks/<route>.md` when extraction is useful |
| **Tactic** | Narrow conditional method used within one or more routes; has trigger, technique, and result. | Inline `## Tactics` or `tactics/<name>.md` |
| **Reference** | Supporting knowledge, schemas, examples, or conventions rather than task ownership. | `references/` |

Router selection and playbook execution are separate responsibilities. A playbook owns its route's task outcome; a tactic only addresses a subproblem. These are repository conventions, not fields mandated by the Agent Skills specification.

Add **Route** to root `GLOSSARY.md`. Retain the existing Router, Playbook, and Tactic definitions. Add concise operational distinctions to the skill-local `references/best-practices.md` so installed copies remain self-contained.

## Target skill-author structure

```text
skill-author/
  SKILL.md
  playbooks/
    grill.md                 # extend brief
    agent.md                 # unchanged
    draft.md                 # generate composition
    shrink.md                # preserve routes and tactics
  references/
    best-practices.md       # define composition rules
    wording.md
    agent-best-practices.md
    agent-examples.md
    agent-platforms.md
  templates/
    SKILL.template.md       # add optional Router and external Tactics blocks
    playbook.template.md    # new
    tactic.template.md      # new
    agent.template.md
    planner.template.md
    planner-output.template.md
```

No internal `tactics/` folder is required for `skill-author` itself. The new templates describe tactics that it may create for target skills.

## Optional structure of a generated skill

```text
my-skill/
  SKILL.md                  # discovery, router, shared constraints
  playbooks/                # only for substantial route procedures
    create.md
    update.md
  tactics/                  # only for substantial conditional techniques
    verification.md
  references/               # when knowledge is needed
    api.md
  templates/                # when scaffolds are needed
    output.template.md
  scripts/                  # when deterministic operations are needed
    cli.py
```

Generate only required directories and files. Do not force Router, Playbooks, or Tactics into a small single-procedure skill.

## Structure selection

| Need | Authoring choice |
| --- | --- |
| One short procedure used in most runs | Inline `## Workflow` |
| Several related outcomes with distinct steps | `## Routing` in `SKILL.md` and separate `playbooks/` |
| One or two short, always-needed methods | Inline `## Tactics` |
| Bulky, conditional, or multi-playbook techniques | `tactics/`, linked directly from `SKILL.md` |
| Definitions, policies, API details, examples | `references/` |
| Fillable output structures | `templates/` |
| Repetitive or error-prone deterministic work | `scripts/` |
| Independently discoverable capability or authority boundary | Separate skill, not a route |

Every routed outcome needs an unambiguous trigger, selected playbook, output contract, ambiguity handling, and behavior for combined requests. Keep shared invariants in `SKILL.md`. Conditional playbooks and tactics must be reachable by direct links from `SKILL.md`; no playbook → tactic → reference loading chains. All paths resolve from the target skill's base directory.

### SKILL.template.md changes

Add optional blocks with hidden `<!-- @: -->` rendering directives:

- `## Routing`: `Route | Select when | Playbook`, explicit selection/continuation/ambiguity policy, and read-only-selected-playbook rule.
- `## Tactics`: a compact registry mapping each observable trigger to its linked tactic and expected result.
- Existing Workflow/Loop/Reference/Output blocks stay available. Delete unused blocks and template directives.

Example router:

```markdown
## Routing

| Route | Select when | Playbook |
| --- | --- | --- |
| create | New resource | [Create](playbooks/create.md) |
| update | Existing resource | [Update](playbooks/update.md) |

Read only the selected playbook. Ask when the requested outcome remains ambiguous.

## Tactics

- **Verification** — when independent proof is needed, read [Verification](tactics/verification.md).
```

### New playbook.template.md

Include: title, owned outcome, inputs, ordered procedure with checkable step completion, output/no-result/incomplete behavior, and result completion criteria when needed. Reference shared skill rules without duplicating them. Do not introduce a second router.

### New tactic.template.md

Include: title, observable trigger, technique or decision criteria, and result/evidence. No standalone task output contract or unnecessary workflow. The tactic should be reusable and conditionally invoked.

## Affected files

| File | Change |
| --- | --- |
| `skill-author/SKILL.md` | Add direct optional pointers to composition guidance and templates; retain existing outer routing and phase isolation |
| `skill-author/playbooks/grill.md` | Extend brief: route inventory (name, intent, output), playbook ownership, tactic trigger/consumer/result, and selected resource layout |
| `skill-author/playbooks/draft.md` | Select inline versus extracted structure; create route playbooks/tactics and direct pointers; preserve existing authoring obligations |
| `skill-author/playbooks/shrink.md` | Inventory and preserve every route, route trigger, playbook path, tactic trigger, and output contract |
| `skill-author/references/best-practices.md` | Add terminology, conditional folder selection, route composition, and direct-link rules |
| `skill-author/templates/SKILL.template.md` | Add optional Routing and linked Tactics sections |
| `skill-author/templates/playbook.template.md` | New reusable playbook scaffold |
| `skill-author/templates/tactic.template.md` | New reusable tactic scaffold |
| `.github/instructions/agent-skills.instructions.md` | Recognize `playbooks/` and `tactics/` as conditional skill-local resource folders; retain direct-link and no-reference-chain rules |
| `GLOSSARY.md` | Add Route in shared language; preserve existing definitions |

Do not refactor existing `design`, `review`, or other skills as part of this change. Do not change `playbooks/agent.md`.

## Implementation sequence

1. Extend the vocabulary and repository resource-layout rules.
2. Add playbook/tactic templates and optional blocks to `SKILL.template.md`.
3. Update Grill to record routes and tactics in the skill brief before drafting.
4. Update Draft to select composition and create only justified files; link them directly from the generated `SKILL.md`.
5. Update Shrink and the outer author skill's final checks to preserve and validate routed behavior.
6. Run existing repository validation and targeted authoring cases; repair any broken pointers or lost behavior.

## Verification

| Case | Expected result |
| --- | --- |
| Simple one-procedure skill | Single `SKILL.md`; no empty `playbooks/` or `tactics/` |
| Multi-route skill | Router selects distinct playbooks; no unrelated playbook loaded |
| Shared tactic | Multiple routes use one tactic with one authoritative definition; trigger documented in `SKILL.md` |
| Conditional reference | Reads the relevant file only when condition holds |
| Rewrite existing skill | Every original rule, route, pointer, output, and failure path preserved or explicitly changed |
| Shrink phase | Links still resolve, route and tactic coverage unchanged, no unflagged behavior loss |

Also verify frontmatter, relative paths, direct links, no unresolved template directives, no duplicated procedures, and the repository's under-300-line `SKILL.md` rule. Verify that user-invoked versus model-invoked behavior and independent Draft/Shrink subagent phases remain unchanged.

## Non-goals

- Introduce separate discoverable skills for every route.
- Require `playbooks/` or `tactics/` in all generated skills.
- Relocate existing Design/Review tactics.
- Create another skill-author execution mode.
- Change GitHub publishing or authorization behavior.
