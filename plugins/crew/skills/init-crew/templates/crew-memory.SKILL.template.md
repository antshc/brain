---
name: crew-memory
description: Repository-local persistent memory for Crew agents. Loads rules from the sibling GOTCHAS.md and persists rule updates produced by crew-gotchas.
---

# Crew memory

This skill owns its sibling `GOTCHAS.md`. Never pass its path to another skill.

## Read Gotchas

Read the sibling `GOTCHAS.md` in full. Pass the rules under `## Gotchas` to `/crew-gotchas`' skill **Read Workflow** as `GOTCHAS RULES`. Pass an empty list when the file or section is missing.

## Write Gotchas

Read the sibling `GOTCHAS.md` in full. Pass its rules under `## Gotchas` to `/crew-gotchas`' skill **Write Workflow** as `GOTCHAS RULES`. Apply the returned `RULE UPDATES` to the same sibling file: extend a matched rule in place or append a new rule under `## Gotchas`, while preserving its heading, comments, and unrelated rules. If the file is missing, create it with a `# GOTCHAS` heading and a `## Gotchas` section before applying updates. Emit the update result required by `/crew-gotchas`; zero updates leave the file unchanged.
