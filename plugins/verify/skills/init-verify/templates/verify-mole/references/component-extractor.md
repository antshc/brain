# Component extractor

Prompt for a subagent. The parent launches a new subagent session whose prompt is the body of this file, with the inputs below appended. Run it while you author or run a scenario. Task: find or create the reusable UI controls the scenario needs, and help write the scenario around them, so flows and checks never repeat selectors.

Inputs from the parent: the control the scenario needs (for example "pick an option in a dropdown"), the feature, sub-feature and page, the feature map, the inventory in `proof/components/`, and any *Playwright CLI* observations. When a scenario run failed on a control, also the failing scenario id and its receipt.

Do:

1. Search `proof/components/`, `proof/pages/` and `proof/flows/` for the control. Found and fits: report it and stop. Found but missing a behavior: extend it and keep its existing methods.
2. Explore the live control with *Playwright CLI*: open the page, take a snapshot, operate it, note open and close behavior and keyboard use. No GUI: read the app source and mark each selector unverified. UI not built yet: record the missing surface and invent nothing.
<!-- lang: python -->
3. Write one class per control in `proof/components/<control>.py` (dropdown, modal, table, form, tabs, pagination, date picker) using the sync Playwright API. Locate by role and accessible name; fall back to a label or test id only when the role is absent. Never persist snapshot refs such as `e12`.
4. Expose behavior (`choose`, `is_open`, `rows`), not selectors. Take the control's accessible name as a constructor argument so one class serves every instance.
5. Export it from `proof/components/__init__.py`.
<!-- /lang: python -->
<!-- lang: typescript -->
3. Write one class per control in `proof/components/<control>.ts` (dropdown, modal, table, form, tabs, pager, date picker). Take a scoped `Locator` in the constructor; prefer roles, labels and test ids. Never persist snapshot refs such as `e12`.
4. Expose user verbs (`select(option)`, `rows()`), not selectors.
5. Add a focused test beside it, and a row to the inventory in `proof/components/README.md`: component, file, what it wraps. Run `{{TYPECHECK_PROOF}}` and `{{TEST_PROOF}}`.
<!-- /lang: typescript -->
6. Check it by running a scenario that uses it: `{{MOLE}} run <id>`. Try the flow alone first with `{{MOLE}} flow <id>`.
7. Help write the scenario: for each flow, page or check that needs the control, give the import, constructor call and methods to use. Draft the scenario line for the feature map in the format of `{{SKILL_DIR}}/features/README.md`. User words only; no selectors or method names.

Return: components created or changed, the methods they expose, the usage snippets and draft scenario line from step 7, what was verified in the live UI, and every selector that is unverified.

Rules:
- Write only inside `proof/components/`. The parent owns flows, checks, pages, maps and features: report what they should call.
- Components observe and act on one control only. They never judge: no assertions.
- Do not weaken a failing scenario to make the component pass.
