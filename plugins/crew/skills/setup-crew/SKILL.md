---
name: setup-crew
description: Manual, user-invoked bootstrap that scaffolds the crew's per-Stack convention files (CODE-<stack>.md, VERIFY-<stack>.md, CHORE-<stack>.md) for a user-chosen subset of the shipped Stack roster, plus a single shared GOTCHAS.md, under the resolved Harness Repo Path. Only creates files that don't already exist; never called by Codey or Chorey themselves.
disable-model-invocation: true
---

# Setup Crew

Scaffold the convention/state files Codey and Chorey resolve during INPUT: one `CODE-<stack>.md`/`VERIFY-<stack>.md`/`CHORE-<stack>.md` triad per Stack the user chooses, plus a single shared `GOTCHAS.md`. Run only on explicit human invocation — never inside an autonomous `codey` or `chorey` run.

## Resolve Harness Repo Path

Mirror `codey.agent.md`'s INPUT resolution — never invent a second scheme:

1. `/resolve-harness` available → run it from cwd; retain the emitted `HARNESS_REPO_PATH`.
2. Unavailable or empty value → `HARNESS_REPO_PATH` := cwd.
3. Available but exits non-zero → stop as blocked.

## 1. Present the Stack choice

Read every `codey-<stack>.agent.md` in `<skill-directory>/../../agents` (never the base `codey.agent.md`/`chorey.agent.md`) — the same closed roster `/crew-select` discovers (currently `py`, `dotnet`, `ai`). Present the discovered stack ids as a plain menu and ask the user which one or more to set up. Never auto-detect which Stacks the repository contains from its files — the choice is the user's alone, and no other technology name is ever offered. No selection made → stop; create nothing.

## 2. Create missing per-Stack files

For each chosen stack, skip silently any file below that already exists — never overwrite, merge, or prompt. If missing, copy the matching template from `templates/` (this skill's directory) verbatim, renamed to the target filename. Create `.crew/` if needed.

| File | Target path | Template |
|---|---|---|
| `CODE-<stack>.md` | `$HARNESS_REPO_PATH/.crew/CODE-<stack>.md` | `templates/CODE-<stack>.template.md` |
| `VERIFY-<stack>.md` | `$HARNESS_REPO_PATH/.crew/VERIFY-<stack>.md` | `templates/VERIFY-<stack>.template.md` |
| `CHORE-<stack>.md` | `$HARNESS_REPO_PATH/.crew/CHORE-<stack>.md` | `templates/CHORE-<stack>.template.md` |

A repository already having some of a Stack's files from a prior run is normal: re-running this skill, whether for the same Stack again or an additional one, creates only what's still missing and never touches an existing Stack's files.

## 3. Create the shared GOTCHAS.md

Regardless of how many Stacks were chosen, create exactly one `$HARNESS_REPO_PATH/.crew/GOTCHAS.md` from `templates/GOTCHAS.template.md` when it doesn't already exist yet — same skip-if-exists rule as Step 2. Never one per Stack.

## 4. Extend each newly created file from the repo

Only for files just created in Step 2 (never `GOTCHAS.md`, never a file that already existed), run the `Explore` agent once over `HARNESS_REPO_PATH` and use its findings to extend every section of each new file with this repository's own observed conventions. Ground every line in files `Explore` actually found — never invent a convention or copy one from another repo or Stack. A section with no discoverable convention keeps its placeholder comment.

Each template ships two kinds of content, marked in its own comments:

- **Hazard rules** — Stack-general, safety-relevant defaults (e.g. Python's broad-`except` hazard, .NET's `.csproj` Module boundary). Keep these exactly as shipped, even when `Explore` finds the repository actually does otherwise. Instead, append one line under `## Gotchas` in the shared `GOTCHAS.md` recording the conflict — what the shipped rule says, what the repo actually does — so a future run reads it before touching that Stack's files.
- **Everything else** (style, layer placement, design principles, tests, verify steps, review rules) — a shipped default here is a suggestion only. When `Explore`'s finding differs from it, the repository's convention wins silently: write what `Explore` found and drop the shipped default, no note required.

## Hard rules

- Manual invocation only — never wire this into either agent's INPUT step.
- Never offer or scaffold a Stack outside the roster discovered in Step 1 — a technology with no shipped `codey-<stack>.agent.md` gets no file, ever.
- Never overwrite, merge, or prompt about an existing file.
- Never read from, copy out of, or delete an existing `.droid/` folder, or an unsuffixed `CODE.md`/`VERIFY.md`/`CHORE.md` left by an older scaffold — migration/renaming is a manual human step outside this skill.
- Never create or modify `.harness.env` — read Harness Settings only through the resolver.
- Templates ship Stack-general hazard defaults plus placeholder sections; do not fill either with invented, repo-specific content outside Step 4.

**Emit**: "HARNESS_REPO_PATH=<path> (resolver | fallback cwd). Stacks chosen: [list]. Created: [list]. Skipped (already exist): [list]. Hazard conflicts recorded in GOTCHAS.md: [count or none]. Templates: <plugin-relative dir>."
