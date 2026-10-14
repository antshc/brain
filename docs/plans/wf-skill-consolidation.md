# WF skill consolidation

Status: partially implemented. `track-ledger` is absorbed into `grill-design` as a root-level `track-ledger.md` reference; its standalone skill is removed. Questioning remains unchanged; other consolidation and archive moves remain proposed.

Backlog entry superseded: `manage-backlog` was removed in favor of GitHub references bundled with each consuming skill and label setup owned by `init-wf`. The historical roster/count below describes the original consolidation proposal, not the current plugin.

Reduce 36 active skills to 27. Use progressive disclosure for grouped procedures; archive `to-use-cases`.

## Proposed skill list

| Proposed skill | Existing skills / disclosed procedures |
|---|---|
| `init-wf` | `init-wf` |
| `wayfinder` | `wayfinder` |
| `grill-design` | `grill-design`, `questioning`, `track-ledger` |
| `research` | `research` |
| `bottom-line` | `bottom-line` |
| `define-research` | `define-research` |
| `explore-codebase` | `explore-codebase` |
| `inspect-nuget-source` | `inspect-nuget-source` |
| `inspect-system` | `inspect-system` |
| `experiment` | `experiment` |
| `prototype-cloud-scenario` | `prototype-cloud-scenario` |
| `define-concept` | `define-concept` |
| `record-architecture` | `record-adr`, `record-building-block`, `record-deployment-view`, `record-term`, `doc-concept`, `record-concept`, `doc-decision` |
| `bootstrap-docs` | `bootstrap-docs` |
| `index-docs` | `index-docs` |
| `doc-architecture-diagram` | `doc-architecture-diagram` |
| `doc-behavior-diagram` | `doc-behavior-diagram` |
| `doc-code-diagram` | `doc-code-diagram` |
| `doc-contracts` | `doc-contracts` |
| `normalize-requirements` | `normalize-requirements` |
| `draft-story` | `draft-story` |
| `to-stories` | `to-stories` |
| `draft-bug` | `draft-bug` |
| `to-spec` | `to-spec` |
| `to-zdesign` | `to-zdesign` |
| `to-tickets` | `to-tickets` |
| `manage-backlog` (superseded; removed) | Historical backlog abstraction; now skill-local GitHub references and `init-wf` label setup |

## Proposed archive

| Existing skill | Destination |
|---|---|
| `to-use-cases` | `_backup/to-use-cases/` |

## Triggering and usage

- `grill-design` covers interviews, questioning, and decision forks. Its ledger procedure is now a root-level reference, loaded before ledger access; questioning remains unchanged.
- `record-architecture` covers documenting or recording ADRs, concepts, deployables, deployment topology, glossary terms, and decision bullets. Select the requested record type and load only its procedure and required helpers.
- `define-concept` discovers, scopes, and resolves concepts; use `record-architecture` to document and persist settled knowledge. Recording a settled concept must not force another interview.
- Keep `bootstrap-docs` and `index-docs` independently reusable by setup, recording, and inspection workflows.
- Preserve independent triggers for research, findings summaries, NuGet inspection, each diagram family, requirement normalization, and single-story drafting.
- Parent descriptions own discovery; `SKILL.md` owns routing; references own disclosed procedures. MUST load the selected procedure before acting.
- Preserve invocation, approval, evidence, and output contracts. Grouping MUST NOT add interviews, publication, or execution to unrelated modes.
- Replace calls to absorbed skills with the parent skill and exact mode. Keep each shared procedure in one place.
- Absorbed procedures lose independent skill triggers and commands; references are not standalone skills.
- Verify representative prompts before implementation is considered complete, especially the broad `record-architecture` entry point.

The `track-ledger` merge was authorized and applied separately. Other consolidation and archive moves have not been applied.
