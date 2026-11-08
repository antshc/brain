# Initiative review

Follow the parent's shared review contract. Review the complete change against the supplied resolved initiative description; return `AXIS: initiative`. Do not discover alternative spec sources. If no qualifying description was supplied, report the gate failure to the parent instead of reviewing.

## What to report

- **Missing or partial**: required behavior absent or incompletely implemented.
- **Scope creep**: changed behavior outside the initiative requirements and stated PR scope. An unmapped symbol is a candidate, not proof; supporting implementation alone is not scope creep.
- **Implemented but wrong**: behavior differs from the requirement's intent.

Ground each finding in the initiative description and specific code evidence. Consider the whole change, cross-symbol behavior, and design intent.

## Investigation guidance

Account for every supplied requirement using implementation and wiring evidence. Check changed behavior against initiative requirements and stated PR scope; supporting code need not map directly to a requirement. Trace relevant entry points to effects where needed to establish reachability and behavior.

Conclude internally for each candidate: confirmed gap or no issue found. Emit only actionable findings under the shared contract; anchor comments on changed right-side lines, not on initiative text or off-diff evidence.

## Finding content

Supply the requirement gap, concrete impact, and smallest correction to the shared conversation draft. Name the exact symbol or code path and state the required behavior: quote the supplied issue/ticket description text verbatim when available, otherwise restate it. Never add the initiative ID, link, or URL.

Contrast required and implemented behavior. For scope creep, state the intended scope explicitly rather than treating an unmapped symbol as proof. Suggest the smallest change that meets the requirement or removes the extra behavior.
