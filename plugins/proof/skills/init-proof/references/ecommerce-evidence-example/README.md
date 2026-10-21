# E-commerce order contract-first example

Copy `order-create.ts` to `proof/contracts/`, register the contract, and associate
`order-create` with the existing FEATURES identity/map. Adapt stable values and
correlation scope before review. The example proves a confirmed order containing
two units of `SKU-COFFEE`, its completed processing task, refreshed order list,
order submission request, clean console and correlated `OrderCreated` event. For API-only projects omit UI/browser checks
before approval; keep persisted GET and tests mandatory. If no read API exists,
review a DB source with `resource.kind: "db"`, a normalized snapshot path and
`noReadApiReason`; never select DB because a GET check failed.

1. Approve check IDs, expectations, test IDs/suites, sources and dependency digests.
2. Implement and commit; run existing tests on the clean final full Git SHA.
3. Authorized project collectors capture the real app to a fresh immutable run.
4. Externally attest the manifest, artifact hashes, app build, scopes, complete
   capture and test execution provenance. Pin final revision/build outside the run.
5. Run `pnpm prove --evidence proof/.runs/<run-id>`. Retain every failed attempt.

Required artifacts: `api/get-order.json`, `tasks/create-order.json`,
`browser/order-list.json`, `browser/order-list.png`, `browser/network.json`,
`browser/console.json`, `logs/scope.json`, `logs/application.jsonl`,
`tests/results.xml`, `tests/run.json`, `evidence.json`. Each is allowlisted,
hashed, revision/build/run-bound, timestamped and marked complete in the manifest.
Console/network capture starts before the action; the collector's attestation
binds this interval and correlation. `scope.json` is complete and correlated or
has an explicit bounded time window. A missing event in a complete valid scoped
capture fails; malformed/truncated/untrusted capture errors.

Tests are checked automatically by the evaluator using the preapproved policy.
The screenshot is supporting evidence; its existence alone proves nothing.
The example is not installed as a passing fake feature by scaffold.
