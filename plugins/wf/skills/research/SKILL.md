---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo, dispatching to a specialist research skill when one covers the subject. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a subagent.
---

# Research

Every path below delegates the investigation to a subagent via `runSubagent` — omit `agentName` so it inherits full tool access (including web fetch), rather than the codebase-only `Explore` agent, since the question usually reaches outside this repo. This keeps the raw reading out of this session's context; it doesn't run in the background, so the caller waits for its one final report.

## 1. Dispatch to a specialist

Specialists are named `research-*`, one per subject domain (a cloud provider, this repo's own system, and whatever else is installed). Each owns its sources, evidence rules, template, and output path — richer than anything the generic job below produces.

Discover them, never hardcode them: scan the available skills roster for every name matching `research-*`, then judge the question against each one's `description`, and against its `compatibility` line where it carries one.

- **One covers the question** → its job is to Run that skill over the question; stop here once the subagent reports back and its output passes Verify the delegated output.
- **Several cover different parts** → one subagent per specialist, each over the part that specialist owns, each writing its own file.
- **The best match names a tool or server in `compatibility` that this session lacks** → say which one is missing, then continue below.
- **None covers it** → continue below.

Pass the user's requested output shape — document count, diagram type, file path, framing — to the subagent **verbatim**, as a constraint the specialist's own defaults do not override. Paraphrasing it is how a shape requirement gets dropped.

A specialist is only what the roster lists — a domain with no entry there is handled by the generic job.

## Verify the delegated output

A subagent's summary is a claim about its output, not the output. Open the primary artifact it wrote and check it yourself before reporting completion:

- **Path and count** — the file sits where the chosen skill's contract puts it, and the run wrote no extra files the contract did not ask for.
- **Diagram type** — every diagram is the type the user or the skill's contract named, not whatever the subagent preferred.
- **Placeholders** — no `{{…}}` token, `**Rules**` block, or unfilled template section survives in the result.
- **Requested shape** — the verbatim constraints passed in are satisfied.

A failing check is a defect: repair it directly when the fix is mechanical, and re-dispatch with the violated constraint stated first when it needs the research redone. Report completion only once every check passes.

## 2. Generic job

Its job:

1. Investigate the question against primary sources — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes (e.g. `docs/kbs/`); match the existing convention, and if there is none, put it somewhere sensible and say where.
