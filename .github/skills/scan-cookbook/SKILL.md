---
name: scan-cookbook
description: Scans any repository's AI agent skills, instructions, and guidance for reusable principles. Creates or updates a cookbook index, checks recipe coverage, and links each covered principle to its recipe or each missing recipe to source evidence.
---

# Scan Cookbook

Scan the **target repository**, not this skill's installation repository. Default target: current Git repository. Default cookbook: `docs/cookbook/`. Use a user-specified target or cookbook path when provided. Create the cookbook and `index.md` if missing.

Copy this checklist and check off items as you complete them:

```md
Scan Cookbook Progress:
- [ ] 1. Inventory sources and recipes
- [ ] 2. Extract principles
- [ ] 3. Match recipe coverage
- [ ] 4. Update index
- [ ] 5. Verify index
```

## 1. Inventory sources and recipes

Run `git rev-parse --show-toplevel` from the target directory. From that root, run `git ls-files --cached --others --exclude-standard` to list tracked and untracked non-ignored files.

Discover active agent guidance wherever it lives: `SKILL.md`, `*.agent.md`, `*.instructions.md`, `AGENTS.md`, and relevant concept, ADR, architecture, and policy documents. Include nested skill and plugin directories. Ignore any `_backup/` or `_in-progress/` directory, generated/vendor files, and retired guidance.

Read existing `<cookbook>/index.md` and every cookbook recipe. If absent, use an empty index or recipe inventory. A cookbook recipe is a coverage target, not source evidence.

*Done when:* Target root, relevant source inventory, existing entries, and available recipes are known.

## 2. Extract principles

Read relevant source files. Extract reusable **AI agent practices** backed by an explicit instruction, constraint, or procedure. Exclude project-specific implementation rules, isolated commands, and generic advice without actionable behavior.

Merge synonyms and duplicate observations; keep independently applicable principles separate. For each principle, retain its current source path. Recheck existing index entries against the current sources. Remove entries with no active source; never keep them only because they appeared in the old index.

*Done when:* Each distinct principle has current evidence and no duplicates remain.

## 3. Match recipe coverage

Read each candidate recipe, not its title alone. A recipe covers a principle only when its **AI Instructions** give actionable commands for that principle. A mention, matching title, or source document does not count. One recipe may cover multiple principles.

- Covered: `- [x] **Principle** — [recipe](relative-recipe-path.md)`
- Missing recipe: `- [ ] **Principle** — [source](relative-source-path.md)`

For previously checked entries, uncheck them if the recipe is missing or no longer covers the principle. Link uncovered principles to their current evidence. Do not create recipes or mark coverage speculatively.

*Done when:* Every principle has an evidence-based status and a destination path.

## 4. Update index

Create or update `<cookbook>/index.md`. Preserve useful existing thematic headings; group new principles under fitting headings. For a new index, use:

```md
# Cookbook Principle Index

- [x] — A cookbook recipe covers the principle; link the recipe.
- [ ] — The principle exists in repository guidance but has no recipe; link its source.

## Principles

- [ ] **Example principle** — [source](../path/to/source.md)
```

Replace the sample entry with actual discoveries. Use relative links from `index.md`. Keep exactly one checkbox per principle and retain entries with valid source evidence. Do not change source files or existing recipes.

*Done when:* The index contains all discovered principles with the correct checkboxes and links.

## 5. Verify index

Re-read the index and check that every checkbox has evidence: `[x]` links to an existing recipe with actionable instructions; `[ ]` links to an existing source. Verify relative paths, unique principles, and coverage of every extracted obligation. Correct mismatches.

Report the index path, total principles, covered count, uncovered count, and any scan limitations. Never claim a complete scan of unread sources.

*Done when:* All index entries and links are valid, with no unsupported checked entries.
