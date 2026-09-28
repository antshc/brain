---
name: crew-memory
description: Repository-local persistent memory for Crew agents. Loads and persists rules from its own Gotchas section, with rule handling supplied by crew-gotchas.
---

# Crew memory

This skill owns its own `## Gotchas` section below. Never pass this file's path to another skill.

## Read Gotchas

Read this file's `## Gotchas` section in full. In a `multi-repo` workspace layout, read only the `### <repo name>` subsection matching cwd's repository; a missing subsection means no rules for that repository. In `single-repo` layout, read the flat rules directly under `## Gotchas`. Pass the resolved rules to `/crew-gotchas`' skill **Read Workflow** as `GOTCHAS RULES`. Pass an empty list when the section or subsection is missing or empty.

## Write Gotchas

Read this file's `## Gotchas` section in full, resolving rules the same way as **Read Gotchas**. Pass them to `/crew-gotchas`' skill **Write Workflow** as `GOTCHAS RULES`. Apply the returned `RULE UPDATES`: extend a matched rule in place or append a new rule, while preserving unrelated rules and every other repository's subsection untouched. In `multi-repo` layout, apply updates within the `### <repo name>` subsection matching cwd's repository, creating that heading (and the `## Gotchas` heading, if missing) before applying updates. In `single-repo` layout, apply updates to the flat list, creating `## Gotchas` when missing. Emit the update result required by `/crew-gotchas`; zero updates leave the file unchanged.

## Gotchas

In `multi-repo` workspace layout, group directives under a `### <repo name>` heading per repository the harness develops, named for that repository's directory name. In `single-repo` layout, skip grouping; this file's directives stay flat under this heading.

<!-- One directive per line. Example: - <directive> -->
