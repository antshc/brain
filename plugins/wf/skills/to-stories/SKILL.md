---
description: Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories** — broken down by capability and technology layer (FE/BE), each carrying a capability reference, stakeholder requirement, functional-requirements list, acceptance criteria, and Jira-sync metadata (Jira ID, Epic ID, Blocked by) — that map to a production codebase. Use when the user has requirements and wants stories, backlog-ready items, acceptance criteria, or FE/BE-split tickets ready to sync with Jira.
name: to-stories
disable-model-invocation: true
---

Package a **single requirement** or a **list of requirements** into one or more atomic, testable, implementation-agnostic **user stories**, broken down **by capability and technology layer (FE/BE)**.

This skill owns the **breakdown**: which capabilities the input holds, which layer(s) each touches, and how the resulting stories are numbered and linked. The story itself — its four blocks, acceptance-criteria rule, sync metadata, appendices, and format — is owned by `draft-story`.

The input is typically a prior requirement set — a capability with its stakeholder requirement, functional requirements, business rules, and edge cases. It also works standalone on any requirement text.

Produce **one story per capability per technology layer**. A capability touching only one layer → one story; a capability spanning both **FE** and **BE** → one story per layer, only after the user approves the breakdown. Split anything non-atomic; never merge unrelated behaviors into one story.

## Capability Identification
Before assembling a story, confirm each candidate is one **capability** — behavior the system provides independently of where it appears, that survives after the current change completes — never a one-off task.
- **Group by shared purpose.** One capability = one purpose statement covering all its requirements. Split when parts differ substantially in actor goals, business rules, permissions, lifecycle, failure handling, external contracts, ownership, or rate of change — that difference is the signal to split, not merge.
- **Strip placement first.** A candidate naming a surface ("show count in header") isn't a capability yet — rewrite it as pure behavior ("provide an active count summary") before judging its scope.
- **Test independence.** If one group's rules can change without touching the other's, they are separate capabilities, hence separate stories.
- **Don't atomize trivial output.** A single tiny output with no behavioral scope of its own belongs inside its broader stable capability, not alone.
- **Done when** every input requirement lands in exactly one capability and no capability bundles two independently-changing behaviors.

## Workflow
1. **Analyze input** → identify each distinct capability (apply Capability Identification above), its domain/module, actors, inputs, outputs, failure cases.
2. **Propose breakdown** → for each capability, classify which technology layer(s) it involves — **BE**: API/data/contract/business-rule behavior; **FE**: presentation/interaction behavior. Present a numbered breakdown table (capability → technology tag(s) → story count) to the user and wait for explicit approval; revise and re-confirm on requested merges/splits/reassignments. *Done when* the user has approved a table; draft no story before that.
3. **Number and link** → assign each approved row a story number in table order, and derive its Blocked-by list from ordering dependencies inside this batch only — a row depending on nothing gets `None`. *Done when* every row carries a number and a resolved Blocked-by list.
4. **Draft each story** → run `/draft-story` skill once per approved row, handing it the capability title, stakeholder requirement, functional-requirements list, technology layer, story number, Blocked-by list, and the feature slug when the user asked for one. A capability spanning both layers keeps the same title, stakeholder requirement, and functional-requirements list in both stories, with acceptance criteria scoped to that layer's behavior only. *Done when* every approved row has a story that passed that skill's Quality Check.

## Quality Check (before output)
- Every input requirement landed in exactly one capability, and every capability passed the grouping and independence checks before any story was drafted.
- The FE/BE breakdown table was presented and explicitly approved by the user before any story was drafted.
- Story count matches the approved table row for row, and numbering follows table order.
- Blocked-by entries reference only `(Story n, Jira ID placeholder)` pairs from this batch, or `None`.
- A capability split across FE and BE carries identical title, stakeholder requirement, and functional-requirements list in both stories, with no criterion testing the other layer's behavior.

## Output Format

Emit the stories in approved-table order, each rendered by `/draft-story` in its own format, separated by a blank line. Add no wrapper prose, no summary section, and no cross-story index around them.
