---
name: delegate-explore
description: Hand a codebase lookup to the Explore subagent instead of reading files in the caller's own context. Owns what to delegate versus what to look up directly. Called by grill-design for broad-sweep code and test lookups.
---

# Delegate Explore

Spawn the `Explore` subagents for codebase lookups — it reads in its own context and returns a verdict, so the caller's context stays clean. The call blocks until the verdict returns; state the thoroughness (`quick`, `medium`, `thorough`) with the question.

## What to delegate

Broad-sweep questions: does this pattern exist elsewhere, who calls this, is the claim true across layers, what do the existing tests cover. Consume only the verdict — never re-read the files it already reported on.

## What to keep direct

Anchor precision only: the exact line, signature, or assertion you need to quote back verbatim.
