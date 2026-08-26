---
name: address-review-discussions
description: Address the review discussion on a pull request — group its comments into issues, investigate each against the code, fix what needs fixing, and reply to every thread. Use when given a PR URL and asked to handle its review comments.
argument-hint: '<PR URL> (e.g., "https://github.com/owner/repo/pull/1245")'
---

# Address review discussions

**Skill base directory:** the directory holding this `SKILL.md`. Load `references/github-api.md` and `references/investigation.md` from there — never via a bare relative link, which resolves against the runtime CWD.

Parse `{{input}}` into `{{owner}}`, `{{repo}}`, and `{{number}}` from `https://github.com/{{owner}}/{{repo}}/pull/{{number}}`.

## 1. Setup

**Load `references/github-api.md` now.** Every `gh` invocation in this run is copied from it, and nothing below restates one.

- `git status --porcelain` must come back empty. Output means uncommitted work is present → stop and report, leaving the user's work theirs.
- `git remote get-url origin` must point at `{{owner}}/{{repo}}`. A different repo → stop and report.
- Fetch the PR metadata to resolve `$headRef` and `$baseRef`, then `git fetch origin` and check out `$headRef` with `git pull --ff-only`.

Done when `git rev-parse --abbrev-ref HEAD` prints `$headRef`.

## 2. Learn how this repo verifies itself

Read `README.md`, `AGENTS.md`, and `.github/copilot-instructions.md` for this repo's build and test commands; record them as `$buildCommand` and `$testCommand`.

Done when each holds a real command or is recorded as absent. Absent → say so in the final report and resolve issues without that gate.

## 3. Collect the discussion

The `discussion` is every unresolved review thread, every PR-level comment, and every non-empty review body.

Done when pagination has run to `hasNextPage: false` and each item carries its author, body, path, and line range.

## 4. Drop what is already answered

A thread whose last comment is authored by `$actingLogin` and opens with any form in Reply already carries this skill's answer from an earlier run. Leave it as it stands.

Done when the working set holds only threads awaiting a first reply.

## 5. Group the discussion into issues

One `issue` is one underlying problem, however many comments describe it. Cluster on the same file and symbol, a comment that points at another ("same as above", "and here"), a reviewer restating one concern across several files, or a review body elaborated in a thread.

Record per `issue`: `issueId`, a one-sentence statement, its member thread ids, the affected paths and line ranges, and the verbatim comment excerpts.

Done when every collected thread belongs to exactly one `issue` and the assigned count equals the collected count.

## 6. Triage each issue

| Class | The issue is | Next |
|---|---|---|
| `chore` | A rename, a typo, wording, formatting, an unused import — the reviewer's instruction is the whole specification. | Step 8 |
| `substantive` | Behaviour, correctness, design, performance, or security — knowing whether the reviewer is right requires reading the code. | Step 7 |

Done when every `issue` carries one class.

## 7. Investigate every substantive issue

**Follow `references/investigation.md`** for the discovery command, the dispatch rules, the prompt template, and the verdict contract.

Done when every `substantive` issue holds a `verdict` backed by at least one `path:line` citation.

## 8. Resolve each issue on its own

Take the issues one at a time. Per `issue`:

1. `chore`, or `verdict: fix-needed` → apply the change, scoped to that `issue` alone.
2. Run `$buildCommand`, then `$testCommand` over the changed files. A failure this `issue` caused → `git checkout -- {{paths}}` and carry the `issue` forward as `unclear`.
3. `git commit`, naming the `issue` and the threads it answers.
4. `git push` to `$headRef`. A rejected push → stop and report; the remote has moved and the rest of the run rests on stale code.
5. Reply to every member thread.

An `issue` whose `verdict` is `no-change-needed` or `unclear` goes straight to the reply.

Done when every `issue` has reached a terminal state and every member thread carries exactly one reply.

## 9. Reply

Every reply takes one of four forms, and each member thread gets exactly one — a `chore` and a `fix-needed` both land on `Fixed!`.

| Situation | Reply |
|---|---|
| The change is committed and pushed. | `Fixed!` |
| The comment names a problem but not enough of it to act on. | `Q: {{question}}` — quote the phrase that is underdetermined and name what you need. |
| The comment proposes a change that reads two ways. | `Q: {{yourReading}}, Do you mean this?` — state the reading you would implement. |
| The `verdict` is `no-change-needed`, or the fix is out of reach this run. | `Thanks, looking for the solution.` |

Leave every thread open for the reviewer to close.

## Rules

- Push to `$headRef`, with a bare `git push`. `--force`, `--force-with-lease`, `--amend`, and rebasing a pushed commit stay off the table — the reviewer is reading these commits as you write them.
- One `issue`, one commit.
- Reply `Q:` the moment the `evidence` runs out. A question costs the reviewer less than a wrong guess.
- Every thread in the working set ends this run with a reply.
