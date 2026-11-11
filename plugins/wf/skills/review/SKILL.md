---
name: review
description: >-
  Review pull requests for findings, judge and fix existing PR comments, assess blast radius, or find regression test gaps. Use for 'review this PR', 'address PR comments', 'blast radius'. Not for posting or thread mechanics → `github`; technical design review → `design`.
argument-hint: '<code|comments|blast-radius|tests-gap|architecture|hitl> [target] [options]'
---

# Review

| Route | Select for | Playbook |
| --- | --- | --- |
| `code` | Review a PR for new findings. Accept a PR URL. | [Code review](playbooks/code.md) |
| `comments` | Investigate and address existing PR review threads. Accept a PR URL. | [PR comments](playbooks/comments.md) |
| `blast-radius` | Assess downstream breakage or what a change could affect. | [Blast radius](playbooks/blast-radius.md) |
| `tests-gap` | Assess regression coverage or identify missing tests. | [Tests gap](playbooks/tests-gap.md) |
| `architecture` | Explicit architecture drift audit. Accept `auto` or `human`. | [Architecture](playbooks/architecture.md) |
| `hitl` | Explicit request for a human-led PR review with approval before posting. Accept a PR URL. | [Human-led review](playbooks/hitl.md) |

1. Honor the explicit route from the user or caller and pass its remaining arguments to the playbook. Continue an active route when the user responds to its question or approval prompt. Otherwise infer the route from clear intent. Select `architecture` and `hitl` only on explicit request, including clear natural language.
2. For a PR URL alone, a generic fix review, or any other ambiguous request, ask which outcome the user wants and wait before loading a playbook or acting. A bare PR URL plus a retired review level remains ambiguous. If the user explicitly asks for both impact and test coverage, run `blast-radius` first and pass its risks to `tests-gap`.
3. Read only the selected playbook in full, then open its references as directed. Resolve skill-relative paths from this `SKILL.md` directory, including absolute paths handed to subagents.

`review` owns judgment; *run `github` skill for review thread, post, reply, and resolve mechanics*. Long-running review and CI monitoring is the caller's loop, not this skill. For technical design review, use `/design review`.
