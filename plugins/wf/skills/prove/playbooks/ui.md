# UI

Route procedure for what a page, component, flow or interaction looks like or how it behaves.

## Workflow

1. **Reuse.** Take frontend framework, routing, components, styles, data access and host page from the Frame's Facts; read only gaps. *Done when* the stack and host are cited or a gap is named.
2. **Host.** Prefer an existing route/page; create an experiment route only when no natural host exists. Reuse the current frontend stack and design system. *Done when* the host route is chosen.
3. **Build.** One minimal variant for behavior validation; 2-3 materially different variants when comparing design alternatives, cap 5. Keep existing data fetching/auth when safe; avoid real mutations unless mutation behavior is the claim. Comparing variants → make them switchable on one route, preferably with a shareable `?variant=` parameter; keep the switcher experiment-only and excluded from production. Surface enough real state/data density to evaluate. *Done when* every variant renders.
4. **Observe.** Capture observations and, when provided, the user's selected variant. *Done when* each variant has a recorded observation.

Keep variants/switcher disposable; retain them until caller verification or requested human review finishes. Return control for *Rerun*.

## Constraints

- Variants differ in structure, hierarchy or primary interaction, not only color/copy.
- Do not introduce a new frontend framework.
- Do not over-share layout code when it prevents meaningful variation.
- Subjective preference stays a human judgment; observed behavior and variant comparisons are evidence, not universal proof.
