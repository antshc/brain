# Investigation

One subagent per substantive `issue`, each returning a `verdict` backed by `evidence`.

## Discover the investigation skills

Investigation skills are named `search-*`, `inspect-*`, and `explore-*`. Their set differs per machine, so resolve it at runtime rather than from memory:

```bash
grep -rlE '^name: (search|inspect|explore)-' --include=SKILL.md . "$HOME/.copilot/skills" "$HOME/.copilot/installed-plugins" 2>/dev/null
```

Read the frontmatter `name` and `description` of each hit and render one line per skill as `- /{{name}} — {{description}}`. That block is `{{investigationSkills}}`. No hits → `{{investigationSkills}}` reads `none — use the built-in search and read tools.`

Search only those three roots. A wider sweep costs minutes and returns the same set.

## Dispatch

Spawn one `runSubagent` per substantive `issue`, in a single parallel batch of at most 3. Issues have separate `evidence` paths, so they never wait on each other.

`agentName: Explore` when the `issue` is answerable from this codebase alone. Omit `agentName` when it turns on an external fact — a package's real API, a framework's documented behaviour, a spec — so the general-purpose subagent inherits web, docs, and package tools.

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
