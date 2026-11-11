# Investigation

One subagent per substantive `issue`, each returning a `verdict` backed by `evidence`.

## Discover the investigation skills

Investigation skills are named `search-*`, `inspect-*`, and `explore-*`. The skills available to you are already enumerated in your system context. Filter that list to names matching those prefixes.

Prioritize these matched skills over generic search/read tools for any issue within their stated scope.

## Dispatch

Spawn one `runSubagent` per substantive `issue`, in a single parallel batch of at most 3. Issues have separate `evidence` paths, so they never wait on each other.

Use the WF `hunter` agent when the `issue` is answerable from this codebase alone. If Hunter is unavailable, fall back to the built-in `Explore` subagent: the caller loads the relevant investigation skills and includes their applicable read-only instructions in the brief, replacing the template's skill-invocation request. Explore performs those checks with its available tools and reports any capability gaps; do not ask it to invoke skills.

Omit `agentName` when the issue turns on an external fact — a package's real API, a framework's documented behaviour, a spec — so the general-purpose subagent inherits skill, web, docs, and package tools. Preserve this caller-specific Hunter → Explore fallback when dispatching through `subagents`.

## Prompt template

```
Read-only investigation. Gather evidence and report; leave every file unchanged.

ISSUE: {{issueStatement}}

WHERE: {{paths}} at {{lines}}

WHAT THE REVIEWER SAID:
{{commentExcerpts}}

INVESTIGATION SKILLS AVAILABLE TO YOU:
{{investigationSkills}}

Consider each listed skill by name and use every one that bears on this issue before falling back to raw search. Name the ones you used in your report.

Establish whether the reviewer is right by reading the code, its callers, and its tests. Report:

1. VERDICT — fix-needed | no-change-needed | unclear
2. EVIDENCE — at least one `path:line` citation per claim, each with the quoted line. A verdict with no citation is not a verdict.
3. ROOT CAUSE — what the code actually does today and why the reviewer's reading holds or fails.
4. PROPOSED CHANGE — the minimal edit in prose, naming the exact symbols and files. No diff.
5. BLAST RADIUS — every other call site, test, or contract the proposed change touches.

Choose `unclear` when the reviewer's intent has two defensible readings, and state both readings plus the one question that separates them.
```

## Verdict contract

| Verdict | Means |
|---|---|
| `fix-needed` | The reviewer is right and the code needs an edit. |
| `no-change-needed` | Cited evidence shows the code already satisfies the reviewer, or the concern rests on a misreading. |
| `unclear` | Two defensible readings of the reviewer's intent survive the evidence. |

A subagent that returns no `path:line` citation has returned `unclear`, whatever verdict it typed.
