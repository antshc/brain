# Requirements-coverage review

Follow the parent's shared review contract. Review the complete change against the supplied qualifying ticket descriptions; return `AXIS: requirements-coverage`. Do not discover alternative spec sources. If no qualifying description was supplied, report the gate failure to the parent instead of reviewing.

## What to report

- **Missing or partial**: required behavior absent or incompletely implemented.
- **Scope creep**: changed behavior outside the ticket requirements and stated PR scope. An unmapped symbol is a candidate, not proof; supporting implementation alone is not scope creep.
- **Implemented but wrong**: behavior differs from the requirement's intent.

Ground each finding in the ticket description and specific code evidence. Consider the whole change, cross-symbol behavior, and design intent.

## LSP workflow

1. Enumerate changed symbols: types, methods, properties, fields, interfaces, records, constructors. Keep this shallow; use the map for reachability checks.
2. Trace each requirement to definitions and references: confirm required behavior exists, is reachable, and is wired rather than dead code.
3. Invert the map: inspect changed symbols without a requirement mapping as scope-creep candidates, then check their supporting role and stated scope before reporting.
4. For requirements spanning symbols, trace incoming/outgoing calls from entry point to effect. Stop when implementation, reachability, and wiring are established; prefer representative paths over exhaustive call graphs.

Conclude internally for each candidate: confirmed issue, evidence-backed plausible risk, or no issue found. Emit only actionable findings under the shared contract; anchor comments on changed right-side lines, not on ticket text or off-diff evidence.

## Comment format

Return each `REVIEW_COMMENT` as a posting-ready body: `requirement gap → impact → fix`.

- One gap; name the exact symbol or code path, identify the ticket, and quote the relevant description text.
- Contrast required and implemented behavior. For scope creep, tie the extra behavior to the quoted scope rather than treating an unmapped symbol as proof.
- Explain the unmet behavior or out-of-scope effect in one sentence; suggest the smallest change that meets the requirement or removes the extra behavior.
- Start with the gap, without classification labels or prefixes (`suggest`, `suggestion`, `nit`, `bug`). Keep only essential context; remove praise, repetition, hedging, and background.