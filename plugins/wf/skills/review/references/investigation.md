# Investigation

One subagent per substantive `issue`, each returning a `verdict` backed by `evidence`.

## Discover the investigation skills

Resolve each exact skill name and description before rendering; never emit placeholders literally. Investigation skills are named `search-*`, `inspect-*`, and `explore-*`. The skills available to you are already enumerated in your system context. Filter that list to names matching those prefixes. Render each applicable call as *Load and follow the `skill-name` skill to <3–6 distinctive keywords from its description>*, using its exact plain name; never send the placeholder literally.

Prioritize these matched skills over generic search/read tools for any issue within their stated scope.

## Dispatch

Spawn one subagent per substantive `issue`, in a single parallel batch of at most 3. Issues have separate `evidence` paths, so they never wait on each other.

For an `issue` answerable from this codebase alone, spawn the wf plugin's registered `codebase` agent (`wf:codebase` where namespaced), passing the checkout path/ref and `thorough` coverage. *Load and follow the `subagents` skill to select the model, effort, and context tier for a named subagent role* with role `codebase`; pass the result to the spawn. The caller renders the calls from Discover the investigation skills, reads each full body, selected route and required resources, and briefs `codebase` on applicable instructions compatible with its read-only and no-subagent rules; report incompatible checks as gaps. `codebase` performs those checks with its available tools and reports capability gaps; do not ask it to invoke skills. Spawn unavailable → report the blocked investigation.

Omit `agentName` when the issue turns on an external fact — a package's real API, a framework's documented behaviour, a spec — so the general-purpose subagent inherits skill, web, docs, and package tools. Investigation workers never load `research` or spawn subagents.

## Prompt template

For `codebase`, replace the investigation-skills block and its following paragraph with the caller-prepared read-only instructions above. For external-fact workers, use the block as written.

```text
Read-only investigation. Gather evidence and report; leave every file unchanged.

ISSUE: {{issueStatement}}

WHERE: {{paths}} at {{lines}}

WHAT THE REVIEWER SAID:
{{commentExcerpts}}

INVESTIGATION SKILLS AVAILABLE TO YOU:
{{investigationSkills}}

For each applicable listed skill, resolve its exact name and description before rendering *Load and follow the `skill-name` skill to <task>* with 3–6 description keywords; never emit placeholders literally. Read its full body, selected route and required resources before raw search. Name the ones you used in your report.

Establish whether the reviewer is right by reading the code, its callers, and its tests. Report:

1. VERDICT — fix-needed | no-change-needed | unclear
2. EVIDENCE — at least one `path:line` citation per claim, each with the quoted line. A verdict with no citation is not a verdict.
3. ROOT CAUSE — what the code actually does today and why the reviewer's reading holds or fails.
4. PROPOSED CHANGE — compare credible remedies and recommend the smallest evidence-backed correction, naming the exact symbols and files. Distinguish required facts from optional optimization. No diff.
5. BLAST RADIUS — every other call site, test, or contract the proposed change touches.

Choose `unclear` only when missing evidence or conflicting requirements prevent a safe verdict or remedy. State the blocked decision and one question that would unblock it. Multiple possible remedies or an unknown optimum alone do not make a verified concern unclear.
```

## Verdict contract

| Verdict | Means |
|---|---|
| `fix-needed` | The reviewer is right and the code needs an edit. |
| `no-change-needed` | Cited evidence shows the code already satisfies the reviewer, or the concern rests on a misreading. |
| `unclear` | A specific evidence or requirement gap blocks a safe verdict or remedy. |

A subagent that returns no `path:line` citation has returned `unclear`, whatever verdict it typed.
