---
feature: example
prove: pnpm mole prove --feature example
touches:
  - src/
surfaces:
{{SURFACES_YAML}}
---

# example (placeholder)

A smoke check that the app answers on each surface. Replace it with real features, or keep it as the first gate.

## Contract

- The app answers on every surface listed above; an answer below the failure range counts.

## Driving it

- Prove it: `pnpm mole prove --feature example`.
- Look at it: `pnpm mole snapshot`<!-- surface: api -->, `pnpm mole api get /`<!-- /surface: api -->.

## What usually lies

- A stale build: `pnpm mole doctor` says STALE when the source moved past the running app.
