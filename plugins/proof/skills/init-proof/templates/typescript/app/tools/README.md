# Project evidence tools

This folder belongs to the consuming project. Scaffold never overwrites it.
Keep API/task/UI/browser/database collectors and custom log/test adapters here.
Do not edit installed `kit/` or `mole/` to add project behavior.

Collectors run separately before evaluation, against an authorized isolated app.
Use read-only parameterized DB queries only when the approved contract explains
why no suitable GET API exists. A failed GET check must never fall back to DB.
Capture browser requests/console before the action until completion; reload UI
before recording rows and screenshots. Redact credentials and sensitive data.

Each immutable `proof/.runs/<run-id>/evidence.json` contains:

- `runId`, full `revision`, `build`, `startedAt`, `endedAt`, `contractDigest`, external `provenance`.
- `artifacts`: relative path -> `sha256`, `runId`, `revision`, `build`, `capturedAt`, `complete`, `kind`.
- Kinds: `api`, `db`, `ui`, `task`, `logs`, `network`, `console`, `tests`, `metadata`, `screenshot`.

The authorized collector must attest completeness and correlation/time scopes;
hashes only detect changes. Keep every attempt, including partial failures.
For logs, save a scope JSON with `complete` plus `correlationId`, `traceId` or
`start`/`end`, and call `scopedLogs()` before shared log checks.

Run existing tests on the clean final commit; save reports plus `tests/run.json`:
`runId`, full `revision`, `build`, `command`, `startedAt`, `endedAt`, `reportHash`,
`dirty: false`, `complete: true`, trusted execution `provenance`.
The project's authorize policy must validate that provenance, not just its presence.
JUnit canonical IDs are `suite::classname::name`; TRX uses `testId`.
JSON reports explicitly contain `complete: true`, `cases` (`id`, `suite`,
`status: passed|failed|skipped`, optional `failure`) and matching
`passed`, `failed`, `skipped`, `total` counts. Custom adapters normalize other
formats (including Playwright JSON) and must resolve retries explicitly.
Export `EVIDENCE_JSON_ADAPTER` from `proof/evidence-config.ts` for CLI evaluation
of an approved custom JSON schema; include its module in the approval pins.

Copy the VPG example from the init-proof reference, adapt real domain fields,
and register it in `proof/contracts/index.ts`. Approve IDs, expected values,
required test suites/IDs, and source selection before coding. Include the registry,
contracts, tools used by contracts, and test/trust policy dependencies in
`EVIDENCE_POLICY.modules`. Each entry pins its file SHA-256; `contractDigest()`
hashes sorted `[path, sha256]` pairs. Store the approved aggregate digest and
approval time in protected reviewer/CI configuration. Reapproval and fresh
evidence are required after any policy change.

Configure `proof/evidence-config.ts` with that externally approved policy and
expected final full Git SHA/build. Default configuration refuses all evidence.
`pnpm prove --evidence proof/.runs/<run-id> [--feature NAME]` reads artifacts,
emits the original receipt and exits 0/1/2. It never invokes collectors or tests.
Contracts/adapters/policy are trusted read-only TypeScript, not a sandbox;
review their imports too. Do not import live app/surface modules into them.
The external runner must verify the checkout and deployed build; evaluator does
not run Git or infer the current revision from an untrusted manifest.
