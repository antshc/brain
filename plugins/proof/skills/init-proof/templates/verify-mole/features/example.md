---
feature: example
prove: {{MOLE}} prove --feature example
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

- Prove it: `{{MOLE}} prove --feature example`.
- Look at it: `{{MOLE}} snapshot`<!-- surface: api -->, `{{MOLE}} api get /`<!-- /surface: api -->.

## What usually lies

- A stale build: `{{MOLE}} doctor` says STALE when the source moved past the running app.
