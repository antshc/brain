---
name: review
description: >-
  Review code changes, PR comments, downstream risks, and regression coverage. Use for 'review this PR', 'address PR comments', 'blast radius', or 'test gaps'. Not for design review → `design`.
argument-hint: '<code|comments|blast-radius|tests-gap|hitl> [target] [--axes list] [options]'
---

# Review

| Route | Select for | Playbook |
|---|---|---|
| `code` | Review a PR for new findings. Accept a PR URL and optional `--axes <list>`; all axes run by default. | [Code review](playbooks/code.md) |
| `comments` | Investigate and address existing PR review threads. Accept a PR URL. | [PR comments](playbooks/comments.md) |
| `blast-radius` | Assess downstream breakage or what a change could affect. | [Blast radius](playbooks/blast-radius.md) |
| `tests-gap` | Assess regression coverage or identify missing tests. | [Tests gap](playbooks/tests-gap.md) |
| `hitl` | Explicit request for a human-led PR review with approval before posting. Accept a PR URL. | [Human-led review](playbooks/hitl.md) |

1. Honor the explicit route from the user or caller and pass its remaining arguments to the playbook. Continue an active route when the user responds to its question or approval prompt. Otherwise infer the route from clear intent. Select `hitl` only on explicit request, including clear natural language.
2. For a PR URL alone, a generic fix review, or any other ambiguous request, ask which outcome the user wants and wait before loading a playbook or acting. If the user explicitly asks for both impact and test coverage, run `blast-radius` first and pass its risks to `tests-gap`.
3. Read only the selected playbook in full, then open its references as directed. Resolve skill-relative paths from this `SKILL.md` directory, including absolute paths handed to subagents.

Every route spawns its own workers or calls worker-owning skills (`research`, `prove`). **MUST** run in the caller's session, never inside a wrapper subagent; a worker that receives this skill returns the request to its caller.

`review` owns judgment; *Load and follow the `github` skill to manage review threads, posts, replies, and resolution mechanics*. Long-running review and CI monitoring is the caller's loop, not this skill. For technical design review, *Load and follow the `design` skill to review technical design architecture* using `review`.
