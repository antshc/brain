# Requirements-coverage review

Follow the parent's shared review contract. Review the complete change against the supplied qualifying ticket descriptions; return `AXIS: requirements-coverage`. Do not discover alternative spec sources. If no qualifying description was supplied, report the gate failure to the parent instead of reviewing.

## What to report

- **Missing or partial**: required behavior absent or incompletely implemented.
- **Scope creep**: changed behavior outside the ticket requirements and stated PR scope. An unmapped symbol is a candidate, not proof; supporting implementation alone is not scope creep.
- **Implemented but wrong**: behavior differs from the requirement's intent.

Ground each finding in the ticket description and specific code evidence. Consider the whole change, cross-symbol behavior, and design intent.

## Investigation guidance

Account for every supplied requirement using implementation and wiring evidence. Check changed behavior against ticket requirements and stated PR scope; supporting code need not map directly to a requirement. Trace relevant entry points to effects where needed to establish reachability and behavior.

Conclude internally for each candidate: confirmed issue, evidence-backed plausible risk, or no issue found. Emit only actionable findings under the shared contract; anchor comments on changed right-side lines, not on ticket text or off-diff evidence.

## Comment format

Return each `REVIEW_COMMENT` as a posting-ready body: `requirement gap → impact → fix`.

- One gap; name the exact symbol or code path, identify the ticket, and quote the relevant description text.
- Contrast required and implemented behavior. For scope creep, tie the extra behavior to the quoted scope rather than treating an unmapped symbol as proof.
- Explain the unmet behavior or out-of-scope effect in one sentence; suggest the smallest change that meets the requirement or removes the extra behavior.
- Start with the gap, without classification labels or prefixes (`suggest`, `suggestion`, `nit`, `bug`). Keep only essential context; remove praise, repetition, hedging, and background.