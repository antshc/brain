import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink, cp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { matchesFields, containsItem, countMatches, fieldSatisfies } from "./kit/matchers";
import { evaluateEvidence } from "./kit/evaluate";
import { sha256, contractDigest, safePath } from "./kit/evidence";
import { JunitAdapter, TrxAdapter, JsonAdapter } from "./kit/test-results";
import { JsonlLogAdapter, OtelLogAdapter, scopedLogs, logs } from "./kit/logs";
import { exitCode } from "./kit/receipt";
import type { EvidenceContract, EvidenceManifest, EvidencePolicy } from "./kit/evidence-types";

test("Stable matching preserves types, missing values and exact arrays", () => {
  assert.ok(matchesFields({ nested: { n: 0, extra: 1 } }, { nested: { n: 0 } }));
  assert.ok(!matchesFields({}, { n: undefined }));
  assert.ok(!matchesFields({ n: null }, { n: undefined }));
  assert.ok(!matchesFields({ n: false }, { n: 0 }));
  assert.ok(!matchesFields({ xs: [2, 1] }, { xs: [1, 2] }));
  assert.ok(!matchesFields(Object.create({ n: 1 }), { n: 1 }));
  assert.ok(containsItem([{ n: 2 }, { n: 1, other: true }], { n: 1 }));
  assert.ok(countMatches([1, 2, 2], n => n === 2, { min: 1, max: 2 }));
  assert.throws(() => countMatches([], () => true, { min: 2, max: 1 }));
  assert.throws(() => countMatches([], () => true, { equals: 1, min: 0 }));
  assert.throws(() => countMatches([], () => true, { min: NaN }));
  assert.ok(fieldSatisfies({ n: 0 }, ["n"], n => n === 0));
  assert.ok(!fieldSatisfies({}, ["n"], n => n === undefined));
  assert.throws(() => fieldSatisfies({}, ["__proto__"], () => true));
  for (const path of ["../x", "/x", "a/../b", "a\\b", "C:/x", "a//b"]) assert.throws(() => safePath(path));
});

async function fixture() {
  const root = await mkdtemp(join(tmpdir(), "proof-evidence-"));
  const runDir = join(root, "run"); await mkdir(runDir);
  const revision = "a".repeat(40), build = "build-1", runId = "run-1";
  const startedAt = "2025-01-01T00:00:00Z", endedAt = "2025-01-01T00:01:00Z";
  await writeFile(join(root, "contract.ts"), "approved contract");
  const modules = [{ path: "contract.ts", sha256: sha256("approved contract") }];
  const digest = await contractDigest(root, modules);
  const report = '<testsuite name="suite" tests="1" failures="0"><testcase classname="C" name="persists"/></testsuite>';
  const metadata = { runId, revision, build, command: "existing test command", startedAt, endedAt, reportHash: sha256(report), dirty: false, complete: true, provenance: { executor: "authorized CI" } };
  const manifest: EvidenceManifest = { runId, revision, build, startedAt, endedAt, contractDigest: digest, artifacts: {}, provenance: "external attestation" };
  const save = async (path: string, value: string, kind: EvidenceManifest["artifacts"][string]["kind"]) => {
    await writeFile(join(runDir, path), value);
    manifest.artifacts[path] = { runId, revision, build, capturedAt: endedAt, complete: true, kind, sha256: sha256(value) };
  };
  await save("resource.json", JSON.stringify({ name: "TestVpg", extra: 1 }), "api");
  await save("report.xml", report, "tests"); await save("test-run.json", JSON.stringify(metadata), "metadata");
  const policy: EvidencePolicy = { revision, build, modules, contractDigest: digest, approvedAt: "2024-12-31T00:00:00Z",
    tests: { report: "report.xml", metadata: "test-run.json", format: "junit", requiredIds: ["suite::C::persists"], requiredSuites: ["suite"], allowedSkips: [] },
    async authorize(m) { return m.provenance === "external attestation"; } };
  const contract: EvidenceContract = { feature: "vpg", required: ["vpg/name"], surfaces: ["api"], resource: { path: "resource.json", kind: "api" },
    async verify(k) { const value = await k.evidence.json("resource.json"); k.check("vpg/name", matchesFields(value, { name: "TestVpg" }), true); } };
  const evaluate = async () => {
    await writeFile(join(runDir, "evidence.json"), JSON.stringify(manifest));
    return evaluateEvidence({ root, runDir, app: "test", policy, contracts: [contract] });
  };
  return { root, runDir, policy, manifest, contract, save, evaluate, cleanup: () => rm(root, { recursive: true, force: true }) };
}

test("Read-only evaluation produces unchanged PASS receipt without network/browser/tests", async () => {
  const f = await fixture(); const fetch = globalThis.fetch;
  globalThis.fetch = () => { throw new Error("Network forbidden"); };
  try {
    const receipt = await f.evaluate(); assert.equal(receipt.verdict, "PASS"); assert.equal(exitCode(receipt), 0);
    assert.deepEqual(Object.keys(receipt).sort(), ["verdict", "revision", "app", "at", "checks", "pageErrors", "next", "features", "surfaces"].sort());
    assert.deepEqual(receipt.features, ["vpg"]); assert.deepEqual(receipt.surfaces, ["api"]);
  } finally { globalThis.fetch = fetch; await f.cleanup(); }
});

for (const [name, mutate] of Object.entries<(f: Awaited<ReturnType<typeof fixture>>) => Promise<void> | void>({
  "business mismatch": f => f.save("resource.json", '{"name":"wrong"}', "api"),
  "failed executed tests": f => f.save("report.xml", '<testsuite name="suite" tests="1" failures="1"><testcase classname="C" name="persists"><failure>bug</failure></testcase></testsuite>', "tests"),
})) test(`${name} is FAIL`, async () => {
  const f = await fixture(); try {
    await mutate(f);
    if (name.includes("tests")) {
      const metadata = JSON.parse(await readFile(join(f.runDir, "test-run.json"), "utf8"));
      metadata.reportHash = f.manifest.artifacts["report.xml"].sha256;
      await f.save("test-run.json", JSON.stringify(metadata), "metadata");
    }
    const receipt = await f.evaluate(); assert.equal(receipt.verdict, "FAIL", receipt.error ?? "Unexpected verdict"); assert.equal(exitCode(receipt), 1);
  } finally { await f.cleanup(); }
});

const errors: Record<string, (f: Awaited<ReturnType<typeof fixture>>) => Promise<void> | void> = {
  "untrusted run": f => { f.manifest.provenance = "self-written"; },
  "stale revision": f => { f.manifest.revision = "b".repeat(40); },
  "stale build": f => { f.manifest.build = "old"; },
  "changed approval": f => { f.manifest.contractDigest = "b".repeat(64); },
  "late approval": f => { f.policy.approvedAt = "2025-01-02T00:00:00Z"; },
  "changed contract": f => writeFile(join(f.root, "contract.ts"), "weakened"),
  "tampered resource": f => writeFile(join(f.runDir, "resource.json"), "{}"),
  "incomplete capture": f => { f.manifest.artifacts["resource.json"].complete = false; },
  "stale capture": f => { f.manifest.artifacts["resource.json"].capturedAt = "2024-01-01T00:00:00Z"; },
  "missing required check": f => { f.contract.required = ["vpg/name", "missing"]; },
  "unknown check caught by contract": f => { f.contract.verify = async k => { await k.evidence.json("resource.json"); try { k.check("unknown", true, true); } catch {} k.check("vpg/name", true, true); }; },
  "duplicate check": f => { f.contract.verify = async k => { await k.evidence.json("resource.json"); k.check("vpg/name", true, true); k.check("vpg/name", true, true); }; },
  "unread persisted resource": f => { f.contract.verify = async k => k.check("vpg/name", true, true); },
  "DB fallback without approval": f => { f.contract.resource.kind = "db"; },
  "missing required test": f => { f.policy.tests.requiredIds = ["missing"]; },
  "missing required suite": f => { f.policy.tests.requiredSuites = ["missing"]; },
  "unapproved test selection": f => { f.policy.tests.requiredIds = []; f.policy.tests.requiredSuites = []; },
  "malformed test report": f => f.save("report.xml", '<testsuite>', "tests"),
  "empty test report": f => f.save("report.xml", '<testsuite tests="0"/>', "tests"),
  "symlink escapes run": async f => { await writeFile(join(f.root, "outside"), '{}'); await rm(join(f.runDir, "resource.json")); await symlink(join(f.root, "outside"), join(f.runDir, "resource.json")); },
  "unallowlisted read": f => { f.contract.verify = async k => { await k.evidence.json("not-listed.json"); }; },
};
for (const [name, mutate] of Object.entries(errors)) test(`${name} is ERROR`, async () => {
  const f = await fixture(); try { await mutate(f); const receipt = await f.evaluate(); assert.equal(receipt.verdict, "ERROR"); assert.ok(receipt.error); assert.equal(exitCode(receipt), 2); }
  finally { await f.cleanup(); }
});

test("JUnit handles namespaces, nested totals and rejects malformed, duplicate and retried cases", () => {
  const adapter = new JunitAdapter();
  const r = adapter.parse('<j:testsuites xmlns:j="urn:junit" tests="2"><j:testsuite name="s"><j:testcase name="a"/><j:testcase name="b"><j:skipped/></j:testcase></j:testsuite></j:testsuites>', "junit");
  assert.equal(r.passed, 1); assert.equal(r.skipped, 1);
  for (const xml of ['<testsuite>', '<!DOCTYPE x><testsuite/>', '<testsuite name="s" tests="5"><testcase name="a"/></testsuite>', '<testsuite name="s"><testcase name="a"/><testcase name="a"/></testsuite>', '<testsuite name="s"><testcase name="a"><flakyFailure/></testcase></testsuite>']) assert.throws(() => adapter.parse(xml, "junit"));
});
test("TRX validates namespace, totals, statuses and stable IDs", () => {
  const xml = '<TestRun xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010"><TestDefinitions><UnitTest id="id"><TestMethod className="Suite"/></UnitTest></TestDefinitions><Results><UnitTestResult testId="id" outcome="Passed"/></Results><ResultSummary outcome="Completed"><Counters total="1" passed="1" failed="0" notExecuted="0" executed="1"/></ResultSummary></TestRun>';
  assert.equal(new TrxAdapter().parse(xml, "trx").cases[0].id, "id");
  assert.throws(() => new TrxAdapter().parse(xml.replace('outcome="Passed"', 'outcome="InProgress"'), "trx"));
  assert.throws(() => new TrxAdapter().parse(xml.replace('total="1"', 'total="2"'), "trx"));
});
test("JSON reports require explicit schema and consistent totals", () => {
  const input = { complete: true, cases: [{ id: "id", suite: "s", status: "passed" }], total: 1, passed: 1, failed: 0, skipped: 0 };
  assert.equal(new JsonAdapter().parse(JSON.stringify(input), "json").passed, 1);
  assert.throws(() => new JsonAdapter().parse(JSON.stringify({ ...input, passed: 2 }), "json"));
  assert.throws(() => new JsonAdapter().parse('{}', "json"));
});
test("Logs require complete scope and match stable correlated fields", () => {
  const adapter = new JsonlLogAdapter();
  const records = adapter.parse(JSON.stringify({ timestamp: "2025-01-01T00:00:00Z", level: "INFO", event: "Created", correlationId: "run", fields: { name: "vpg", extra: 1 } }), "logs");
  const scoped = scopedLogs(records, { complete: true, correlationId: "run" });
  assert.ok(logs.eventExists(scoped, "Created", { name: "vpg" })); assert.ok(logs.noErrors(scoped));
  assert.ok(!logs.eventExists(scopedLogs(records, { complete: true, correlationId: "other" }), "Created"));
  assert.ok(logs.count(scoped, "Created", { equals: 1 }));
  assert.throws(() => scopedLogs(records, { complete: false, correlationId: "run" }));
  assert.throws(() => scopedLogs(records, { complete: true }));
  assert.throws(() => adapter.parse('{broken', "logs"));
  const otel = { resourceLogs: [{ scopeLogs: [{ logRecords: [{ timeUnixNano: "1735689600000000000", severityNumber: 17, body: { stringValue: "bad" }, attributes: [] }] }] }] };
  assert.ok(!logs.noErrors(scopedLogs(new OtelLogAdapter().parse(JSON.stringify(otel), "otel"), { complete: true, start: "2025-01-01T00:00:00Z", end: "2025-01-01T00:01:00Z" })));
});


test("Live runProof keeps strict equality and revision staleness", async () => {
  const { runProof } = await import("./kit/run");
  let closed = false;
  const page = { setDefaultTimeout() {}, on() {} };
  const browser = { async newContext() { return { async newPage() { return page; }, async close() { closed = true; } }; } };
  const receipt = await runProof(browser as never, "test", async kit => {
    kit.check("exact object", { x: 1, extra: true }, { x: 1 });
    kit.check("exact type", 0, false);
  }, { surfaces: ["api"], revision: async () => "same" });
  assert.equal(receipt.verdict, "FAIL"); assert.ok(receipt.checks.every(c => !c.pass)); assert.ok(closed);
  let n = 0;
  const stale = await runProof(browser as never, "test", async k => k.check("fact", true, true), { surfaces: ["api"], revision: async () => String(n++) });
  assert.equal(stale.verdict, "ERROR");
});

for (const field of ["revision", "dirty", "complete", "provenance", "endedAt"]) test(`Invalid test metadata ${field} is ERROR`, async () => {
  const f = await fixture(); try {
    const metadata = JSON.parse(await readFile(join(f.runDir, "test-run.json"), "utf8"));
    metadata[field] = ({ revision: "b".repeat(40), dirty: true, complete: false, provenance: null, endedAt: "2024-01-01T00:00:00Z" } as Record<string, unknown>)[field];
    await f.save("test-run.json", JSON.stringify(metadata), "metadata");
    assert.equal((await f.evaluate()).verdict, "ERROR");
  } finally { await f.cleanup(); }
});

test("Evidence CLI passes without importing live app, features, runtime or browser", async () => {
  const { spawnSync } = await import("node:child_process");
  const f = await fixture(); try {
    await mkdir(join(f.root, "proof/contracts"), { recursive: true });
    await mkdir(join(f.root, "mole"));
    await cp(join(process.cwd(), "proof/kit"), join(f.root, "proof/kit"), { recursive: true });
    for (const file of ["prove-cli.ts", "evidence-cli.ts"]) await cp(join(process.cwd(), "mole", file), join(f.root, "mole", file));
    for (const file of ["proof/app.ts", "proof/features.ts", "mole/runtime.ts", "mole/prove-live.ts"]) await writeFile(join(f.root, file), 'throw new Error("FORBIDDEN live import");');
    await symlink(join(process.cwd(), "node_modules"), join(f.root, "node_modules"));
    await writeFile(join(f.root, "package.json"), '{"type":"module"}');
    const module = `export const CONTRACTS = [{ feature: "vpg", surfaces: ["api"], required: ["vpg/name"], resource: {path:"resource.json", kind:"api"}, async verify(k) { const r = await k.evidence.json("resource.json"); k.check("vpg/name", r.name, "TestVpg"); } }];`;
    await writeFile(join(f.root, "proof/contracts/index.ts"), module);
    f.policy.modules = [{ path: "proof/contracts/index.ts", sha256: sha256(module) }];
    f.policy.contractDigest = await contractDigest(f.root, f.policy.modules);
    f.manifest.contractDigest = f.policy.contractDigest;
    await writeFile(join(f.root, "proof/evidence-config.ts"), `export const EVIDENCE_APP = "test"; export const EVIDENCE_POLICY = { ...${JSON.stringify(f.policy)}, async authorize(m) { return m.provenance === "external attestation"; } };`);
    await writeFile(join(f.runDir, "evidence.json"), JSON.stringify(f.manifest));
    const run = () => spawnSync(process.execPath, ["--import", "tsx", "mole/prove-cli.ts", "--evidence", f.runDir], { cwd: f.root, encoding: "utf8", timeout: 30000 });
    const first = run(); assert.equal(first.status, 0, first.stderr); assert.equal(JSON.parse(first.stdout).verdict, "PASS");
    const second = run(); assert.equal(second.status, 0, second.stderr);
    const { readdir } = await import("node:fs/promises");
    assert.equal((await readdir(join(f.root, "proof/.runs/receipts"))).length, 2);
    assert.equal(JSON.parse(await readFile(join(f.root, "proof/.runs/last-receipt.json"), "utf8")).verdict, "PASS");
    await writeFile(join(f.runDir, "resource.json"), "{}");
    const bad = run(); assert.equal(bad.status, 2); assert.equal(JSON.parse(bad.stdout).verdict, "ERROR");
  } finally { await f.cleanup(); }
});


test("Approved database snapshot uses a declared no-read-API reason", async () => {
  const f = await fixture(); try {
    f.contract.resource = { path: "resource.json", kind: "db", noReadApiReason: "No resource read endpoint exists" };
    f.manifest.artifacts["resource.json"].kind = "db";
    assert.equal((await f.evaluate()).verdict, "PASS");
  } finally { await f.cleanup(); }
});
test("Contract changes during evaluation cannot pass", async () => {
  const f = await fixture(); try {
    const verify = f.contract.verify;
    f.contract.verify = async k => { await verify(k); await writeFile(join(f.root, "contract.ts"), "changed"); };
    assert.equal((await f.evaluate()).verdict, "ERROR");
  } finally { await f.cleanup(); }
});
test("Optional observations cannot mask a failed required check", async () => {
  const f = await fixture(); try {
    f.contract.optional = ["extra"];
    f.contract.verify = async k => { await k.evidence.json("resource.json"); k.check("vpg/name", false, true); k.check("extra", true, true); };
    assert.equal((await f.evaluate()).verdict, "FAIL");
  } finally { await f.cleanup(); }
});
