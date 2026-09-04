---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a subagent.
---

# Research

Delegate the investigation to a subagent via `runSubagent` — omit `agentName` so it inherits full tool access (including web fetch), rather than the codebase-only `Explore` agent, since the question usually reaches outside this repo. This keeps the raw reading out of this session's context; it doesn't run in the background, so the caller waits for its one final report.

Its job:

1. Investigate the question against primary sources — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes (e.g. `docs/kbs/`); match the existing convention, and if there is none, put it somewhere sensible and say where.

# Research template
```
# Research: <Topic>

## Question
What are we trying to find out, and why now?

## Scope
In / out of scope.

## Findings
- Claim
  Source: <official doc / code path / API reference>
- Claim
  Source: ...

(Group findings by provider/system/component subheading when comparing more than one.)

## Comparison / Trade-offs
Table or bullets, only if multiple options were evaluated.

## Impact on our system
Where this touches current dependencies, config, or code.

## Recommendation
Answer the original question directly.

## Open Questions / Risks
```