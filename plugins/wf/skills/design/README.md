# Design skill

One discoverable entry point for code architecture, standalone code sketches, deep-module interfaces, evidence, decision interviews, specifications and tickets.

| Request | Route | Outcome |
| --- | --- | --- |
| `/design architect design retries` | `architect` | Research, Arena sketch, evidence and verification, then implementation by default |
| `/design architect checkpoint design retries` | `architect` | Review the sketch before implementing or handing off |
| `/design architect arena-agents=2 design retries` | `architect` | Compare two independently drafted architecture shapes |
| `/design sketch add pagination to orders` | `sketch` | One usage-first design package, no production edits |
| `/design deep-module order pricing seam` | `deep-module` | Three or more interface options, comparison, recommendation |
| `/design interrogate intent: preserve writes; target: DynamoDB Local` | `interrogate` | Reproduced adversarial findings, no fixes applied |
| `/design prove GSI backfill; target: DynamoDB Local` | `prove` | Observed experiment, reproducible command and report |
| `/design grill` / `/design spec` / `/design tickets` | Corresponding route | Decisions, spec or approved ticket breakdown |
| `/design wayfinder` / `/design review` | Corresponding route | Decision map or design-gap assessment |

Architect accepts `arena-agents=1|2|3` (default 1); Interrogate accepts `adversaries=1|2|3` (default 1). `checkpoint` requires explicit request. Explicit design-only handoff stops before implementation and returns the accepted `synthesis/` package to `design spec`.

Both `sketch` and `architect` use [one code-sketch contract](references/sketch-contract.md). The former makes one package; the latter uses that procedure for Arena candidates and synthesizes the selected package. Artifacts live under `<repo-root>/tmp/design-<slug>/` and the accepted package is always `synthesis/{sketch/,module-map.md,rationale.md}`.

See [Skill router](SKILL.md) and [Architect playbook](playbooks/architect.md). `draft-artifact design` remains the owner of authoritative feature-design documents.
