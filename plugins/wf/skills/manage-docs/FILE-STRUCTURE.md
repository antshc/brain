# File structure

Read this once, when setting up the domain-model files for a repo that doesn't have them yet, or when deciding where a new file belongs.

Most repos have a single context:

```
/
├── ARCHITECTURE.md                      ← also indexes the Solution Strategy (SSRs)
├── CONTEXT.md
├── docs/
│   ├── ssr/                             ← Solution Strategy Records (backbone rules)
│   │   └── 0001-persisted-domain-model-repository.md
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `CONTEXT-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── ARCHITECTURE.md
├── CONTEXT-MAP.md
├── docs/
│   ├── ssr/                             ← Solution Strategy Records (backbone rules)
│   │   └── 0001-persisted-domain-model-repository.md
│   └── adr/                          ← system-wide ADRs (docs/ssr/ holds system-wide SSRs)
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when you have something to write.

If no `CONTEXT.md` exists, create one when the first term is resolved.

If no `ARCHITECTURE.md` exists, create one when the first term is resolved.

If no `docs/adr/` exists, create it when the first ADR is needed, then add it to the `## Architecture Decision Records` index in `ARCHITECTURE.md`.

If no `docs/ssr/` exists, create it when the first SSR is needed, then add it to the `## Solution Strategy` index in `ARCHITECTURE.md`.
