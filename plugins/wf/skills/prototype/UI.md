# UI Prototype

Use when the question is what a page, component, flow, or interaction should look or feel like.

## Build

1. Inspect the existing frontend framework, routing, components, styles, data access, and host page.
2. Prefer an existing route/page. Create a prototype route only when no natural host exists.
3. Reuse the current frontend stack and design system.
4. Build 3 structurally different variants by default; cap at 5.
5. Keep existing data fetching/auth when safe. Avoid real mutations unless mutation behavior is the question.
6. Make variants switchable on one route, preferably with a shareable URL parameter such as `?variant=`.
7. Keep the switcher clearly prototype-only and excluded from production.
8. Surface enough real state/data density to evaluate the variants.
9. Capture the selected design decision; remove prototype variants/switcher from production code.

## Constraints

- Variants must differ in structure, hierarchy, or primary interaction, not only color/copy.
- Do not introduce a new frontend framework.
- Do not over-share layout code when it prevents meaningful variation.
