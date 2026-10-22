# Components

Reusable page parts (a dropdown, a modal, a table) shared by page objects, flows and checks. Each one wraps the selectors and waits of one UI part once, so a feature never repeats them.

Before you build a part, search here and in `pages/`. List what exists:

| Component | Where | What it wraps |
|---|---|---|

Add a row when you add a component. `.github/skills/verify-mole/scripts/component-extractor.md` finds repeated UI parts in the app and proposes components.
