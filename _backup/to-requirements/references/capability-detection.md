# Capability Detection

How to split an input into **capabilities** before writing requirement sets. A **capability** is behavior the system provides *independently of where it appears*, and it *survives after the current change is completed* — never a screen, control, or one-off task. Each capability becomes exactly one requirement set.

## Grouping rule
Group requirements that share **one clear purpose**. Split them into separate capabilities when the groups differ substantially in any of:
- actor goals
- business rules
- permissions
- lifecycle
- failure handling
- external contracts
- ownership
- rates of change

A difference in one or more of these means the groups **change independently** — the signal to split. Avoid both directions of error: do not create one capability per requirement automatically, and do not merge behaviors that evolve independently into one catch-all.

## Decision process
Run these questions in order on each candidate.

1. **Is this a stable behavior domain?** If the candidate names placement or a surface ("show alert count in header"), rewrite it as pure behavior ("provide an active alert summary") before judging. Done when the candidate names a behavior with no placement left in it.
2. **Can one purpose statement cover all its requirements?** One sentence covers them → keep one capability. It can't → split along the sentence's seam. Done when every retained capability has a single purpose statement that covers all its requirements.
3. **Can the requirements change independently?** If one group's rules can change without touching another's, they are separate capabilities. Done when no capability holds two groups that change on different clocks.
4. **Does the candidate hold several related behaviors, or just one tiny output?** Several related behaviors → it stands alone as a capability. One tiny output with no likely behavioral scope → place it inside a broader stable capability rather than alone. Done when no capability is a lone trivial output.
5. **Is the name independent of UI and implementation?** Replace any page, grid, button, endpoint, controller, service, or database name with the domain behavior. Done when renaming a screen or swapping the technology would not force a retitle.

## Result
Every requirement belongs to exactly one capability; each capability passes all five questions; no two capabilities that change independently are merged.

## Worked example
*"Show alert count in header"* is not yet a capability — it carries placement. Rewrite the behavior as *"Provide an active alert summary"*, yielding the capability `alert-summary`. If alert-count rules can change without task-action rules changing, keep `alert-summary` separate from the task capability.
