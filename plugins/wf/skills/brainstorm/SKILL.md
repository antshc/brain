---
name: brainstorm
description: Interview the user relentlessly about an idea, problem or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test an idea, get brainstormed on their design, or mentions "brainstorm".
disable-model-invocation: true
---
<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action.
</HARD-GATE>

Run a `/grilling` session on the idea, problem, or design.

Once clear, spawn 1-3 `general-purpose` subagents in parallel, each exploring a different approach under a distinct constraint (e.g., simplest, most flexible, optimized for the common case). Each subagent returns: the approach, trade-offs, pros/cons, and reasoning.

Present list of approaches as bullets with terse, concise sumamry, then give your own recommendation — the strongest approach, presented in full. Propose a hybrid if elements from different approaches combine well.

Ask the user to approve, or present other approach.

On approval, summarize using [BRAINSTORM-FORMAT.md](./BRAINSTORM-FORMAT.md).
