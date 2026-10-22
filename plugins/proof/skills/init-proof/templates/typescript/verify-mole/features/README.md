# Feature maps

One map per feature in `proof/features/`. A map states what a user does and what proves it, never selectors, routes or wire details: those live in page objects and evidence adapters. `{{TEST_PROOF}}` fails when a map and the builders drift apart.

## Format

Four `##` sections, in this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with Mole`, `Gotchas`.

- `Sub-features`: one bullet per sub-feature: ``- `id` — description``.
- `Driving it with Mole`: one unbulleted paragraph per scenario, starting `**(sub-feature-id | scenario-id):**`, then `**Given** ...; **When** ...; **Then** .... **Proof:** check (evidence); check (evidence).`
- Every proof check names its evidence in parentheses: `DOM assertion`, `API response`, `Screenshot`, `Network`, `Console`, `Storage`, or a project adapter. No separate Evidence clause; no pipes between clauses.
- The n-th proof check is the n-th `.proof()` of the scenario's builder, with exactly that evidence. A screenshot needs an assertive source beside it.
- Flows stay in TypeScript.

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

## Features

| Feature | Surfaces | Map | Run |
|---|---|---|---|
| example | {{SURFACES_TEXT}} | [example.md](example.md) | `{{MOLE}} run example` |

Open only the maps for the features your files touch: `{{MOLE}} features --changed`.
