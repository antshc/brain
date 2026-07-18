# File structure

Read this once, when setting up the domain-model files for a repo that doesn't have them yet, or when deciding where a new file belongs.

Repo structure:

```
/
├── ARCHITECTURE.md                      ← also indexes the Crosscutting Concepts
├── CONTEXT.md
├── docs/
│   ├── concepts/                        ← Crosscutting Concepts (backbone rules)
│   │   └── 0001-persisted-domain-model-repository.md
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

Create files lazily — only when you have something to write.

If no `CONTEXT.md` exists, create one when the first term is resolved.

If no `ARCHITECTURE.md` exists, create one when the first term is resolved.

If no `docs/adr/` exists, create it when the first ADR is needed, then add it to the `## Architecture Decision Records` index in `ARCHITECTURE.md`.

If no `docs/concepts/` exists, create it when the first Concept is needed, then add it to the `Crosscutting Concepts` index in `ARCHITECTURE.md`.
