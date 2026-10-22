# Component extractor

Prompt for a subagent. Task: find or create reusable UI components so flows and checks never repeat selectors.

Inputs from the parent: the capability needed (for example "pick an option in a dropdown"), the feature and page, the inventory in `proof/components/README.md`, and any *Playwright CLI* observations.

Do:

1. Read the inventory, `proof/components/`, `proof/pages/`. Reuse a component that already wraps the control; stop and report it.
2. Inspect the reachable app with *Playwright CLI*: accessibility snapshot, roles, labels, open and close behavior, keyboard use. Read the app source beside it. UI not built yet: record the missing surface, mark selectors unverified, invent nothing.
3. Create or extend a component in `proof/components/` for the control (dropdown, modal, table, form, tab, pager, date picker). Take a scoped `Locator` in the constructor, expose user verbs (`select(option)`, `rows()`), prefer roles, labels and test ids, never snapshot refs such as `e12`.
4. Add a focused test beside it. Run `{{TYPECHECK_PROOF}}` and `{{TEST_PROOF}}`.
5. Add a row to the inventory: component, file, what it wraps.

Return: files written, the inventory row, what was verified in the live UI, what is unverified. Write only inside `proof/components/`; the parent owns the files it is editing.
