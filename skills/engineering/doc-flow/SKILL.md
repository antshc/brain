---
name: doc-flow
description: Draft or revise workflows as compact numbered pseudocode. Use for `flow!`, doc-flow, process flows, branching execution paths, skill handoffs, subflows, and subprocesses.
---

# Doc Flow

1. Read [subflow-template.md](references/subflow-template.md) completely before drafting.
2. Prefer the template's **main flow + named subflows** when the workflow has alternate paths, handoffs, reusable phases, or subprocesses. Use a single flow only when no meaningful subflow exists or the user requests one.
3. Keep the main flow at orchestration level: shared entry, decision, calls to named subflows, and end. Put branch-specific steps in their own subflows.
4. Number steps independently within each flow, starting at 1. Label branches A, B, etc. Match every `Run <name>` call to an exact `Subflow <label>: <name>` and end each subflow with `Return`.
5. Use short verb phrases; retain supplied skill names, execution modes, order, and handoffs. When the user requests skill-call level, do not expand skills into internal steps.
6. Express loops as `For each <item>:` followed by the called action or skill. Express concurrency as `In parallel:` followed by the independent actions and an explicit join when relevant.
7. Preserve known decisions and outcomes. Mark required unknown behavior `TBD`; do not invent missing steps.
8. Return only the numbered flow unless an explanation or different format is requested.
