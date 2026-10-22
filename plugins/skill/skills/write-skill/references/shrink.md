# Shrink phase

Make agent-facing files shorter and more consistent while preserving every behavior. Apply [wording.md](wording.md); keep frontmatter valid per Frontmatter and description in [best-practices.md](best-practices.md).

## Inputs

- **Files** — paths to `SKILL.md`, its bundled references/templates, `*.agent.md`, or instructions files.

## Constraints

- **MUST** preserve every behavior: rules, steps, order, constraints, MUST/MUST NOT guardrails, failure behaviors, pointers and their conditions, skill invocations, completion criteria, output contract.
- Keep code blocks, commands, paths, identifiers, placeholders, template directives, and frontmatter keys literal.
- Change meaning only to merge duplicates; add no new rules.

## Steps

1. **Inventory.** Number every behavior item per file. *Done when* every sentence maps to an item or is marked no-op or duplicate candidate.
2. **Rewrite.** Go sentence by sentence: rule first, imperative active voice, terse, positive phrasing, normative MUST only for hard rules, consistent terms, one physical line per paragraph. *Done when* every sentence was visited.
3. **Collapse.** Merge duplicate meanings into the authoritative place, replace repeated triads or gestures with leading words, co-locate scattered rules. *Done when* each meaning appears once per skill.
4. **Prune.** Delete whole sentences failing the No-op test and lines without relevance. *Done when* every remaining sentence changes behavior.
5. **Re-verify.** Map the inventory 1:1 against the result; restore any lost item. Check description characters, name matches folder, links resolve, `SKILL.md` body under 300 lines. *Done when* every inventory item is present and checks pass.

## Return

- Modified file paths (absolute).
- Lines and words before → after per file.
- Merged or deleted items, each with reason (duplicate, no-op, irrelevant).
- Any item whose preservation is uncertain, flagged for review.
