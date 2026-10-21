# Plan: Durable Evidence Verifiers for Proof (Python)

**Status:** Proposed; not implemented  
**Repository:** `antshc/brain`  
**Target:** `plugins/proof/skills/init-proof/templates/python/`  
**Scope:** Code-first feature verification, durable evidence collection, extensible adapters, read-only evaluation, and existing receipt compatibility.  
**Out of scope:** New YAML manifests, changing the Loop public API, replacing existing tests, TypeScript parity in the first implementation.

## Goal

Require a reviewed **verification contract before feature implementation**. The coding agent implements the feature, runs the project's existing tests, and collects runtime evidence. The Prover reads that evidence and evaluates a small set of stable business invariants, producing the **original Proof receipt format**. Project-owned adapters can supply API, UI, database, task, log, and test-result observations without patching the shared kit.

**Principles**

1. **Prove business behavior, not exact data shapes.** Compare named fields, membership, presence, and bounded counts. Ignore irrelevant JSON fields, generated IDs, timestamps, and unordered list positions.
2. **Predefine the checks.** Approve a contract before coding starts. Keep a contract digest and revision in the external evidence manifest. No weakening checks during implementation merely to obtain PASS.
3. **Collect once; evaluate separately.** Evidence collection may interact with an isolated running app. The read-only Prover loads recorded artifacts, validates completeness/provenance, and compares expectations. It MUST NOT start the app, execute tests, or query a live database.
4. **Keep the original receipt.** Preserve `Check(name, passed, expected, actual, hint)`, `Receipt` JSON keys, and `PASS / FAIL / ERROR` + exit codes 0/1/2. Evidence-file references and detailed test metadata live in a companion run folder; the receipt can mention paths using existing `hint`, `screenshot`, and `next` fields.
5. **Use the strongest appropriate evidence.** Prefer resource-read APIs to database probes. Use database evidence only when no suitable verification API exists, not as an automatic retry after a failing API check.
6. **Do not hide gaps.** A conclusive mismatch is FAIL; missing, stale, incomplete, or untrustworthy required evidence is ERROR (can't tell). Missing optional evidence is reported but does not invalidate mandatory checks.

## Existing design and integration points

The Python scaffold already has these responsibilities:

| Existing file | Current role | Planned change |
|---|---|---|
| `kit/types.py` | `ProofKit`, `Check`, `Receipt`, `Feature` | Keep receipt/check serialization; expose evidence evaluation inputs without breaking legacy usage |
| `kit/run.py` | Live browser setup, `same()`, `run_proof()` | Preserve live behavior and strict `same()`; add a separate read-only evaluation flow |
| `kit/features.py` | Feature registry and selection | Reuse existing feature names, touches, and surfaces |
| `kit/receipt.py` | Exit codes, stale check, coverage | Preserve original result and coverage semantics |
| `app/features/` | Project-specific `prove` functions | Express stable checks in Python, before implementation |
| `app/features/surfaces/` | Web/API wire adapters | Continue to own routes/selectors; allow extra project-owned collectors |
| `mole/` | Browser/app lifecycle, drive commands, receipts | Provide artifact collection and read-only prove entry point without forcing test execution |
| `init-proof/SKILL.md` + `references/concept.md` | Scaffold instructions and concepts | Document contract-first collection/evaluation and compatible receipts |

Existing `run_proof()` starts Chromium, captures page errors, and invokes live feature checks. Do not silently change its default behavior. Add a distinct read-only API and route a new CLI mode to it. Migrate older commands only with explicit tests.

The original `Surface = Literal["web", "api"]` remains unchanged. Database, logs, tasks, and test results are **evidence sources/adapters**, not new user-facing surfaces.

## Architecture and ownership

```text
Author/reviewer                         Coding agent
  |                                       |
  | approve Python feature contract      | implement + commit
  | BEFORE implementation                | run existing tests
  v                                       | collect isolated app evidence
versioned feature contract               v
  |                              run artifacts (immutable)
  |                              API / DB / UI / task /
  |                              browser / logs / tests
  +---------------+-----------------------+
                  |
                  v
          Proof read-only evaluator
          shared generic matchers
          + project-specific verifiers
                  |
                  v
          Original Receipt / Check
          PASS | FAIL | ERROR
```

| Owner | MUST do | MUST NOT do |
|---|---|---|
| Feature author/reviewer | Define required checks and expected business invariants before coding | Compare entire response snapshots by default |
| Coding agent | Run tests against final code, collect complete run artifacts, record provenance | Author a self-declared PASS verdict |
| Mole / collectors | Drive approved isolated app, capture HTTP/UI/task/DB/log evidence, save artifacts | Determine required feature acceptance policy |
| Shared `kit` | Provide read-only evidence loading, matchers, parser contracts, receipt evaluation | Depend on application or project database schema |
| Project `proof/tools/` | Implement project-specific normalized evidence adapters and checks | Modify installed `proof/kit/` or `mole/` in consumer repos |
| Prover | Validate contract and evidence identity, run predeclared checks, evaluate saved tests | Run test suites, re-query live resources, relax checks |
| Workflow (e.g., Loop) | Arrange collection/evaluation and act on verdict | Override Proof verdict based on agent narrative |

## Evidence durability and selection

Rank by how directly the evidence demonstrates the desired durable outcome (not by file retention length):

| Priority | Evidence | Expected verifier behavior |
|---|---|---|
| 1 | GET resource API returns expected order | Partial JSON/business invariant matching against **recorded** response |
| 2 | Database record for the order | Normalized, read-only snapshot when **no suitable read API** exists |
| 3 | Refreshed order list with resource visible | Machine-readable UI observation + supporting screenshot after reload |
| 4 | order task completed successfully | Task status, correlation/resource association |
| 5 | Expected application log event (if applicable) | Structured event/fields with run-scoped correlation |
| 6 | Browser sent expected order request | Captured network request method/path and selected payload fields |
| 7 | No unexpected browser console errors | Complete console capture scoped to feature execution |

Also require **tests for the final commit**, separately from the strength ranking. A task success, HTTP 2xx, a screenshot alone, or the absence of console errors cannot prove persistence.

No automatic downgrade: if a GET API exists but gives incorrect results, the check fails; the Prover does not search for a passing DB snapshot instead.

## Contract shape: code first, compatible with `kit.check()`

Use the existing feature registry, Python feature functions and `kit.check(name, actual, expected, hint)`. New helpers may return booleans or stable normalized values; they MUST NOT force full payload equality. Example below is **proposed usage**, not an implemented API:

```python
from proof.kit import matches_fields, contains_item

def prove_order_create(kit):
    # Read stored artifacts; do not send HTTP or query the DB here.
    order = kit.evidence.json("api/get-order.json")
    task = kit.evidence.json("tasks/create-order.json")

    kit.check(
        "order/api: stable fields",
        matches_fields(order, {"orderNumber": "ORD-1001"}),
        True,
        "Check api/get-order.json",
    )
    kit.check(
        "order/api: line item is present",
        contains_item(order["items"], {"sku": "SKU-COFFEE", "quantity": 2}),
        True,
        "Check api/get-order.json",
    )
    kit.check(
        "order/task: succeeded",
        matches_fields(task, {"state": "Succeeded"}),
        True,
        "Check tasks/create-order.json",
    )
```

The existing `kit.check` function remains the final recording boundary. For optional/required selection, prefer project metadata associated with feature checks or a small library contract declaration rather than modifying the original `Check` JSON. Every required check must be observed exactly once or reported as missing.

### Generic matchers

Add `kit/matchers.py` and export its functions via `kit/__init__.py`:

- `matches_fields(actual, expected_subset)` — recursive subset of explicitly required dictionary fields. Unexpected keys ignored, but missing specified keys fail.
- `contains_item(items, expected_subset)` — find at least one list item satisfying partial field matching, regardless of order.
- `count_matches(items, predicate, *, min_count=None, max_count=None, equals=None)` — bounds/relations where a count is a business rule.
- `field_satisfies(actual, path, predicate)` — typed domain predicates for values not suited to equality.

Keep `same()` as the existing strict matcher for callers that explicitly need it. Make predicate behavior deterministic and testable. Distinguish false from numeric zero; type-check numeric bounds; do not quietly cast string numbers. Paths MUST be safe lookups, not arbitrary expressions. Avoid fuzzy semantic/LLM judgments as acceptance criteria.

**Durability is purposeful, not permissive.** An order number/line-item membership may be stable across implementation iterations; if a status is transient or eventually consistent, explicitly define when it can be checked and use a captured settled observation. Do not weaken actual business requirements to avoid flaky checks.

## Project-owned evidence adapters

A shared collection interface should return normalized JSON-serializable evidence and write artifact metadata. Implementations belong in consumer `proof/tools/`, not installed shared `kit/`.

```python
from typing import Protocol

class DatabaseAdapter(Protocol):
    def get_resource(self, kind: str, key: str) -> dict | None:
        """Read and normalize a resource from an authorized test database."""
        ...
```

The project implements `SqlServerOrderAdapter`, `PostgresOrderAdapter`, or domain-specific adapters. Queries MUST be read-only, parameterized, scoped to an isolated approved environment, and use least-privilege credentials. Collection stores a stable snapshot such as `{"orderNumber":"ORD-1001","items":[{"sku":"SKU-COFFEE","quantity":2}]}`; verification reads that snapshot and uses generic partial/invariant matchers. Never expose connection strings or sensitive rows in artifacts. Add a capture-time/environment/correlation record so an unrelated old DB row cannot prove a new run.

For UI, collect a normalized list-row observation and screenshot *after reload*; the image supports human review but a screenshot file's existence alone never passes an assertion. For task and browser network, save structured status/request records with correlation IDs and timestamps.

## Log adapters (new)

Log collection may use Serilog JSONL, OpenTelemetry log exports, text files, or project-specific formats. Define a project-extensible `LogAdapter` with one responsibility: parse and normalize collected log artifacts into stable records. It does not fetch live logs during read-only proof.

```python
from typing import Protocol

class LogAdapter(Protocol):
    def records(self, source: str) -> list["LogRecord"]: ...
```

Normalized `LogRecord` should expose timestamp, severity, event identifier/template (if available), trace/correlation ID, and a typed property dictionary. Preserve source offsets/paths for diagnosis.

Reusable **log verifiers**:

| Helper | Condition |
|---|---|
| `logs.event_exists` | Required structured event occurred |
| `logs.fields_match` | Event includes expected stable properties |
| `logs.no_errors` | No unexpected error records in a complete scoped capture |
| `logs.count` | Event count satisfies an explicit bound |
| `logs.message_contains` | Limited fallback for unstructured text, substring or reviewed regex |

For example:

```python
logs.event_exists(
    "logs/application.jsonl",
    event="OrderCreated",
    fields={"orderNumber": "ORD-1001"},
    correlation_id=run_id,
)
```

The example denotes a **read-only matching helper** over a saved log, not a live logger client. Ignore message formatting, timestamps, unrelated properties and log order by default. Require an approved run/correlation scope or an explicitly bounded interval with source-completeness markers; historical events must not yield false PASS. A complete relevant log capture missing the expected event is FAIL. A required truncated/unavailable/unparsable capture is ERROR, not FAIL. Optional logs are labeled supplementary; absence does not silently become success.

## Test-result parsers (new)

**The coding agent runs the tests automatically. The Prover MUST only parse existing reports.** Add reusable readers:

| Reader | Inputs |
|---|---|
| `TrxAdapter` | VSTest/`.trx` result files |
| `JUnitAdapter` | JUnit XML (pytest and compatible frameworks) |
| `JsonAdapter` | Documented project-specific structured test result schema |

Proposed typed normalized outcome:

```python
@dataclass(frozen=True)
class TestRunResult:
    passed: int
    failed: int
    skipped: int
    total: int
    test_names: list[str]
    failures: list[str]
```

Adapter responsibilities:

- Parse safely; reject malformed XML/JSON and incomplete reports instead of manufacturing success.
- Preserve canonical test IDs and test outcomes; handle TRX/JUnit namespaces, aliases, and duplicate/retried tests deterministically.
- Validate totals, test discovery (>0 for required suites), no unexpected skips, and required test IDs/suites (declared before implementation).
- Validate report hash, manifest run ID, tested Git SHA, dirty-worktree policy, and post-final-commit freshness. A report claiming the correct SHA without a trusted execution manifest is not sufficient.
- Distinguish **conclusive failed tests = FAIL** from **missing, stale or invalid reports = ERROR**.
- Do not call `dotnet test`, pytest, subprocess, a test-runner API, or another mechanism to execute test code.

Reusable helpers: `tests.all_passed`, `tests.minimum_executed`, `tests.required_present`, `tests.no_unexpected_skips`, `tests.matches_revision`. Feed results to ordinary `kit.check`; do not create a `tests` key in the receipt.

The collector saves e.g. `tests/results.trx` and `tests/run.json` containing an evidence-run ID, full tested commit SHA, command, start/end times, tracked/dirty state, and content hashes. If a revision changes after testing, recapture test results against the final revision. Build artifacts deployed for runtime verification must also match that revision.

## Evidence manifest, storage and original receipt

Suggested **companion files**, not changes to receipt JSON:

```text
proof/.runs/<run-id>/
  evidence.json            # run ID, full Git SHA, contract SHA, captures, hashes
  api/get-order.json
  tasks/create-order.json
  browser/order-list.json
  browser/order-list.png
  browser/network.har
  browser/console.json
  db/order.json               # if API unavailable by contract
  logs/application.jsonl
  tests/results.trx
  tests/run.json
  receipt.json              # original format
```

The run manifest identifies the approved contract digest, evidence provenance, capture scope, application/build revision, and completeness. Content hashes detect accidental changes; trust requires that the capture manifest comes from an authorized execution rather than a self-authored claim by the coding agent. Redact secrets, tokens and personal data. Evidence remains available for review and must not be silently overwritten; use immutable run IDs.

**Keep receipt keys and semantics exactly as currently defined:**

```json
{
  "verdict": "PASS",
  "revision": "abc123",
  "app": "shop",
  "at": "2026-10-21T12:00:00Z",
  "checks": [
    {
      "name": "order/api: order number",
      "pass": true,
      "expected": "ORD-1001",
      "actual": "ORD-1001",
      "hint": "See api/get-order.json"
    },
    {
      "name": "tests: results match commit",
      "pass": true,
      "expected": true,
      "actual": true,
      "hint": "See tests/results.trx and tests/run.json"
    }
  ],
  "features": ["order-create"],
  "surfaces": ["web", "api"],
  "pageErrors": [],
  "screenshot": "browser/order-list.png",
  "next": ["These checks passed on this revision."]
}
```

`hint` remains optional as in the original serializer; the example includes it to link reviewable evidence. The original fields `error` (when applicable) and receipt storage/history behavior remain supported. Do not insert new `tests`, `artifacts`, `evidence`, or `UNKNOWN` fields into `Receipt.to_json()`. Use `ERROR` to represent can't-tell outcomes and keep exit code 2.

For missing **required** artifacts or failed provenance validation, set `receipt.verdict = "ERROR"` and populate the original `error` and `next` fields without writing misleading passing checks. For actual observed invariant mismatches, record a failed check; final verdict FAIL. Persist partial observations on ERROR so reviewers can troubleshoot.

## Implementation phases

### Phase 1 — Stable generic matching

1. Add `kit/matchers.py` with partial object matching, unordered containment, count bounds and safe predicates.
2. Export helpers through `kit/__init__.py`; retain `same()` exact equality for existing consumers.
3. Add unit tests for extra keys, reordering, missing required fields, duplicate elements, incorrect types, null vs absent, bounds and nested values.

### Phase 2 — Evidence loading, project adapters and log parsing

4. Add `kit/evidence.py` for saved evidence and manifest verification, content hashes, revision identity and capture completeness.
5. Document/project-scaffold `proof/tools/` extension points for normalized SQL Server/PostgreSQL/custom DB, API/UI/task/browser and log records.
6. Implement reusable log parsing/matching and project-supplied log schema adapters; test structured JSONL, OTel, plain text, correlation isolation, incomplete/truncated logs and no-error semantics.
7. Ensure the scaffold treats `proof/tools/` as **project-owned** and never overwrites project extensions.

### Phase 3 — Separate read-only Proof evaluation

8. Add `kit/evaluate.py`: selected contracts + recorded evidence + immutable manifest -> unchanged `Receipt`.
9. Add a read-only CLI mode to the existing Mole commands/entry point. It reads evidence and evaluates contracts but MUST NOT invoke app startup, browser launch, HTTP/SQL clients or test runners.
10. Preserve `run_proof()`, live Mole drive/prove commands, and existing receipt history for backward compatibility. Distinguish observed failures from missing-evidence ERROR consistently.
11. Detect missing required checks, changed contract digest, stale build revision and incomplete artifact sets before PASS.

### Phase 4 — Test report parsing and receipt integration

12. Add `kit/test_results.py` with `TrxAdapter`, `JUnitAdapter` and a project `JsonAdapter` interface.
13. Add common required-test, discovery, revision and skip validation checks.
14. Feed test results into original `kit.check()` and original receipt; preserve `PASS/FAIL/ERROR` and exit codes.
15. Verify clean success, failed test, zero discovered, unexpected skip, incomplete XML, stale SHA, wrong run ID and missing required suite. Assert that Prover NEVER executes the tests.

### Phase 5 — Skill/template updates and end-to-end example

16. Update `init-proof/SKILL.md`, `references/concept.md`, Python template READMEs, `verify-mole` skill scaffolding and scaffold/self-tests.
17. Add an order-create example with predeclared invariant checks: persisted API (or approved DB alternative), refreshed-list screenshot, successful task, browser request, clean console, applicable correlated log, and test report.
18. Run template tests, Python type checks, scaffold smoke tests, old Mole command regression tests, and new read-only evaluation integration tests.
19. Document what is reviewed before coding, collection command responsibilities, evidence retention, and how to extend per-project adapters without changing `kit/`.

## Acceptance criteria

- [ ] Feature verification contracts are defined/reviewed before feature implementation and pinned in run evidence.
- [ ] Extra JSON properties and array reordering do not fail stable subset checks; absent required properties do.
- [ ] The old strict matcher, live `run_proof()`, existing feature registry and surface selection still work.
- [ ] SQL Server/PostgreSQL project-owned adapters emit normalized **saved** snapshots; read-only Prover cannot query the DB.
- [ ] Log matchers support structured events/fields, scoped no-error checks, bounded counts and plain-text fallback.
- [ ] Missing, truncated, stale or unparseable required logs produce ERROR; complete logs missing a required event produce FAIL.
- [ ] TRX/JUnit/JSON readers normalize test results and validate discovery, required tests, skips, provenance and revision.
- [ ] Tests are run by the coding agent on the final implementation, NEVER by the Prover.
- [ ] Failed required tests produce FAIL; missing/invalid/stale reports produce ERROR.
- [ ] Original `Receipt` and `Check` JSON schemas, exit codes, and append-only receipt history remain unchanged.
- [ ] Evidence cannot be falsely accepted from a different build/run; mandatory evidence gaps prevent PASS.
- [ ] Order example exercises the API-preferred/DB-only-if-unavailable rule, refreshed UI evidence, task, browser, console, logs, and test outcomes.
- [ ] Consumer-specific extensions remain outside upgrade-replaced `proof/kit/` and `mole/` folders.

## References

- [Python Proof template](../../plugins/proof/skills/init-proof/templates/python)
- [Proof concept](../../plugins/proof/skills/init-proof/references/concept.md)
- [Proof initialization skill](../../plugins/proof/skills/init-proof/SKILL.md)

**Implementation boundary:** This is a plan; do not modify implementation files as part of publication.
