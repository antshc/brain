# Feature maps

One map per feature in `proof/features/`. A map says, per scenario, what is given, what the user does, what must be true and what proves it. It never holds selectors, routes or wire details: those live in <!-- lang: python -->pages, components and flows<!-- /lang: python --><!-- lang: typescript -->page objects, components and evidence adapters<!-- /lang: typescript -->. `{{TEST_PROOF}}` fails when a map and the <!-- lang: python -->registry<!-- /lang: python --><!-- lang: typescript -->builders<!-- /lang: typescript --> drift apart.

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
<!-- lang: python -->

- `Driving it with Mole`: one line per scenario: `**(sub-feature | scenario):** **Given** ...; **When** ...; **Then** ...; **Proof** check (Evidence label), check (Label + Label).` The evidence in parentheses is exactly what the check declares.
<!-- /lang: python -->
<!-- lang: typescript -->

- `Sub-features`: one bullet per sub-feature: ``- `id` — description``.
- `Driving it with Mole`: one unbulleted paragraph per scenario, starting `**(sub-feature-id | scenario-id):**`, then `**Given** ...; **When** ...; **Then** .... **Proof:** check (evidence); check (evidence).`
- Every proof check names its evidence in parentheses: `DOM assertion`, `API response`, `Screenshot`, `Network`, `Console`, `Storage`, or a project adapter. No separate Evidence clause; no pipes between clauses.
- The n-th proof check is the n-th `.proof()` of the scenario's builder, with exactly that evidence. A screenshot needs an assertive source beside it.
- Flows stay in TypeScript.
<!-- /lang: typescript -->

## Features

| Feature | Surfaces | Map | Run |
|---|---|---|---|
| example | {{SURFACES_TEXT}} | [example.md](example.md) | `{{MOLE}} run example` |

Open only the maps for the features your files touch: `{{MOLE}} features --changed`.
