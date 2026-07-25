# Checklist-Driven Workflow

**Status:** Accepted

## Purpose

A multi-step skill or agent task with sequential, resumable steps — where skipping a step, losing progress after a context reset, or not returning to an earlier step after a failure would break correctness — needs an explicit anchor for progress. A Checklist-Driven Workflow embeds a literal Markdown checklist in the skill instructions that the agent copies into its own working notes at task start, checks off one item at a time as it executes, and re-consults before declaring the task done. It is not a Copilot/GPT/Claude feature; it is a reusable skill-authoring pattern any skill with an ordered, multi-step procedure can adopt.

## Design Guidance

- Use for skills with 3+ sequential steps where skipping/reordering breaks correctness, or where a step can fail and require returning to an earlier step.
- Emit the checklist as literal, fenced Markdown (`- [ ] Step N: ...`) that the agent is instructed to copy and check off — not just prose describing the order.
- Pair each checklist item with its own numbered subsection giving the exact command/action and expected artifact, so the agent executes directly without re-deriving the step.
- Name concrete inputs/outputs/scripts per step, not generic descriptions.
- State the failure/retry path explicitly (e.g. "if verification fails, return to Step 2") rather than leaving recovery to inference.
- Distinct from a Completeness Sweep ([0004](0004-completeness-sweep.md)): a Checklist-Driven Workflow orders sequential execution steps *during* the task; a Completeness Sweep is a closing pass that checks coverage *after* implementation is believed done.
- Minimal skill instruction to embed:

```
## <Task name> workflow

Copy this checklist and check off items as you complete them:
\```
Progress:
- [ ] Step 1: <action> (run <script>)
- [ ] Step 2: <action> (edit <file>)
- [ ] Step 3: <action> (run <script>)
\```
**Step 1: <action>**

Run: `<command>`

<what it produces>

...

If <step N> fails, return to Step <M>.
```

## Exceptions

- None recorded yet.
