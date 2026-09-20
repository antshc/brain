# Feature Research: {{featureName}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Every claim carries `path:line` or `path:startLine-endLine`; a bare symbol name is not evidence.
- Quote the deciding line whenever it is short enough to settle the claim on sight.
- Executing code proves behavior; tests, comments, and docs state only intent — record any mismatch as a finding.
- Nothing reaches the diagram, tables, or conclusion without a Fact behind it.

- Question: {{the exact question being answered — capability, entry point, specific behavior}}
- Scope: {{repo/service and layers in scope; what's explicitly out, with a link to any doc that owns the excluded area}}
- Status: investigating | answered

## Summary

**Rules:** 2-3 sentences answering the framed question. Lead with whatever most surprises a reader who assumed the obvious mechanism.

{{summary}}

## Mechanism

**Rules:** `sequenceDiagram` for a call/message flow, `flowchart` for branching decision logic. Every participant is a real file or component; every message carries the `path:line` that established it. When several sources can serve the flow, the diagram shows the selector and the fallback edges, not only the winning path.

```mermaid
sequenceDiagram
    {{participants and messages tracing the confirmed call chain, each message noting its file:line}}
```

## External sources

**Rules:** one row per source reachable for the framed case; keep the section when a single source is confirmed to be the only one, and say so. `Selected when` names the config key, flag, or tweak and the deciding value, including the default when it is absent.

| Source | Selected when | Falls back to | Demotion trigger | Evidence |
|---|---|---|---|---|
| {{client or implementation}} | {{key=value, flag, tweak, or default}} | {{next source, or none}} | {{exception, timeout, status code, invalid-result rule}} | {{path:line}} |

**Rules:** state the terminal behavior when every source fails, whether the selector is read per call or once at startup, and whether a fallback result is cached — each cited.

{{sourceSelectionNotes}}

## Facts

**Rules:** one row per confirmed claim. Prefer facts that contradict the default assumption over facts that confirm it.

| # | Fact | Evidence |
|---|---|---|
| 1 | {{fact}} | {{path:line — `deciding line quoted`}} |

## Assumptions

**Rules:** plausible but unconfirmed. `What would verify it` is a concrete action — a command, a probe, a file to open — not "investigate further".

| # | Assumption | Why unverified | What would verify it |
|---|---|---|---|

## Unknowns

**Rules:** `Next probe` names the exact search, command, or file to open.

| # | Unknown | Next probe |
|---|---|---|

## Conclusion

**Rules:** state the explanation the facts support, and name which artifact actually enforces the behavior when several describe it.

{{conclusion}}
