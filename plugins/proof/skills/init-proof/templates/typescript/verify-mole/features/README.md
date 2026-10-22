# Feature maps

One map per feature in `proof/features/`. A map states what a user does and what proves it, never selectors, routes or wire details: those live in page objects and evidence adapters. `{{TEST_PROOF}}` fails when a map and the builders drift apart.

## Format

Four `##` sections, in this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with Mole`, `Gotchas`.

- `Sub-features`: one bullet per sub-feature: ``- `id` — description``.
- `Driving it with Mole`: one unbulleted paragraph per scenario, starting `**(sub-feature-id | scenario-id):**`, then `**Given** ...; **When** ...; **Then** .... **Proof:** check (evidence); check (evidence).`
- Every proof check names its evidence in parentheses: `DOM assertion`, `API response`, `Screenshot`, `Network`, `Console`, `Storage`, or a project adapter. No separate Evidence clause; no pipes between clauses.
- The n-th proof check is the n-th `.proof()` of the scenario's builder, with exactly that evidence. A screenshot needs an assertive source beside it.
- Flows stay in TypeScript.

| Feature | Surfaces | Map | Run |
|---|---|---|---|
| example | {{SURFACES_TEXT}} | [example.md](example.md) | `{{MOLE}} run example` |

Open only the maps for the features your files touch: `{{MOLE}} features --changed`.
