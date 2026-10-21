# Project evidence extensions

This folder belongs to the project. Scaffold reruns skip existing files; keep custom adapters here, outside upgrade-replaced `proof/kit/` and `mole/`.

1. Before implementing a feature, review its `Contract`: named mandatory checks, artifacts, test IDs, business constants, surface names and evidence sources. Use the same feature names as the live registry. Register in `contracts.py`. `vpg_example.py` is an opt-in example; adapt routes and schema before use.
2. Commit the approved contract. Record `contract_digest(Path('proof'))` through a trusted workflow. It hashes relative paths and contents of all Python files under `proof/`; include imports outside that tree in the project's review/pinning policy. Do not weaken checks during implementation. A contract change requires review and a new digest.
3. Implement and commit the feature. The coding agent/workflow runs existing tests on the clean final commit, records the full Git SHA, command, start/end times, dirty state and report hash in `tests/run.json`. Rebuild/deploy that revision; do not infer the deployed revision merely from the current source checkout.
4. An authorized collector drives the isolated app and saves observations with `Capture`. It verifies the clean checkout and build identities, strips secrets and writes complete run-scoped captures. Use fresh immutable run directories; never reuse old resource snapshots. Required screenshots accompany structured post-reload UI observations. A screenshot alone cannot prove persistence.
5. The workflow retains the `Capture.finish()` digest outside the artifact folder and invokes `mole evaluate`. Never accept that digest from the coding agent's narrative or from a sidecar in the same untrusted folder. A hash is integrity, not authentication. The workflow authenticates the collector and approved contract; this library does not provision credentials or signatures.
6. Keep run artifacts and append-only receipts under the project's retention policy (for example upload the entire run as a CI artifact). Redact secrets/tokens and personal data before hashing. Recapture after any source/build change.

```python
from pathlib import Path
from proof.kit.capture import Capture

# Values are supplied/verified by the trusted workflow, not copied from a report.
capture = Capture(Path('proof/.runs/unique-id'), run_id='unique-id',
    revision=final_sha, build_revision=deployed_sha,
    contract_sha256=approved_digest, environment='isolated-ci')
# Project collectors perform actual API/UI/DB/log collection here.
capture.add('api/get-vpg.json', normalized_response_bytes)
# Add every required artifact, then hand the digest to the workflow securely.
manifest_digest = capture.finish()
```

`Capture.add()` timestamps collection. Copy reports/logs promptly during the run, preserving original execution times in `tests/run.json` and log records. Do not label truncated captures complete. Capture only records bytes and provenance; it never produces a verdict.

`DatabaseAdapter.get_resource()` is a collection seam. `database.py` shows parameterized SQL Server/PostgreSQL queries against an example schema. Supply a read-only, least-privilege connection to the approved isolated environment; adapt schema here. Never serialize credentials or unrelated rows. Use DB only when the preapproved contract has no suitable read API. An incorrect API result remains FAIL.

`LogAdapter.parse()` and `ResultAdapter.parse()` are pure offline seams. Built-ins support normalized/Serilog JSONL, OTLP JSON, explicit text parsing, TRX, JUnit and documented JSON test results. Unsupported schemas or retries require a deterministic project adapter; built-ins reject duplicate test IDs rather than choosing a passing retry. JUnit IDs use `classname.name` (or `name`); TRX uses `testId`. Namespace-qualified XML is accepted; DTD/entities are rejected.

Read log files via `evidence.text()` before parsing so missing, incomplete or tampered captures cause ERROR. Use `LogView` with the approved correlation ID; for text without IDs, the collector must isolate the source and `TextAdapter` assigns that scope. Missing expected events in complete scoped captures are FAIL. A no-error check needs complete capture and explicit severity parsing; do not label unknown severity as Information.

Use `matches_fields`, `contains_item`, `count_matches` and `field_satisfies` for stable invariants. Nested dicts are subsets; list equality stays strict unless explicitly using containment. `same()` retains strict comparison. Missing required values fail; booleans do not equal numeric zero/one. Predicates must return booleans and safe paths contain field names/list indices, never expressions.

`check_results()` validates the saved execution manifest, report hash, revision/run, interval, discovered required IDs, failures and skip policy. Zero discovered or missing required IDs = ERROR; observed failing tests or unexpected skips = FAIL. It never runs tests. `all_passed()` requires nonzero tests, no failures and no skips; use the explicit skip helper when skips are preapproved.

Contracts are trusted reviewed Python, not sandboxed programs. Keep their imports and callbacks pure: no app startup, HTTP/SQL, browser, subprocess or test execution. The evaluator itself only reads artifacts and records checks; enforce OS/process restrictions in the workflow when evaluating untrusted project code. `Evidence.optional()` reports missing supplementary captures in receipt next steps; it never makes a required artifact optional.
