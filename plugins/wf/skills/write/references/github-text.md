# GitHub text: PR descriptions, commit messages, and review comments

The caller's format reference owns structure, required sections, subjects, and markers. This file owns prose only.

## Shared rules

- Write in the present tense and active voice. Name who does what: "the retry loop caps the delay", not "the delay is capped".
- Put symbols, paths, flags, and commands in code font.
- Write a briefing a reviewer can read in under a minute.
- Link swarm logs, SHA lists, and metric tables. Do not paste them.
- Put code, commands, and output in fenced code blocks. Write real paths and symbol names.
- Make every count or tree claim true at the commit that lands it, and include the command that regenerates it.

## PR description

- Open each section with its point. Keep the rationale in Why and the change in What changed.
- Report checks as run and observed, not as intended.

## Commit message body

- Leave the subject unchanged. Edit only the body and preserve footers.
- Explain why the change was made. The diff already shows what changed.

## Review comment

- Keep the comment short and peer to peer. The caller's review-comment format owns tone, structure, and hidden metadata.
- State the concern and its concrete effect before any suggestion.

## Worked example

Before:

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
