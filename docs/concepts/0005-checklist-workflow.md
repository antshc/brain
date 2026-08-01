# Checklist-Driven Workflow

**Status:** Accepted

## Purpose

A multi-step skill or agent task with sequential, resumable steps — where skipping a step, losing progress after a context reset, or not returning to an earlier step after a failure would break correctness — needs an explicit anchor for progress. A Checklist-Driven Workflow embeds a literal Markdown checklist in the skill instructions that the agent copies into its own working notes at task start, checks off one item at a time as it executes, and re-consults before declaring the task done. It is not a Copilot/GPT/Claude feature; it is a reusable skill-authoring pattern any skill with an ordered, multi-step procedure can adopt.

## Design Guidance

- Use for skills with 3+ sequential steps where skipping/reordering breaks correctness, or where a step can fail and require returning to an earlier step.
- Emit the checklist as literal, fenced Markdown (`- [ ] Step N: ...`) that the agent is instructed to copy and check off — not just prose describing the order.
- Precede the fenced checklist with the literal instruction line `Copy this checklist and check off items as you complete them:` — this is required, not optional prose; a checklist without it risks being read as reference material instead of copied into working notes.
- Name the checklist header after the task/section it belongs to (`<Task name> Progress:`), not a generic `Task Progress:` or `Progress:` label — this keeps multiple checklists (e.g. an agent's own plus each of its skills') distinguishable when copied into working notes together.
- Pair each checklist item with its own numbered subsection giving the exact command/action and expected artifact, so the agent executes directly without re-deriving the step.
- Name concrete inputs/outputs/scripts per step, not generic descriptions.
- State the failure/retry path explicitly (e.g. "if verification fails, return to Step 2") rather than leaving recovery to inference.
- Distinct from a Completeness Sweep ([0004](0004-completeness-sweep.md)): a Checklist-Driven Workflow orders sequential execution steps *during* the task; a Completeness Sweep is a closing pass that checks coverage *after* implementation is believed done.
- Minimal skill instruction to embed:

```
## <Task name> workflow

Copy this checklist and check off items as you complete them:
\```
<Task name> Progress:
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

- An agent/skill family that wants uniform structure across every step (e.g. Codey, Chorey, and their Ralph skills) may embed a literal checklist even for 1-2 step skills, trading minor ceremony for consistency across the whole family. The 3+/order-sensitive bar remains the default for skills outside such a family.
