# Authoring scenarios

Read before you add or change a scenario, flow, check, page or component in `proof/`. `{{MOLE}}` runs and records; you write the flows, checks and map lines. Run the rules in order.

1. **Read the map and search first.** Open the feature's map in [{{SKILL_DIR}}/features/](../{{SKILL_DIR}}/features/README.md), then search `proof/components/`, `proof/pages/`, `proof/flows/` and `proof/checks/` for what you need. Reuse before you create.
2. **Explore the live UI before new or changed browser flows.** Use Playwright CLI on the running app (`playwright-cli` skill): open the page, take an accessibility snapshot, perform the user path, confirm stable locators and control behavior. No GUI available or UI not built yet: read the source, write the expected behavior, mark every selector you could not verify as unverified in your report, and invent no observations.
3. **Missing control?** Launch a new subagent session whose prompt is the body of [{{SKILL_DIR}}/references/component-extractor.md](../{{SKILL_DIR}}/references/component-extractor.md) (dropdown, modal, table, form, tabs, pagination, date picker), with the inputs it lists appended: the control, the feature and page, your Playwright CLI observations and the `proof/components/` inventory. Review the components and the scenario draft it returns. Do not write the control's selectors into a flow or a check.
<!-- lang: python -->
4. **Persist in Python.** Page Objects in `proof/pages/`, controls in `proof/components/`, user journeys as `@flow("id")` in `proof/flows/`, observations as `ProofCheck` in `proof/checks/`, composed with the builder in `proof/features/<feature>.py`. Never write a Playwright CLI snapshot ref such as `e12` into code: use role and accessible name.
<!-- /lang: python -->
<!-- lang: typescript -->
4. **Persist in TypeScript.** Components in `proof/components/`, page objects in `proof/pages/`, flows in `proof/flows/`, checks in `proof/checks/`, composed with `defineFeature` in `proof/features/<feature>.ts`. Never write a Playwright CLI snapshot ref such as `e12` into code: use roles, labels and test ids.
<!-- /lang: typescript -->
5. **Flows act, checks observe.** A flow never judges. A check never navigates or changes state. Every check lists the evidence that proves it<!-- lang: typescript -->, and observes through `ctx.observe(source, query)` for each source it declares<!-- /lang: typescript -->; the runner captures that evidence for the check and keeps it. Match narrowly (the chosen product id and quantity), not whole-payload equality. Assert browser errors only when they affect completion. Read a database only when no public API shows the result.
<!-- lang: python -->
6. **Keep the map in step.** One scenario line per scenario under "Driving it with Mole": `**(sub-feature | scenario):** **Given** ...; **When** ...; **Then** ...; **Proof** check (Evidence label), check (Label + Label).` The evidence in parentheses is exactly what the check declares. No selectors, no method names. Then run `{{TEST_PROOF}}`.
<!-- /lang: python -->
<!-- lang: typescript -->
6. **Keep the map in step.** One unbulleted paragraph per scenario under "Driving it with Mole": `**(sub-feature-id | scenario-id):** **Given** ...; **When** ...; **Then** .... **Proof:** check (evidence); check (evidence).` Each proof check names its evidence in parentheses; the n-th check is the n-th `.proof()` of the builder. No selectors, no method names; flows stay out of Markdown. Then run `{{TEST_PROOF}}`.
<!-- /lang: typescript -->
7. **Check the environment, then run.** `{{MOLE}} doctor`, then `{{MOLE}} run <id>`. Try a flow alone first with `{{MOLE}} flow <id>`. A step fails on a control: launch the component extractor subagent again with the scenario id and its receipt.
8. **Troubleshoot without weakening the rules.** Playwright CLI helps you see why a step fails. Fix the flow, page or component. Never loosen a check, drop its evidence or skip a step to get a PASS. Playwright CLI observations never produce PASS: only the receipt does.
9. **Re-prove on a fresh revision.** After any edit to the app or the proof code, restart the app if it changed, then run again. An old receipt proves nothing.
10. **Stop after two failed repairs of one check.** Hand a human the receipt and what you tried.

Verdicts: PASS = checks held and each declared source left an artifact. FAIL = the observed behavior violates the requirement. ERROR = the proof could not be made (environment, collector, missing evidence). STALE = the source moved mid-run. NOT_REACHED = an earlier step stopped the scenario. A screenshot is never proof on its own.
