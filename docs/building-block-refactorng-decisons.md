
## Implementation Decisions

- Retain arc42's Building Block View as the architecture method and use Mermaid C4 notation for its representations: `C4Context` for system context, `C4Container` for deployable building blocks, and optional `C4Component` detail within a deployable record.
- Make `ARCHITECTURE.md` a terse retrieval index. Its Context section links the glossary and `system-context`, `Container` diagrams; its Building blocks section uses `Building block | Trigger condition | Summary` rows; it contains no diagrams, interaction diagram, or source tree.
- Store one required building-block record per deployable under `docs/building-blocks/<slug>.md`. The record owns cross cutting concepts, responsibility, dependencies,  interfaces, repository/source paths, detailed codebase structure, its container view, and optional component view.
- ARCHITECTURE.md has a reference to multi repo codebase lookup index in `*-codebase-index.md` (/home/pet/_projects/afk/brain/plugins/wf/skills/explore-codebase/CODEBASE-INDEX-FORMAT.md) the -codebase-index.md.
- Extend deployment documentation with external dependencies covering managed services, registries, SaaS endpoints, reverse proxies, and runtime platforms.
- Rename `record-service` to `record-building-block`, update all callers and references, and provide no compatibility alias.
- Update the reusable `index-docs`, `record-building-block`, `record-deployment-view`, and `research-system` contracts and their owned templates. Also update reusable callers and public reference documentation that name the old skill or schema.
- Keep root project architecture documents and the ZIC research example unchanged; they are examples and migration targets for a separate project repository.