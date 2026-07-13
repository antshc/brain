---
description: Break down or group a **scope** — user story, ticket, task, or feature design — into smaller or bigger pieces organised by **capability**. Use when the user wants to decompose a scope into capabilities, group several capabilities into one user story, or split a capability into smaller pieces.
name: breakdown
disable-model-invocation: true
---

Break down or group a **scope** — a user story(s), ticket(s), task(s), or feature design — into smaller or bigger pieces organised by **capability**. A **capability** is behaviour the system provides independently of where it appears, and it survives after the current change ships — never a screen, control, or one-off task.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Pick the direction (optional)

Ask the user which move they want, then run only that branch:

- **Decompose** — split the scope into its capabilities.
- **Group** — fold several capabilities into one user story.
- **Split** — break one capability into smaller pieces.

Done when the user has named one direction.

### 3. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Capability names should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 4. Detect capabilities

Every direction turns on the same test: does a group of behaviour form **one capability**, or two that **change independently**?

<capability-detection>

**Grouping rule.** Keep behaviours that share one clear purpose in one capability. Split into separate capabilities when the groups differ in any of: actor goals, business rules, permissions, lifecycle, failure handling, external contracts, ownership, rate of change. A difference in one or more means they **change independently** — the signal to split. Avoid both errors: not one capability per requirement, not one catch-all.

Run these questions in order on each candidate:

1. **Stable behaviour domain?** If it names placement or a surface ("show alert count in header"), rewrite as pure behaviour ("provide an active alert summary") first. Done when no placement is left in the name.
2. **One purpose statement covers all its requirements?** One sentence covers them → one capability. It can't → split along the sentence's seam.
3. **Requirements change independently?** If one group's rules can change without touching another's, they are separate capabilities.
4. **Several related behaviours, or one tiny output?** Several → it stands alone. One tiny output with no behavioural scope → place it inside a broader capability, not alone.
5. **Name independent of UI and implementation?** Replace any page, grid, button, endpoint, controller, service, or database name with the domain behaviour. Done when renaming a screen or swapping the technology forces no retitle.

</capability-detection>

Apply the test to your direction:

- **Decompose** — run the five questions across the scope; each retained capability becomes one piece. Done when every part of the scope belongs to exactly one capability.
- **Group** — confirm the candidate capabilities share one purpose statement and none change independently, then fold them into one user story.
- **Split** — treat the capability as the scope and run the five questions again to find the seams inside it.

Done when every piece is a capability that passes all five questions, named in domain behaviour.

### 5. Quiz the user

Present the result as a numbered list. For each piece show:

- **Name** — the capability in domain-behaviour terms.
- **Purpose** — the one-sentence statement that covers its requirements.
- **Covers** — the parts of the original scope it accounts for.

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Should any pieces merge (they share a purpose) or split (they change independently)?

Iterate until the user approves the breakdown.

### 6. Record the result

Write the approved pieces back into the **source** the user provided — never a new file of your own shape. Edit that file in place, matching its existing formatting — heading levels, list style, field labels, ordering. Make the **minimal changes** that add, merge, or split the pieces; leave everything else byte-for-byte. Mirror the file's own kind: a user-stories file gets stories, a capabilities file gets capabilities.

Done when every piece lands in the provided source and the source's original formatting is preserved.
