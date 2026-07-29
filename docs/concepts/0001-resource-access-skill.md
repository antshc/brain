# Resource Access Skill

## Purpose

A feature skill that needs infrastructure (a ticket tracker, a docs backend, an external API) risks coupling its callers directly to a specific vendor or tool. A Resource Access Skill encapsulates access to one category of infrastructure — similar to the iDesign Resource Access layer — so the backend can be replaced without affecting its callers.

## Design Guidance

- A Resource Access Skill owns all vendor-specific knowledge for one infra category (commands, IDs, formats). That knowledge lives only inside the skill, not in its callers.
- Direct use of the underlying infra tool is still allowed. When a caller does invoke the skill, it must do so via the skill's documented actions, using the style `run` / `via` `` `/{{skillName}}` `` **{{ActionName}}** — never by inlining the underlying infra command in place of the skill reference.
- An action reads its inputs as `{{placeholder}}` variables already in the caller's context (the same way the action's own steps reference them internally), rather than declaring a formal call-site argument list. An action documents its return shape (what it hands back to the caller) alongside its steps, so a caller can invoke it without reading the skill's internals.
- The skill's set of actions is its stable interface. Swapping the backend (e.g. GitHub → Jira) means rewriting the skill's internals only; callers and their invocation style stay unchanged.
- Examples in this repo: `manage-backlog` (ticket tracker, currently GitHub issues, swappable for Jira) and `index-docs` (docs backend, currently local markdown files).
