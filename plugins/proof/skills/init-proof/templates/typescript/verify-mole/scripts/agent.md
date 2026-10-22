# Authoring and proving scenarios

Read before you add or change a scenario. `{{MOLE}}` runs and records; you write flows, checks and map paragraphs.

1. Read the feature map. Pick the scenarios under their sub-features.
2. Search `proof/components/`, `proof/pages/`, `proof/flows/` and `proof/checks/` before you write anything. Reuse.
3. New or changed browser scenario: explore the app with *Playwright CLI* first (`playwright-cli` skill). Navigate as a user, take accessibility snapshots, confirm stable locators and control behavior, note reusable parts. UI not built yet: read the source, write the expected behavior, mark selectors unverified, invent no observations.
4. Missing reusable control (dropdown, modal, table, form, tab, pager, date picker): run a subagent with [component-extractor.md](component-extractor.md). Pass your CLI observations and the component inventory. Review the files it returns.
5. Persist what you learn as TypeScript: components, page objects, flows, checks, builders in `proof/features/`. Never persist snapshot refs such as `e12`; use roles, labels and test ids.
6. Write the map paragraph, unbulleted: `**(sub-feature-id | scenario-id):** **Given** ...; **When** ...; **Then** .... **Proof:** check (evidence); check (evidence).` Each proof check names its evidence in parentheses; no separate Evidence clause. Flows stay out of Markdown.
7. A proof check observes through `ctx.observe(source, query)` for each source it declares. It never navigates or changes the app. Match narrowly (the chosen product id and quantity), not whole-payload equality. Assert browser errors only when they affect completion. Read a database only when no public API shows the result.
8. Run `{{MOLE}} doctor`, then `{{MOLE}} run <scenario>`. Failing step, missing element, navigation or `{{MOLE}}` error: use *Playwright CLI* to look, compare with the receipt, repair the flow or check. Never weaken an acceptance rule to pass.
9. Run again through `{{MOLE}}` in a fresh context and revision. CLI observations never produce PASS and never replace the mole's evidence. Report only a current, complete, evidenced PASS.
10. The same check fails twice after repairs: return the receipt and ask a human.

Verdicts: PASS = checks held and each declared source left an artifact. FAIL = the observed behavior violates the requirement. ERROR = the proof could not be made (environment, collector, missing evidence). STALE = the source moved mid-run. NOT_REACHED = an earlier step stopped the scenario. A screenshot is never proof on its own.
