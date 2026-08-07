---
name: to-capabilities
description: Break an idea or grilled requirement input into **capabilities**, each with a stakeholder requirement, functional requirements, business rules, and edge cases — solution-agnostic. Use to author structured requirement sets from a feature idea.
---

**Capability** — a single, focused area of system behavior, defined by verifiable requirements and scenarios. It is behavior the system provides *independently of where it appears* and *survives after the current change completes* — never a one-off task. It names what the system *does* and the outcome the actor gets. Each capability scopes exactly one requirement set (stakeholder requirement + functional requirements + business rules + edge cases); an idea spanning several unrelated behaviors yields one set per capability, never merged.

**Capability** - a **scoping unit**, not a requirement type. It exists to prevent requirement sprawl — each set stays focused on one behavior rather than bundling several unrelated behaviors under one title.

**Functional requirement** - imperative `{{behavior}} when {{condition}}.` statements — specific, testable, externally visible. Cover, at minimum: **Capability** (actions and outcomes), **Integration** (external interactions), **State** (persistence and state changes), **Permissions** (who may and may not act), **Degraded behavior** (what still works when a dependency is slow or fails).

# To Capabilities

Break a functional requirements, spec, or conversation into a set of **capabilities** — capability-aligned slices, each with a stakeholder requirement, functional requirements, business rules, and edge cases — solution-agnostic.

## Process

### 1. Gather context
Work with functional requirements from whatever is already in the conversation context. If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase
Use functional requirements and the (directory, solution, project, code) structure and module definitions defined in the docs (check `README.md`, `ARCHITECTURE.md`) to explore the codebase and understand the boundaries of the capabilities. Draft a **list of candidate capabilities**. Name capabilities with the project's domain vocabulary (check `CONTEXT.md`).

### 3. Group functional requirements per capability
- Use the the **list of candidate capabilities** and grouping rule and five-question decision process in [references/capability-detection.md](references/capability-detection.md) to group functional requirements into capabilities. Each capability must have a single purpose statement that covers all its requirements, and no two capabilities that change independently may share a set.
- Assign every provided requirement to exactly one capability; note each capability's domain/module, actors, inputs, and outputs.
- **Done when** every provided requirement belongs to one capability, every capability passes all five questions, and no two independently-changing capabilities share a set.

### 5. Quiz the user
Present the proposed capability breakdown as a numbered list. For each capability show:
- **Title** — the behavior + entity, solution-agnostic.
- **Stakeholder Requirement** — The {{actor}} needs to {{behavior}} {{entity}}, so {{value}}.
- **Covers** — the parts of the input it accounts for.

Ask the user:
- Does the granularity feel right? (too coarse / too fine)
- Should any capabilities merge (they share a purpose) or split (they change independently)?

Iterate until the user approves the breakdown.

### 6. Before output run Quality Check
- Each capability is atomic; unrelated capabilities are split into separate requirement sets.
- Every requirement is **solution-agnostic** — swapping UI or technology would not force a reword. Run `/solution-agnostic` to check **capability title**, **functional requirements**, **business rules**, and **edge cases** are **solution-agnostic**.
- Every functional requirement is specific, testable, and externally visible.
- Business rules state invariants, not capabilities.
- Every edge case traces to a functional requirement or business rule.

### 7. Write the output
Write **all** capability blocks into **one** file `docs/requirements/{{slug}}.md`, following the template and writing style in [references/output-format.md](references/output-format.md). `{{slug}}` is a short kebab-case identifier derived from the input or lead capability (e.g., `reinstate-cancelled-orders`, `real-time-catalog-availability`). Create the `docs/requirements/` directory if it does not exist.