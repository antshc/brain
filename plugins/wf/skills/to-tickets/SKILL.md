---
name: to-tickets
description: Breaks a Spec issue into codebase-informed, agent-executable implementation tasks and, after explicit user approval, publishes them as GitHub sub-issues with a native blocker dependency graph. Use when cutting a spec or plan.md into tickets, sub-issues, AFK/HITL slices, or offline Markdown tickets.
argument-hint: "{{specIssueNumber}} [{{implementationDetails}}, `plan.md`] | offline {{localSpecPath}}"
disable-model-invocation: true
---

# To Tickets

Turn one Spec into user-approved, self-contained implementation tickets linked to that Spec.

## Inputs

- `{{specIssueNumber}}` — parent Spec issue; required online.
- `[implementationDetails]` — inline text or file path (e.g. `plan.md`, `/memories/session/plan.md`); replaces the spec body as slicing source.
- `offline {{localSpecPath}}` — explicit offline mode; needs local spec content plus Initiative/source-repository metadata.

Load [github.md](./references/github.md) before any GitHub read/write or offline save.

## Constraints

- **Approval guard:** **MUST NOT** create, label, link, or save tickets (GitHub issues or `docs/tickets/` files) until the user explicitly approves the current breakdown in step 4. Silence, partial feedback, corrections, and ambiguous replies are not approval. Any slice change after approval needs re-presentation and re-approval. Before approval, only read and draft. Rationale: published tickets create tracker state the user must clean up.
- **MUST NOT** close or modify the parent Spec issue.
- **Source precedence:** spec (or supplied implementation details) is authoritative for behavior and requirements; matched Concepts/ADRs for implementation patterns and policies; code for current state. On conflict, surface it in step 4; do not silently pick a side.
- **Label guard:** every created ticket **MUST** carry `hitl`, whatever its HITL/AFK type. **MUST NOT** create or apply an `afk` label or any label encoding HITL/AFK type. Rationale: `implement-spec` skips `hitl` tickets; the user removes `hitl` to release a reviewed ticket for execution.
- Use offline publishing only when explicitly requested or after a reported GitHub/tool/authentication failure. **MUST NOT** report offline or partial output as GitHub success.

## Workflow

### 1. Resolve inputs

Reject an explicit `auto` argument as unsupported before any publication; do not treat it as approval.

Determine mode:

- **Online, spec only:** resolve the tracker repository once from the docs/harness root (current repository for single-repo work) with `gh repo view --json nameWithOwner --jq .nameWithOwner` → `{{trackerRepository}}` (tracker, not the source repository). Fetch via **Read spec** in [github.md](./references/github.md); slicing source = issue title, body, and comments.
- **Online, spec + implementation details:** resolve `{{trackerRepository}}` and read the spec as above; slicing source = implementation details (read file paths; use inline text directly).
- **Explicit offline:** follow **Offline publishing** in [github.md](./references/github.md); use the supplied local spec and metadata; skip all GitHub lookups.

Set `{{repoLabel}}` to the spec's single `repo:target:<owner>/<name>` label (offline: from metadata). Missing `{{specIssueNumber}}` online, missing offline spec/metadata, or zero/several routing labels → ask the user; **MUST NOT** invent values.

*Done when* slicing source, `{{specIssueNumber}}`, `{{repoLabel}}`, and (online) `{{trackerRepository}}` are known.

### 2. Explore code and records

- Explore affected code until you can name current behavior, module/folder boundaries, dependencies, shared files, integration layers, and verification seams. For restructuring, inspect project references, namespace/path conventions, build configuration, and existing regression tests. Reuse exploration already done this session.
- Use `GLOSSARY.md` vocabulary for ticket titles and bodies.
- Read the `Architecture Decision Records` and `Crosscutting Concepts` indexes in `ARCHITECTURE.md`; open each record relevant to the changed area.
  - **Concepts** (shared domain behavior, implementation patterns, operational policies such as layering, validation, persistence, testing) — slices and their acceptance/testing decisions **MUST** conform.
  - **ADRs** (localized decisions) — respect and reference them in ticket bodies.
- Find prefactoring that makes the change easy: "Make the change easy, then make the easy change."

*Done when* matched Concepts/ADRs, prefactor candidates, and source conflicts are listed.

### 3. Select strategy and draft tasks

Choose task boundaries using the plan/spec and the inspected codebase:

<task-decomposition-rules>

- **Functional:** Prefer one complete business capability across touched layers. For small API services with existing API integration tests, keep endpoint, domain, persistence/integration, and tests in a cohesive functional slice. In larger systems prefer cohesive end-to-end vertical slices. Allow technical prerequisites only with named consumers, a stable deliverable, and independent verification.
- **Structural:** Group file/folder moves, renames, namespace and project relocation, and required reference updates by independently movable structural unit. Preserve business behavior and public contracts; do not introduce unrelated logic changes.
- **Behavior-preserving refactoring:** Group work by coherent implementation boundary and regression coverage; preserve externally observable behavior.
- **Mixed:** Put truly necessary structural or prefactoring prerequisites before their consumers, without inventing dependencies for shared writes alone.
- Size by cohesion, context load, integration risk, stable contracts, and write ownership—not estimated duration. Keep multi-hour cohesive work with one capable implementer; merge trivial work when coordination dominates. Split at independently verifiable, stable-contract context boundaries. Shared writes require serialization, not automatic merging; disjoint write ownership is required for concurrency, not task validity. Never split solely to shorten runtime or increase concurrency, even if it appears faster.
- Give each task an included outcome, exclusions, producer contracts/assumptions, and acceptance-to-check evidence mapping. Prefer existing API integration tests for API behavior; supplement with focused contract, concurrency, retry, or boundary checks where needed. Structural work uses deterministic location/reference checks and existing regression tests.
- Type each task `HITL` (needs human interaction, e.g. architectural decision or design review) or `AFK` (implementable and mergeable without humans). Prefer AFK.
- For overlapping writes, merge tasks, move the shared edit into one task, or flag a `file` conflict for later serialization. Shared paths alone do not justify a blocker edge; add blockers only when a consumer needs the producer's integrated change to implement or verify. Independent tasks may run concurrently.

</task-decomposition-rules>

The `implement-spec` planner selects implementer models after reading the ticket graph; do not encode model preferences in ticket bodies.

Build an acyclic **blocker graph**: nodes are all tasks; each directed edge runs from blocker to dependent. Use stable slice IDs before publication, then map them to issue identities. Reject cycles and missing blocker nodes; include roots with no blockers. Identify the initial ready frontier separately; do not assign execution batches.

*Done when* every spec Functional Requirement, Business Rule, and Edge Case maps to at least one task or is flagged as uncovered.

### 4. Review the breakdown with the user

Present a numbered list; per task show:

- **Title**: short descriptive name
- **Type**: HITL | AFK
- **Blocked by**: tasks that must complete first
- **Outcome and exclusions**: bounded deliverable and out-of-scope work
- **Producer contracts/assumptions**: required inputs and unresolved evidence
- **Verification seam**: criteria-to-check mapping, commands/prerequisites, expected evidence
- **Functional Requirements covered**: spec requirement numbers addressed (full verbatim text is copied into each ticket in step 5)

Then print the blocker graph as a table `Slice | Blocked by` with one row per slice, using `none` for roots; list the initial ready frontier, anticipated write conflicts (with shared paths), uncovered requirements, and source conflicts.


Ask in ordinary conversation; **MUST NOT** use question/input tools:

- Does the granularity feel right (too coarse / too fine)?
- Are blocker edges genuine producer-consumer dependencies and acyclic? Are overlapping writes handled without artificial blocker edges?
- Should any slices be merged or split?
- Are HITL/AFK types correct?

**On correction:** apply it, recompute the blocker graph and ready frontier, print the full updated breakdown and graph, then end the turn awaiting approval. **MUST NOT** publish in the same turn as a correction.

*Done when* the user explicitly approves the current breakdown.

### 5. Publish tickets

Before any write, confirm the approval guard holds for the current breakdown; otherwise return to step 4.

Render each ticket body from [issue-template.md](./references/issue-template.md) verbatim — every section, each drafted per its `<...-rule>`. Copy each addressed requirement's spec text verbatim into **Requirements addressed**; numbers alone are insufficient.

Branch on mode:

- **Offline:** save approved bodies and the symbolic blocker graph via **Offline publishing** in [github.md](./references/github.md); skip GitHub steps below.
- **Online:**
  1. Run **Reconcile reruns** in [github.md](./references/github.md); reuse matched children, create only missing ones.
  2. Per missing slice, run **Create sub-ticket** with `parentIssueNumber` = `{{specIssueNumber}}` and label `hitl,{{repoLabel}}` (per **Label guard**).
  3. After every ticket exists, run **Link blocking** per slice with blockers: `issueNumber` = slice, `blockedBy` = its blockers' issue numbers; link only missing edges.

**Failures:**

- Label not found → follow **Labels** in [github.md](./references/github.md), then retry the failed operation once.
- Other GitHub/tool/authentication failure → stop dependent operations, report the failed operation, and preserve known issue numbers, completed/pending links, and remaining drafts via **Offline publishing**.

## Completion criteria

- **Online:** every approved task has exactly one child issue under `{{specIssueNumber}}` labeled `hitl` and `{{repoLabel}}`, no `afk` label; each body contains every template section (Contracts Delta only when a contract is touched); every approved **Blocked by** edge is a native link confirmed by reread; parent Spec unchanged. Report the final blocker graph as `Ticket | Blocked by`, with fully qualified issue identities and `none` for roots; include every ticket and confirmed edge.
- **Offline or partial:** report local paths and unpublished/partially published status; no invented GitHub issue numbers.
