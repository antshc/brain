# Feature maps

One map per feature in `proof/features/`. A map states the behavior contract and how to drive it, never selectors, routes or wire details: those live in the surface adapters. `{{TEST_PROOF}}` fails when a map and the registry drift apart.

| Feature | Surfaces | Map | Prove |
|---|---|---|---|
| example | {{SURFACES_TEXT}} | [example.md](example.md) | `{{MOLE}} prove --feature example` |

Open only the maps for the features your files touch: `{{MOLE}} features --changed`.
