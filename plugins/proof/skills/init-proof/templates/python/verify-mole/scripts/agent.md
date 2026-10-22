# Authoring scenarios

Read before you add or change a scenario, flow, check, page or component in `proof/`. Run the rules in order.

1. **Read the map and search first.** Open the feature's map, then search `proof/components/`, `proof/pages/`, `proof/flows/` and `proof/checks/` for what you need. Reuse before you create.
2. **Explore the live UI before new or changed browser flows.** Use Playwright CLI on the running app: open the page, take a snapshot, perform the user path. No GUI available: read the source, and mark every selector you could not verify as unverified in your report.
3. **Missing control?** Run a new subagent session with [component-extractor.md](component-extractor.md) (dropdown, modal, table, form, tabs, pagination, date picker). Pass the control, the feature and page, your Playwright CLI observations and the `proof/components/` inventory. Review the components and the scenario draft it returns. Do not write the control's selectors into a flow or a check.
4. **Persist in Python.** Page Objects in `proof/pages/`, controls in `proof/components/`, user journeys as `@flow("id")` in `proof/flows/`, observations as `ProofCheck` in `proof/checks/`, composed with the builder in `proof/features/<feature>.py`. Never write a Playwright CLI snapshot ref such as `e12` into code: use role and accessible name.
5. **Flows act, checks observe.** A flow never judges. A check never navigates or changes state. Every check lists the evidence that proves it; the runner captures that evidence for the check and keeps it.
6. **Keep the map in step.** One scenario line per scenario under "Driving it with Mole": `(sub-feature | scenario): **Given** ...; **When** ...; **Then** ...; **Proof** check (Evidence label), check (Label + Label).` The evidence in parentheses is exactly what the check declares. No selectors, no method names. Then run `{{TEST_PROOF}}`.
7. **Check the environment, then run.** `{{MOLE}} doctor`, then `{{MOLE}} run <id>`. Try a flow alone first with `{{MOLE}} flow <id>`. A step fails on a control: run the component extractor subagent again with the scenario id and its receipt.
8. **Troubleshoot without weakening the rules.** Playwright CLI helps you see why a step fails. Fix the flow, page or component. Never loosen a check, drop its evidence or skip a step to get a PASS. Playwright CLI observations never produce PASS: only the receipt does.
9. **Re-prove on a fresh revision.** After any edit to the app or the proof code, restart the app if it changed, then run again. An old receipt proves nothing.
10. **Stop after two failed repairs of one check.** Hand a human the receipt and what you tried.
