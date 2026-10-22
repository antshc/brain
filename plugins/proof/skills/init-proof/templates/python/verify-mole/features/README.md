# Feature maps

One map per feature in `proof/features/`. A map says, per scenario, what is given, what the user does, what must be true and what proves it. It never holds selectors, routes or wire details: those live in pages, components and flows. `{{TEST_PROOF}}` fails when a map and the registry drift apart.

## Baseline preconditions

TODO(proof): how the app starts for a proof (URL, env vars, data directory, seed data, auth) and what `{{MOLE}} doctor` must show. Never drive an instance this run did not start.

## Driving conventions

- Prefer ARIA roles and accessible names over CSS selectors or DOM position.
- Start every scenario from the baseline state unless its Given says otherwise. Restore seeded data after a mutation.
- Run `{{MOLE}} flow <id>` to look, `{{MOLE}} run <id>` to prove.

## Proof and skip reporting

- A check passes only on the evidence it cites, captured for it and kept in `proof/.runs/mole/`.
- Report an unreachable path with the attempted command and the unmet precondition. Never report a skipped entry point as verified through another path.
- Evidence survives cleanup.

## Feature entry contract

Each map starts with an H1 and one paragraph on the user-visible behavior, then four H2s in order: `Sub-features`, `How to get to it (user POV)`, `Driving it with Mole`, `Gotchas`. Keep selectors, routes and wire details out: only user paths, required state and observable proof.

## Features

| Feature | Surfaces | Map | Run |
|---|---|---|---|
| example | {{SURFACES_TEXT}} | [example.md](example.md) | `{{MOLE}} run example` |

Open only the maps for the features your files touch: `{{MOLE}} features --changed`.
