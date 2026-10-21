# Plan: Durable Evidence Verifiers for Proof (TypeScript)

**Status:** Implemented on feature branch; pending review
**Repository:** `antshc/brain`  
**Target:** `plugins/proof/skills/init-proof/templates/typescript/`  
**Reference:** [Python durable-evidence plan](proof-durable-evidence-verifiers.md)  
**Scope:** TypeScript/pnpm parity for contract-first verification, durable evidence, project-owned adapters, read-only evaluation, and unchanged receipts.  
**Out of scope:** Implementing this plan, new YAML, new test framework, Loop API changes, changes to the receipt schema, or replacing live Mole commands.

## Goal

Before implementing a feature, define and review its **required verification checks** in TypeScript. The coding agent implements the feature, executes existing tests, and collects evidence from the running application. A separate **read-only Prover** evaluates those saved artifacts against stable business invariants and emits the original Proof receipt (`PASS / FAIL / ERROR`, exit codes `0 / 1 / 2`).

Project-specific collectors and adapters live in the consumer's `proof/tools/`. Proof's installed `kit/` and `mole/` remain generic and upgrade-replaceable.

**Rules**

1. MUST check named fields, membership, existence, status, and bounded counts; MUST NOT require equality of whole JSON responses by default.
2. MUST review the contract and pin its digest before implementation. A changed or weakened contract requires fresh approval and evidence.
3. MUST separate live collection from read-only evaluation. The Prover MUST NOT open Chromium, call HTTP/SQL, launch the app, or execute tests.
4. MUST preserve `Check`, `Receipt`, `Feature` compatibility, `PASS / FAIL / ERROR`, and exit codes. No extra receipt keys.
5. MUST prefer the persisted-resource GET API over a database snapshot. DB is selected only if the approved contract has no suitable read API; it is not a fallback for a failing API check.
6. MUST treat a conclusive business/test mismatch as `FAIL`; missing, stale, unparseable, or untrustworthy required evidence as `ERROR`.
7. MUST retain existing live `runProof()` behavior, surface registry (`web`, `api`), `observe()`, and strict `check()` semantics.

## Existing TypeScript integration points

| Current template path | Existing responsibility | Planned addition |
|---|---|---|
| `kit/types.ts` | `ProofKit`, `Check`, `Receipt`, `Feature` | Keep public live types; add separate evidence-evaluation types |
| `kit/run.ts` | Chromium-backed `runProof()`, strict deep equality, screenshot and revision checks | Keep unchanged behavior; share receipt/check helpers only where safe |
| `kit/features.ts` | Feature registry, selection, `touches` and surfaces | Reuse feature identity/selection; register read-only contracts without a fake browser `Page` |
| `kit/receipt.ts` | Exit codes, staleness, coverage | Reuse exactly |
| `kit/surfaces.ts` | `web`/`api`, `observe()` | Preserve: DB/logs/tests/tasks are evidence sources, **not surfaces** |
| `app/features/*.ts` | Project feature checks | Declare preimplementation evidence contracts/checks in project-owned TypeScript |
| `app/features/surfaces/*.ts` | Project routes, selectors, normalized live observations | Keep for live mode; add project collectors in `proof/tools/` |
| `mole/prove-cli.ts` | `pnpm prove` live proof | Add explicit evidence mode that bypasses Chromium |
| `mole/mole.ts`, `mole/receipts.ts` | Live app/browser lifecycle and saved receipts | Route read-only mode without `withPage()`; preserve existing history |
| `app/features.test.ts`, `mole/selftest.ts` | Node/tsx proof tests | Add contract, parser, no-side-effect, and compatibility tests |
| `scripts/scaffold.py`, `init-proof/SKILL.md`, `references/concept.md` | pnpm scaffold and usage guidance | Install/document TypeScript evidence extension points |

The current scaffold uses Node 20.12+, `pnpm`, `tsx`, strict `tsc`, and `@playwright/test`; prefer the existing Node test runner (`tsx --test`). Do not add a new test runner.

## Ownership and flow

```text
Reviewer: approve contract before code changes
        |
Versioned TypeScript contract + SHA-256
        |
Coding agent: implement, commit, run existing tests
        |
Mole/project collectors: capture real app evidence
        |
proof/.runs/<run-id>/ (immutable artifacts + evidence.json)
        |
Read-only TypeScript evaluator + generic matchers
        |
Original receipt.json + actionable next steps
```

| Owner | MUST do | MUST NOT do |
|---|---|---|
| Reviewer/feature author | Specify required check IDs and expected business invariants before implementation | Approve assertions only after seeing a passing implementation |
| Coding agent | Run relevant existing tests on the final commit; collect revision-bound evidence | Self-declare success or relax the contract for PASS |
| Mole/collectors | Interact with an approved isolated environment and save structured artifacts | Decide acceptance policy or silently replace evidence |
| Shared `kit/` | Read immutable artifacts, normalize/match values, parse reports, emit compatible receipts | Know the application's schema, credentials or infrastructure |
| Consumer `proof/tools/` | Implement project DB/API/UI/task/log collectors and custom report adapters | Require edits inside installed `kit/` or `mole/` |
| Prover | Check contract, manifest, source revision, completeness, and required checks | Drive browser/network/DB or run a test suite |

## Contract and API design

Keep the live `ProofKit` requiring Playwright `Page` unchanged. Introduce a distinct `EvidenceKit` so a read-only verifier cannot accidentally use browser methods. Reuse existing `Check` and receipt serialization. Proposed APIs, not existing code:

```ts
export type EvidenceKit = {
  evidence: EvidenceReader;
  check(name: string, actual: unknown, expected: unknown, hint?: string): void;
};

export type EvidenceContract = {
  feature: string;
  required: readonly string[];
  optional?: readonly string[];
  verify(kit: EvidenceKit): Promise<void>;
};

export interface EvidenceReader {
  json<T = unknown>(path: string): Promise<T>;
  // Loads only allowlisted, integrity-checked run artifacts.
}
```

Project-owned contracts can live in `proof/contracts/<feature>.ts`, associated with existing `FEATURES` names and feature maps. All required check names MUST be unique, declared before coding, and executed exactly once. Unknown/duplicate/missing required checks prevent PASS. A contract file/digest MUST NOT be changed during a run.

Example VPG checks:

```ts
import { matchesFields, containsItem } from "../kit";
import type { EvidenceContract } from "../kit";

export const vpgCreate: EvidenceContract = {
  feature: "vpg-create",
  required: ["vpg/api: name", "vpg/api: VM present", "vpg/task: succeeded"],
  async verify(kit) {
    const vpg = await kit.evidence.json<{ name: string; vms: { name: string }[] }>("api/get-vpg.json");
    const task = await kit.evidence.json("tasks/create-vpg.json");
    kit.check("vpg/api: name", matchesFields(vpg, { name: "TestVpg" }), true, "See api/get-vpg.json");
    kit.check("vpg/api: VM present", containsItem(vpg.vms, { name: "TestVm" }), true, "See api/get-vpg.json");
    kit.check("vpg/task: succeeded", matchesFields(task, { state: "Succeeded" }), true, "See tasks/create-vpg.json");
  },
};
```

`kit.check()` still performs **strict equality on the calculated boolean or stable normalized value**. Existing `runProof()` continues deep equality of values. Stable partial matching happens explicitly through helper functions.

### Shared matchers

Add `kit/matchers.ts`, exported through `kit/index.ts`:

| Helper | Stable rule |
|---|---|
| `matchesFields(actual, expectedSubset)` | Recursive match of named properties; ignore unrelated keys |
| `containsItem(items, expectedSubset)` | Unordered membership by subset |
| `countMatches(items, predicate, bounds)` | `equals`, `min`, `max` on a filtered collection |
| `fieldSatisfies(actual, safePath, predicate)` | Explicit typed domain predicate on a field |

MUST distinguish missing properties from `undefined`/`null`, `0` from `false`, and array order from membership. MUST reject invalid bounds and unsafe object paths. Do not coerce numbers or use fuzzy/LLM acceptance. Keep strict comparison available for explicitly exact requirements.

## Evidence selection and durability

The list ranks **directness of proving durable business behavior**, not file retention:

| Priority | Evidence | Check |
|---|---|---|
| 1 | Recorded GET resource response | Persisted VPG exists with stable fields and VM membership |
| 2 | Read-only normalized DB snapshot | Use only when suitable GET API is unavailable by contract |
| 3 | Refreshed UI list observation + screenshot | VPG appears after reload; screenshot supports review |
| 4 | Completed task record | Correct VPG-associated task has succeeded |
| 5 | Correlated application logs (when applicable) | Expected event/fields appeared during the run |
| 6 | Captured browser network request | Browser submitted method/path and selected payload fields |
| 7 | Complete browser console capture | No unexpected runtime errors for the flow |

Existing test results for the final commit are **mandatory separately**; they do not replace the persisted-resource check. A screenshot file's existence, successful task, HTTP 2xx, or empty console alone cannot prove persistence.

## Project-owned evidence adapters

Collectors MUST operate only during the collection phase. Generic interfaces belong in `kit/`, while implementations, database queries, routes, and credentials belong in the consuming repository's `proof/tools/`.

```ts
export interface DatabaseAdapter {
  getResource(kind: string, key: string): Promise<Record<string, unknown> | null>;
}

export interface LogAdapter {
  parse(input: string, source: string): LogRecord[];
}

export interface TestResultAdapter {
  parse(input: string, source: string): TestRunResult;
}
```

- Database adapters: e.g. SQL Server/PostgreSQL project modules using read-only parameterized queries and least-privilege test credentials; capture normalized JSON, not arbitrary row dumps. Never include credentials or sensitive records.
- API/task collectors: save method, endpoint identity, selected payload fields, response, task ID/correlation, time window and completeness.
- UI/browser collectors: Playwright page reload plus normalized row observation and screenshot; capture network and console from **before** the feature action through completion.
- All adapters: include run ID, capture timestamp, revision/build identity, source path, and completeness; avoid sensitive production data.

`proof/tools/` MUST be project-owned and never overwritten by scaffold upgrades. Do not widen `Surface` beyond `web | api` for these evidence sources.

## Log adapters and checks

Provide shared parsers for JSONL structured logs and OpenTelemetry-style exports; support a limited reviewed text/regex fallback. Project adapters normalize records to `{timestamp, level, event?, template?, traceId?, correlationId?, fields, source, offset}`.

Reusable read-only checks:

- `logs.eventExists`: event + selected stable fields.
- `logs.fieldsMatch`: selected typed properties, not full log records.
- `logs.noErrors`: no unexpected errors in **complete scoped** capture.
- `logs.count`: explicit event-count bounds.
- `logs.messageContains`: substring or approved regex for legacy text logs.

Require a run/correlation ID or explicitly bounded time scope and capture-completeness marker. Ignore formatting/timestamps/unrelated fields/order unless part of the contract. Complete capture missing a required event = `FAIL`; missing, truncated, stale or invalid required logs = `ERROR`. Optional logs are reported as supplementary and cannot be used to mask a failed required check.

## Existing-test report adapters

**The coding agent runs tests; the Prover only parses saved reports.** Implement `kit/test-results.ts`:

| Parser | Saved formats |
|---|---|
| `JunitAdapter` | Playwright/Jest/Vitest/JUnit-compatible XML reports |
| `TrxAdapter` | .NET/VSTest `.trx` reports for mixed-stack repositories |
| `JsonAdapter` | Explicit project-defined schema and Playwright JSON via an approved adapter |

Use a maintained, non-executing XML parser if necessary; validate namespaces, malformed XML, duplicate/retried cases, totals and result statuses deterministically. Do not evaluate JS from report files.

Normalize to `TestRunResult` with `passed`, `failed`, `skipped`, `total`, canonical test IDs, failures, report-source metadata. Shared checks: `tests.allPassed`, `tests.minimumExecuted`, `tests.requiredPresent`, `tests.noUnexpectedSkips`, `tests.matchesRevision`.

The companion test-run metadata records run ID, tested full Git SHA, test command, start/end, report hash, worktree dirty state, and trusted execution provenance. Validate required test IDs/suites declared before implementation, nonzero discovery, complete report, hash, source/build revision, and execution after final changes. Failed executed tests = `FAIL`; missing/invalid/stale/zero-test required reports = `ERROR`. No call to `pnpm test`, `npx playwright test`, subprocess, or any test runner in the evaluator.

## Run artifacts and receipt compatibility

Use JSON as an **external manifest**, not YAML and not a new receipt format:

```text
proof/.runs/<run-id>/
  evidence.json           # contract digest, Git SHA, app build, sources, hashes, completeness
  api/get-vpg.json
  tasks/create-vpg.json
  browser/vpg-list.json
  browser/vpg-list.png
  browser/network.json
  browser/console.json
  db/vpg.json              # only if API not suitable by contract
  logs/application.jsonl
  tests/results.xml
  tests/run.json
  receipt.json            # UNCHANGED original Check/Receipt shape
```

Keep all original `Receipt` keys and history semantics: `verdict`, `revision`, `app`, `at`, `checks` (`name`, `pass`, `expected`, `actual`, optional `hint`), optional `features`/`surfaces`, `pageErrors`, optional `screenshot`/`error`, and `next`. Never add `artifacts`, `tests`, `evidence`, or `UNKNOWN` to the receipt. Reference artifact paths through existing `hint`, `screenshot`, and `next`.

The manifest MUST bind evidence to a trusted authorized run, exact tested/deployed revision, preapproved contract digest, capture scope, and individual SHA-256 hashes. A self-written manifest or hash only detects changes; it is not proof of trustworthy capture. Store immutable run folders; keep prior attempts and failed artifacts. Preserve partial evidence even on `ERROR`.

## CLI behavior

1. Keep `pnpm prove` and `pnpm mole prove` unchanged when no evidence option is given.
2. Add explicit read-only mode, e.g. `pnpm prove --evidence proof/.runs/<run-id>`; route **before** API discovery, Chromium launch, session attachment or live `runProof()`.
3. Optionally route `pnpm mole prove --evidence ...` to that same evaluator without calling `withPage()`. Both entry points must return identical receipts/exit codes.
4. Evaluate exactly the preapproved feature contracts, require all selected mandatory checks, validate evidence provenance and revision, then save the usual receipt/history.
5. On required missing/stale/untrusted artifacts or contracts, return `ERROR` (exit 2); on observed mismatches/tests failed, `FAIL` (exit 1); on complete required success, `PASS` (exit 0).

## Implementation phases

### Phase 1 — Matching and contract primitives

1. Implement/export `kit/matchers.ts` with deep subset, unordered containment, count bounds and typed predicates.
2. Add `EvidenceKit`, `EvidenceContract` and required-check tracking separate from live `ProofKit`.
3. Test nested extra fields, array order, missing vs null, duplicates, type mismatches and strict live `check()` backward compatibility.

### Phase 2 — Saved evidence and collectors

4. Implement `kit/evidence.ts` for allowlisted artifact reads, hash, run/contract/revision checks, capture-completeness validation and safe relative paths.
5. Scaffold/document `proof/tools/` for project API, task, UI, browser and database collectors, never overwritten by future scaffolding.
6. Implement shared log adapters/verifiers and test correlations, missing events, malformed/truncated captures, optional logs and completeness.

### Phase 3 — Read-only evaluator and CLI

7. Implement `kit/evaluate.ts` taking contracts + saved evidence + manifest and producing the original `Receipt`.
8. Add the explicit `--evidence` branch to `mole/prove-cli.ts`, and matching Mole route if desired; no app/browser/network side effects.
9. Preserve live `runProof()`, feature selection/coverage, receipt history, strict checks and stale-build behavior. Reject absent/duplicate/unexpected required check names before PASS.

### Phase 4 — Test report parsing

10. Add JUnit, TRX, and pluggable JSON result parsers with safe normalization and stable canonical IDs.
11. Validate expected test suites/cases, counts, skips, failures, report hash, final Git SHA and capture provenance.
12. Map conclusive failures to `FAIL`, missing/invalid/stale reports to `ERROR`; prove no test command can execute in read-only mode.

### Phase 5 — Scaffold, docs and VPG example

13. Update TypeScript `app/README.md`, `init-proof/SKILL.md`, `references/concept.md`, verify-mole guidance and scaffold/self-tests.
14. Provide VPG-create contract-first example: recorded GET (or contract-approved DB), refreshed UI + screenshot, task success, browser request, clean scoped console, applicable log event, and test report.
15. Run `pnpm typecheck:proof`, `pnpm test:proof`, scaffold smoke tests (`web`, `api`, `both`), live Mole regression tests, and read-only evaluation integration tests.

## Acceptance criteria

- [ ] TypeScript feature contracts/check IDs are reviewed **before** feature implementation and their digest is pinned.
- [ ] Matching ignores unrelated JSON fields and list order without ignoring missing required values.
- [ ] Live `runProof()`, strict `check()`, `ProofKit`, feature registry, `web`/`api` surfaces, and existing Mole commands are compatible.
- [ ] Read-only evaluation does not launch Playwright, query network/DB, start apps, or execute tests.
- [ ] Project-owned DB adapters capture authorized normalized snapshots; no automatic fallback from failed GET API to DB.
- [ ] Scoped log checks support event, selected fields, counts, no-error and text fallback; incomplete evidence is ERROR.
- [ ] JUnit/TRX/project JSON parsers correctly handle failing tests, no tests, missing suites, skips, malformed data and stale results.
- [ ] Original receipt fields, `PASS / FAIL / ERROR`, exit codes `0 / 1 / 2`, coverage and history remain unchanged.
- [ ] Every required check is executed exactly once; missing evidence, changed contract or mismatched final revision prevent PASS.
- [ ] `proof/tools/` extensions survive scaffold/kit upgrades; API-only, web-only and both-surface scaffolds work.
- [ ] VPG example proves the persisted business result plus supporting UI/task/request/console/log/test observations.

## References

- [Python plan](proof-durable-evidence-verifiers.md)
- [TypeScript Proof kit](../../plugins/proof/skills/init-proof/templates/typescript/kit)
- [TypeScript Mole](../../plugins/proof/skills/init-proof/templates/typescript/mole)
- [Initialization skill](../../plugins/proof/skills/init-proof/SKILL.md)
- [Proof concept](../../plugins/proof/skills/init-proof/references/concept.md)

**Implementation boundary:** This document is a plan only. No TypeScript template code is changed by publishing it.


## Implementation notes

- `pnpm prove --evidence <run>` selects the saved-artifact evaluator before live imports.
  `pnpm mole prove` remains the live command; the optional Mole evidence alias was omitted.
- Protected project policy supplies approved digest/time, final full SHA/build and
  attestation validation. The scaffold defaults to denial. Callbacks/imports are
  trusted read-only project code; this is capability separation, not a JS sandbox.
- JSON reports use an explicit normalized schema; custom `TestResultAdapter`
  implementations handle Playwright JSON and project-specific retry policies.
- JUnit/TRX XML parsing uses `fast-xml-parser` with validation and no DTD/entities.
- Project extension guidance and a VPG contract live in the scaffold and references.
