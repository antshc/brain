---
name: crew-memory
description: Repository-local persistent memory for Crew agents. Loads and persists rules from its own Gotchas section, with rule handling supplied by crew-gotchas.
---

# Crew memory

This skill owns its own `## Gotchas` section below. Never pass this file's path to another skill.

## Read Gotchas

Read this file's `## Gotchas` section in full. Pass its rules to `/crew-gotchas`' skill **Read Workflow** as `GOTCHAS RULES`. Pass an empty list when the section is missing or empty.

## Write Gotchas

Read this file's `## Gotchas` section in full. Pass its rules to `/crew-gotchas`' skill **Write Workflow** as `GOTCHAS RULES`. Apply the returned `RULE UPDATES` to that section: extend a matched rule in place or append a new rule, while preserving unrelated rules. If the section is missing, create a `## Gotchas` heading before applying updates. Emit the update result required by `/crew-gotchas`; zero updates leave the file unchanged.

## Gotchas

<!-- One directive per line. Example: - <directive> -->
