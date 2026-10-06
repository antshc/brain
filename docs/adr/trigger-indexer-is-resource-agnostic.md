# Trigger-indexer is resource-agnostic

`trigger-indexer` carries no hardcoded knowledge of which file, section, record type, directory, or column set it operates on. The caller supplies table metadata (including the Trigger condition column and row locator rules) and row metadata (including explicit cell values) at skill-invoke time. This lets Service, ADR, Concept, and custom tables reuse trigger generation, semantic **Scan and match**, and **Keeping the indexes in sync** without a skill change, while preserving columns the caller did not name.

## Considered Options

- **Hardcode an architecture file, Concepts/ADR sections, record directories, or a Summary column into the skill** (status quo before this decision) — rejected: a new indexed record type or table shape would require editing `trigger-indexer` instead of passing different metadata, and callers could not preserve columns outside the assumed schema.
