---
name: doc-concept
description: Document the body of an arc42 Crosscutting Concept using a domain behavior, structural implementation, or operational policy one-page template. Use to write or revise shared domain workflows, architecture or design patterns, or operational conventions; called by record-concept and define-concept.
---

# Document Concept

Render **body only**. `/record-concept` owns frontmatter, record identity, file writes, and index synchronization. Do not edit those surfaces here.

Choose by the shared concern, not the component where it was found; read only the selected template:

| Concern | Template |
|---|---|
| Business processes, rules, user-facing validation, domain safety, domain batch work | [domain-behavior.md](./templates/domain-behavior.md) |
| Architecture/design patterns (including codebase-specific patterns), transactions, persistence, caching, concurrency, integration | [structural-implementation.md](./templates/structural-implementation.md) |
| Security, error handling, testing, configuration, migration, installation, logging, disaster recovery, runtime safety or batch operations | [operational-policy.md](./templates/operational-policy.md) |

Keep one concept per page and aim for one page. Describe a shared approach that governs multiple building blocks; name the affected scope and the conditions under which it applies. If the subject crosses categories, select the template that explains its governing rule best; link related concepts instead of duplicating obligations. Show **how** it works with one representative scenario, code or test anchor where useful. Omit optional sections and inapplicable template prompts.

Keep `Purpose`, `Rules`, `Design Guidance` as the required `##` headings in that order. Follow with optional `## Violation signals`, `## Exceptions`, `## Examples`, `## Consequences` in that order. Preserve these headings when extending an existing record; do not bulk-rewrite old records merely to choose another template.

Write one independently checkable obligation per `Rules` bullet, using MUST, MUST NOT, or SHOULD. Put the reason and application criteria in `Design Guidance`, self-contained without following a link. State a repo path or symbol only when it is itself governed; otherwise use code and tests as corroborating examples. Mark an unverified behavior as unknown outside the normative rules; do not promote codebase observations into policy without a resolved decision. Keep volatile commands and growing inventories in a linked runbook or code, not in the concept.
