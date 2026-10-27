---
name: write-skill
description: Write or rewrite an agent skill from a brief or request using bundled best practices, then shrink it; or only shrink an existing file.
disable-model-invocation: true
---

# Write Skill

Own skill authoring end to end: the draft phase writes, the shrink phase tightens. Each phase runs in its own fresh subagent and follows its procedure file. This file owns mode selection, delegation, and the final check.

## Mode

- **Shrink mode** — request is to shrink, tighten, compress, or condense existing file(s): run Shrink phase only.
- **Write mode** — everything else (skill brief from `grill-skill`, free-text request, rewrite of an existing skill): run Draft phase, then Shrink phase.

## Constraints

- **MUST** run each phase in a separate fresh subagent; the parent never drafts or shrinks inline. Rationale: isolated context keeps the shrink pass independent and stops the draft rushing toward later phases. If subagents are unavailable, stop and report the blocker.
- Pass the user input verbatim; restate nothing from the procedure files in prompts.
- Pass absolute paths of this skill's `references/` and `templates/` files, resolved from this skill's base directory.

## Workflow

1. **Resolve.** Select mode. Write mode: take the brief or request and any target path. Shrink mode: collect the file paths. *Done when* mode and inputs are known; ask only when no target can be derived from input or repository layout.
2. **Draft phase** (write mode). Launch a fresh subagent instructed to read and follow `references/draft.md`, given the input verbatim, the target path, and absolute paths of `references/draft.md`, `references/best-practices.md`, `references/wording.md`, and `templates/SKILL.template.md`. It returns per draft.md Return. *Done when* every returned path exists on disk.
3. **Shrink phase.** Launch a new fresh subagent instructed to read and follow `references/shrink.md` on the drafted paths (write mode) or given paths (shrink mode), given absolute paths of `references/shrink.md`, `references/wording.md`, and `references/best-practices.md`. It returns per shrink.md Return. *Done when* the report lists every file with before → after counts.
4. **Final check.** Read the result files. Confirm Completion criteria; fix a failing item by re-running the owning phase with the defect named. *Done when* all criteria hold or a remaining defect is reported.
5. **Report.** Return paths, mode, blocks and invocation mode (write mode), assumptions, shrink deltas, flagged items.

## Completion criteria

- Every target `SKILL.md` has valid frontmatter: `name` matches folder; description passes the forbidden description character table in best-practices.md.
- `SKILL.md` body under 300 lines; no template placeholder or `<!-- @: -->` directive left in a produced skill.
- Every relative link resolves inside its own skill folder.
- Shrink report shows no unflagged lost behavior item.
- New plugin, when created, is registered alongside its siblings.
