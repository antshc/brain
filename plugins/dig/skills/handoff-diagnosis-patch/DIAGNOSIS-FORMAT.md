<!-- @: {{title}} = one line naming the symptom and the proven behavior; prefix ticket id when one exists -->
# {{title}}

Self-contained bundle to re-apply, re-run, and re-summarize {{diagnosis|one sentence: what was broken and what proves it}}. Written so an agent with **no memory of the original session** can replay it from this folder alone.

- Root cause: [root-cause.md](root-cause.md)
- Investigation log: [diagnosis-log.md](diagnosis-log.md)
- Patch: {{[{{slug}}.patch]({{slug}}.patch), or "none — repro needs no code changes"}}
- Repository: `{{git remote get-url origin, credentials stripped}}`, base commit `{{baseCommit}}`

## Matching signals

<!-- @: verbatim strings a future root-cause run would grep for; one bullet per signal; never paraphrase error text -->
- Symptom: {{user-visible symptom, short}}
- Error text: `{{verbatim error, exception type, or log line}}`
- Components: {{modules, services, classes involved}}
- Paths: `{{path}}`
- Environment: {{runtime, config, data shape, version the bug needs}}

## What the patch changes

<!-- @: one row per file in the patch; omit section when there is no patch -->
| File | Kind | Change |
|---|---|---|
| `{{path}}` | harness \| fixture \| trace \| instrumentation \| test | {{what it adds and why}} |

## Scenario

<!-- @: one Scenario per proven behavior, phrased against the real interface; unexercised capability → title says "not yet exercised" -->
```gherkin
Feature: {{behavior under test, not the ticket id}}
  {{1-3 lines: what was reported, what the root cause is, what this scenario proves}}

  Background:
    Given {{shared preconditions}}

  Scenario: {{names the proven behavior, not the mechanism}}
    When {{action against the real interface}}
    Then {{observable, checkable outcome}}
```

## How to replay

<!-- @: every command MUST have been run in the original session with its real output recorded; mark anything else "untested" -->
All commands run from the repository root unless noted.

### 1. Apply the patch

<!-- @: omit when there is no patch -->
```bash
git status --short          # tree clean, or not touching the files above
git apply --check patches/{{slug}}/{{slug}}.patch
git apply patches/{{slug}}/{{slug}}.patch
```

### 2. Set up

```bash
{{Setup commands from the log — env var names only, never values}}
```

### 3. Run the loop

```bash
{{the red-capable loop command}}
```

Expected: `{{exact redacted red output line observed}}`.

A different result is itself a finding — capture the exact output; the code path changed since this bundle was written.

### 4. Produce a new summary

1. State whether the loop still goes red, with the exact output line.
2. State whether it still confirms the root cause in [root-cause.md](root-cause.md) — or, if not, what changed.
3. If the fix has landed, state whether the loop now goes green and which regression test locks it: `{{test name or "no seam — see log"}}`.
4. Note any open question from the log that new evidence narrows.

## Possible follow-up

<!-- @: unexercised capabilities, missing seams, architectural recommendations; omit section if none -->
- {{item}}
