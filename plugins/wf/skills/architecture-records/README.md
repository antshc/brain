# Architecture records

Define crosscutting Concepts, record settled architecture, maintain its indexes, and check whether records still describe the system.

## Routes and examples

| Request | Route | Result |
|---|---|---|
| `/architecture-records route: define-concept caching` | `define-concept` | Inspect candidates, settle decisions with the user, record and index one Concept |
| `/architecture-records route: adr` | `adr` | A qualifying decision, alternatives, and its owning index row |
| `/architecture-records route: building-block` | `building-block` | Deployable record/index and applicable context diagrams |
| `/architecture-records route: deployment-view` | `deployment-view` | Runtime topology and architecture pointer |
| `/architecture-records route: term` | `term` | One resolved glossary entry |
| `/architecture-records route: concept-body` | `concept-body` | Rendered body and kind; no files |
| `/architecture-records route: concept-record` | `concept-record` | Persist/extend a settled Concept and its index row |
| `/architecture-records route: decision-bullet` | `decision-bullet` | One established decision bullet; no files |
| `/architecture-records route: initialize` | `initialize` | Only missing ARCHITECTURE.md and GLOSSARY.md |
| `/architecture-records route: index action: load` | `index` | Complete loaded rows/counts or explicit failure |
| `/architecture-records route: doctor docs/concepts/` | `doctor` | Scoped evidence-backed currency report |

Other index actions: `scan`, `trigger`, `ensure-section`, `sync-row`, `sync-deployment`; row mutations use `rowAction`. Explicit routes win; existing record `mode` aliases remain accepted. Ambiguous artifact or persistence intent is resolved before writing.

## Define versus record

`define-concept` owns candidate selection, evidence-backed questioning, and confirmed defaults. `concept-body` renders resolved content; `concept-record` persists it without another interview. ADRs, terms, blocks, and topology retain their own recording gates. The separate `define` skill charts Research maps only.

## Doctor scope and output

Default: all ADRs, Concepts, building blocks, root/block indexes, unindexed records, and linked architecture records under the established docs scope. Context diagrams and deployment pointers are checked when referenced. Explicit paths/kinds narrow the audit; exclusions remain visible.

Report sections: Summary, Scope, Coverage, Findings, Current records, Unknowns and blockers, Recommended next actions. Verdicts: `current`, `drift`, `obsolete`, `unknown`; outcome: `findings`, `incomplete`, `clean`. Only complete coverage permits clean. An approved but unimplemented decision remains valid; implementation disagreement is drift, never implicit permission to change policy.

Doctor is read-only; a supplied report path permits only that report write. Corrections require a separate requested record/index action. No report path means inline output.

## Resource ownership

The router selects playbooks and directly lists every required resource with its loading condition. Templates own record/report shape; playbooks own procedures; the router owns shared rules and handoffs. Questioning and arc42 taxonomy are local. The index loader's CLI/JSON/counts contract is unchanged. Authored records retain their existing paths.
