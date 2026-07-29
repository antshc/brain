---
name: delegate-explore
description: Spin up a background agent to explore the codebase so the caller keeps working while it reads. Owns what to hand to a sub-agent versus what to look up directly. Called by grill-design for broad-sweep code and test lookups.
---

# Delegate Explore

Spin up a background agent to do the explore, so you keep working while it reads.

## What to delegate

Broad-sweep questions: does this pattern exist elsewhere, who calls this, is the claim true across
layers, what do the existing tests cover. Hand the question over, keep working, then consume only
the verdict — never re-read the files it already reported on.

## What to keep direct

Anchor precision only: the exact line, signature, or assertion you need to quote back verbatim.
