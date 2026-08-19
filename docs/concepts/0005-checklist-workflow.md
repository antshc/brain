# Checklist-Driven Workflow

**Status:** Accepted

## Purpose

A skill or agent task with multiple actions needs an explicit, ordered process when skipping an action, losing progress after a context reset, or failing to return after an error would break correctness. A numbered instruction list gives the agent that process: it makes the required order visible and provides stable references for each action. A Checklist-Driven Workflow is the more advanced form of this control: it embeds a literal Markdown checklist that the agent copies into its working notes at task start, checks off one item at a time, and re-consults before declaring the task done. The copied checklist gives the agent an explicit, durable record of execution state. It is not a Copilot/GPT/Claude feature; it is a reusable skill-authoring pattern for any skill with an ordered procedure.

## Design Guidance

- Use numbered instructions for skills with sequential actions, especially where skipping or reordering an action breaks correctness.
- Use a copied checklist for skills with 3+ sequential actions, where progress must survive a context reset, or where a failure requires returning to an earlier item.
- Emit the checklist as literal, fenced Markdown (`- [ ] N. ...`) that the agent is instructed to copy and check off — not just prose describing the order.
- Precede the fenced checklist with the literal instruction line `Copy this checklist and check off items as you complete them:` — this is required, not optional prose; a checklist without it risks being read as reference material instead of copied into working notes.
- Name the checklist header after the task/section it belongs to (`<Task name> Progress:`), not a generic `Task Progress:` or `Progress:` label — this keeps multiple checklists (e.g. an agent's own plus each of its skills') distinguishable when copied into working notes together.
- Pair each checklist item with its own numbered subsection giving the exact command/action and expected artifact, so the agent executes directly without re-deriving the action.
- Name concrete inputs, outputs, and scripts for each numbered item, not generic descriptions.
- State the failure/retry path explicitly (e.g. "if verification fails, return to item 2") rather than leaving recovery to inference.
- Distinct from a Completeness Sweep ([0004](0004-completeness-sweep.md)): a Checklist-Driven Workflow orders sequential execution steps *during* the task; a Completeness Sweep is a closing pass that checks coverage *after* implementation is believed done.
- Minimal skill instruction to embed:

```
## <Task name> Workflow

Copy this checklist and check off items as you complete them:
\```
<Task name> Progress:
- [ ] 1. <action> (run <script>)
- [ ] 2. <action> (edit <file>)
- [ ] 3. <action> (run <script>)
\```
**1. <action>**

Run: `<command>`

<what it produces>

...

If item <N> fails, return to item <M>.
```

## Exceptions

- An agent/skill family that wants uniform structure for every action (e.g. `codey`/`chorey` and their `crew-*` skills) may embed a literal checklist even for 1-2 actions, trading minor ceremony for consistency across the whole family. The 3+/order-sensitive bar remains the default for skills outside such a family.
