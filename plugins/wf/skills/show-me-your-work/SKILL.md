---
name: show-me-your-work
description: >-
  Keeps a reviewable decision trail for long-running or unattended work as a TSV log, one row per decision with why, evidence, and result; audits it against the transcript, gets a cross-model review, and prints the final report. Use for /show-me-your-work, autonomous or multi-phase runs, or work reviewed after stepping away.
---

# Show me your work

Keep one canonical log. Select mode from the request; default **Log**.

| Mode | Trigger |
|---|---|
| **Log** | start of a run, a decision to record, no mode named |
| **Report** | end of a run, print report, hand back |

## Format

One TSV file, one row per decision. Cells single-line. Evidence is a pointer, not prose. Header: [references/decision-log-template.tsv](references/decision-log-template.tsv).

| Column | Content |
|---|---|
| `ts` | ISO8601 UTC timestamp |
| `phase` | phase or workstream |
| `decision` | what was chosen or done, one line |
| `why` | reason in plain words; name a driving principle plainly, not as a tag |
| `evidence` | commit SHA, PR/issue number, `file:line`, artifact/trace/screenshot path; never a paragraph |
| `result` | outcome or predicate state: `tests green`, `reverted`, `INCONCLUSIVE`, `open` |

```
ts	phase	decision	why	evidence	result
2026-05-24T09:02:00Z	frame	counted the work first, about 100 components	wanted the size before a long run	commit 3a9f1c2	found 5 blockers to sort first
2026-05-24T12:30:00Z	widget	threw out a helper's work because its screenshots were blank	checked the real files instead of trusting its summary	worktree reset	reverted, tightened the brief
```

## Location

Default `tmp/{{taskSlug}}/decisions.tsv` under the repo root, or the caller's path. Confirm the path is ignored with `git check-ignore {{logfile}}`; not ignored → pick an ignored dir. Keep it out of git. Commit only when a reviewer needs the trail to trust the result.

## Log

Append with **`python3 ./scripts/log.py {{logfile}} {{phase}} {{decision}} {{why}} {{evidence}} {{result}}` from this skill's base directory**. It stamps `ts`, writes the header on first use, flattens tabs/newlines, and quotes cells starting with `=`, `+`, `-`, `@`. Done when the row is appended.

- Write like telling a teammate what you did: plain words, concrete actions, no jargon.
- Log decision points and checkpoints: a fork chosen, a unit completed with its verification, a pivot or revert with its trigger, a blocker, a gate fixed. Loop runs → one row per iteration. Skip the trivial.
- Append-only. A wrong call gets a new superseding row; never edit or delete history.
- Prefer evidence produced by committed scripts over hand-made one-offs.

**Runs.** A run is one agent conversation including later turns. A pickup, replacement agent, or new chat starts a new run. Adding to a log with existing rows → first row has phase `start`; a returning run first reads the last rows to see whether another run wrote since. A `start` row names the `ts` range of prior rows this run did not write; evidence names this run (agent or session id). Use phase `start` for nothing else.

## Report

Run in order before handing back.

1. **Audit against the transcript.** Read this run's transcript only: the current session's `events.jsonl` in its session-state folder (the session folder the system prompt names). Never read other sessions. Walk this run's rows (from its `start` row, or the first row if it created the log, to the next foreign `start` row):
   - every row maps to a real decision or action;
   - every evidence pointer resolves and shows the claim;
   - a fork, pivot, or abandoned approach that shaped the work but is missing is a gap → add it.
   Correct the log, not the story: a wrong or invented row gets a superseding row with what happened and a resolving pointer. Done when every row is checked and gaps are added.
2. **Cross-model review.** Spawn one subagent on a different model family from the one that did the work; self-review is not a substitute. It reads the log and transcript and flags, without redoing the work:
   - decisions with weak or absent evidence;
   - verification skipped or claimed without proof in the transcript;
   - choices risky in hindsight (premature, scope-creeping, papering over a symptom);
   - gaps a casual skim would miss.
   Done when the subagent returns its flags.
3. **Print the report.** Render the log as a Markdown table (all columns), then an **Attention** section: first line `reviewed by {{model}}`, then each flag pointing at specific rows or moments. "No flags" is valid; the model line is required. Done when both appear in the reply.

## Composing

Other skills route their audit trail here; reference this skill by name and let it own the format. Do not restate the columns.
