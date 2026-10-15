---
name: bootstrap-docs
description: Creates missing ARCHITECTURE.md and GLOSSARY.md immediately from bundled formats. Use when a caller's existence check finds either absent; leaves section insertion to index-docs and record directories to record-architecture.
---

# Bootstrap Docs

Own the *mechanics* of `ARCHITECTURE.md`/`GLOSSARY.md` existence and creation — nothing else. Bundle the required formats locally; ongoing structural prose and sections belong to `index-docs`, term capture to `record-architecture`.

## Mandatory creation

If `ARCHITECTURE.md` and/or `GLOSSARY.md` don't exist, create them **immediately** — don't wait for a term, structural rule, ADR, Concept, or service to be ready to capture.

- **`ARCHITECTURE.md`** is the system map and ADR/Concept index. Fill in only the required sections (`{{systemName}} Overview`, `Context`) from what's already known about the codebase, using [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md). Leave the optional sections (`Building blocks`, `Deployment View`, `Architecture Decision Records`, `Crosscutting Concepts`) out until there's content for them — `index-docs` adds those via *Ensure section exists*.
- **`GLOSSARY.md`** is the glossary every other document assumes as shared vocabulary. Create it with its `{{contextName}}` heading and an empty `Language` section, using [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md) — leave individual terms out. Once a term resolves, *run `record-architecture` skill in `term` mode to record settled architecture glossary terms*.

These two are the only non-lazy documents. `docs/adr/`, `docs/concepts/`, and `docs/building-blocks/` are created lazily by the skill that writes into each.
