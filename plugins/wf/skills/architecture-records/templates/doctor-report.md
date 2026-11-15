# Architecture doctor report

<!-- @: Fill this scaffold; omit placeholder rows, keep empty sections with “None”, and use relative record links plus source path:line or source URLs. -->

## Summary

- **Outcome:** {{outcome|findings, incomplete, or clean}}
- **Coverage:** {{coverage|complete or incomplete}}; {{currentCount}} current, {{driftCount}} drift, {{obsoleteCount}} obsolete, {{unknownCount}} unknown artifacts.

<!-- @: Count each artifact once by aggregate verdict; claim findings may exceed artifact counts. Findings takes precedence over incomplete, while Coverage preserves blockers. -->

## Scope

- **Revision / inspected at:** {{revision}} / {{time}}
- **Roots and artifacts:** {{scope}}
- **Exclusions:** {{exclusions|None}}
- **Available evidence:** {{sourcesAndAccess}}

## Coverage

| Artifact kind | Inventoried | Assessed | Blocked |
| --- | --- | --- | --- |
| {{kind}} | {{inventoried}} | {{assessed}} | {{blocked}} |

<!-- @: Assessed and blocked are disjoint; a partially assessed artifact counts blocked, retaining known findings. Inventoried equals assessed plus blocked; excluded artifacts are listed in Scope. -->

| Index / table | Total rows | Consumed rows | Load result / gaps |
| --- | --- | --- | --- |
| {{indexAndTable}} | {{total \| unknown if loading failed}} | {{consumed}} | {{loadResult}} |

## Findings

| ID | Artifact / claim | Verdict | Impact | Documented statement | Observed evidence | Suggested correction / owning route |
| --- | --- | --- | --- | --- | --- | --- |
| {{id}} | {{recordAndSection}} | {{verdict \| drift, obsolete, or unknown}} | {{impact}} | {{statementAndCitation}} | {{observationAndCitation}} | {{correctionAndRoute}} |

## Current records

| Artifact | Verdict | Evidence / implementation state |
| --- | --- | --- |
| {{record}} | current | {{supportingEvidence \| Explicit approved decision awaiting implementation, with decision citation}} |

## Unknowns and blockers

| Artifact / claim | Missing evidence or access | What resolves it |
| --- | --- | --- |
| {{artifactOrClaim}} | {{gap}} | {{resolution}} |

## Recommended next actions

1. {{action|Correction and owning route/action, or decision required; recommendation only}}
