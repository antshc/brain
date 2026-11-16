# UI

Route procedure for falsifiable page, component, flow, appearance or interaction claims. Subjective layout preference belongs to Design.

## Workflow

1. **Reuse.** Take frontend framework, routing, components, styles, data access and host page from the Frame's Facts; read only gaps. *Done when* the stack and host are cited or a gap is named.
2. **Select.** Prefer existing focused GUI E2E tests against the relevant route/page. No suitable test → build the smallest browser scenario using the current frontend stack, design system and test tooling; create an experiment route only when no natural host exists. Keep existing data fetching/auth when safe and use realistic deciding state. *Done when* the browser scenario, target and assertions are identified, or a blocker is recorded.
3. **Run.** Launch or connect to the scoped app, drive the relevant browser interaction and assert the claim's expected DOM, navigation, network, accessibility or visual result. Appearance claims require an explicit observable criterion and captured browser rendering. A prototype must run in the browser; source, build output or generated screenshots without the deciding execution are insufficient. *Done when* the scenario actually executed and deciding assertions/results are captured.
4. **Capture.** Record launch/test commands, URL, browser/version, viewport, fixtures, actions, expected/actual results and screenshots/traces when relevant. Distinguish a prototype's behavior from the existing app. *Done when* the deciding browser scenario can be rerun from the record.

Keep new scenarios and experiment routes disposable; retain them until caller verification or requested follow-up finishes. Return control for *Rerun*.

## Constraints

- Do not introduce a new frontend framework.
- Exercise the relevant UI flow; API-only success cannot establish GUI behavior.
- Avoid real mutations unless mutation behavior is the claim and the target is authorized.
- Unavailable app/browser/access → blocked; an executed scenario without deciding evidence → inconclusive.
- Subjective preference stays a human judgment; selecting a variant is not proof.
