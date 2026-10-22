# Feature maps

One map per feature in `proof/features/`. A map says, per scenario, what is given, what the user does, what must be true and what proves it. It never holds selectors, routes or wire details: those live in pages, components and flows. `{{TEST_PROOF}}` fails when a map and the registry drift apart.

| Feature | Surfaces | Map | Run |
|---|---|---|---|
| example | {{SURFACES_TEXT}} | [example.md](example.md) | `{{MOLE}} run example` |

Open only the maps for the features your files touch: `{{MOLE}} features --changed`.
