# Trigger-indexer is resource-agnostic

`trigger-indexer` carries no hardcoded knowledge of which file, section, or record directory it operates on. `{{indexFile}}`, `{{indexSection}}`, and (for sync) `{{recordDirectory}}`/`{{recordPath}}` are always supplied by the caller in context at skill-invoke time — never assumed to be `ARCHITECTURE.md`'s `Crosscutting Concepts`/`Architecture Decision Records` sections or `docs/concepts/`/`docs/adr/`. This lets any future indexed record type (e.g. a Building-block service index) reuse the same **Scan and match** and **Keeping the indexes in sync** actions without a skill change — only Concepts/ADRs appear in the skill's prose as parenthetical examples, never as the primary instruction.

## Considered Options

- **Hardcode `ARCHITECTURE.md`, the Concepts/ADR sections, and `docs/concepts/`/`docs/adr/` into the skill** (status quo before this decision) — rejected: a new indexed record type (e.g. a service index) would require editing `trigger-indexer` itself instead of just passing different context, and the prose read as Concepts/ADR-specific even though the mechanics are generic.
