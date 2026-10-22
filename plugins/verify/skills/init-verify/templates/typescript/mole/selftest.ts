// Keeps the registry, the feature maps and the app config in step, and pins the rules a verdict must follow. Run with: pnpm test:proof
// Add your own adapter, flow and check tests to proof/features.test.ts; this file belongs to the mole and is replaced on upgrade.
import assert from "node:assert/strict";
import { test } from "node:test";
import type { Page } from "@playwright/test";
import { ADAPTERS } from "../proof/adapters";
import { APP } from "../proof/app";
import { FEATURES } from "../proof/features";
import {
  ALL_SURFACES, Failure, aggregate, buildRegistry, builtinAdapters, checkMaps, defineFeature, defineFlow, defineProof, exitCode, mergeAdapters,
  parseMap, runScenario, runScenarios, selectScenarios, type ArtifactStore, type EvidenceAdapter, type RunHost,
} from "../proof/kit";
import { loadMaps } from "./maps";

const BANNED = [/localStorage/, /querySelector/, /page\.locator/, /getByRole/, ...(APP.mapBanned ?? [])];

test("app config names a supported set of surfaces", () => {
  assert.ok(APP.surfaces.length > 0, "APP.surfaces is empty");
  for (const surface of APP.surfaces) assert.ok(ALL_SURFACES.includes(surface), `APP.surfaces has the unknown surface "${surface}"`);
  assert.ok(APP.sourcePaths.length > 0, "APP.sourcePaths is empty: the revision would cover the whole repo");
});

test("the registry is valid and its maps are in step with its builders", async () => {
  const registry = buildRegistry(FEATURES, mergeAdapters(builtinAdapters(), ADAPTERS));
  assert.ok(registry.scenarios.length > 0, "no scenarios");
  assert.deepEqual(checkMaps(registry, await loadMaps(), BANNED), []);
});

// A tiny map: four sections, a bullet per sub-feature, one unbulleted paragraph per scenario.
const MAP = (paragraph: string) => `# Cart

## Sub-features

- \`add\` — Add a product.

## How to get to it (user POV)

Open the shop.

## Driving it with Mole

${paragraph}

## Gotchas

None.
`;
const GOOD = "**(add | one-item):** **Given** an empty cart; **When** the user adds a product; **Then** the cart shows one item. **Proof:** cart count is 1 (State).";

test("a map names its scenarios, and each proof clause names the evidence it needs", () => {
  const map = parseMap(MAP(GOOD));
  assert.deepEqual(map.errors, []);
  assert.deepEqual(map.scenarios.map(entry => [entry.sub, entry.id, entry.proof[0].evidence]), [["add", "one-item", ["state"]]]);
});

test("a map is rejected for a pipe, a separate Evidence clause, an orphan declaration or a check with no evidence", () => {
  for (const [bad, expected] of [
    ["**(add | one-item):** **Given** a | b; **When** c; **Then** d. **Proof:** e (State).", /pipe/],
    ["**(add | one-item):** **Given** a; **When** c; **Then** d. **Proof:** e (State). **Evidence:** State.", /Evidence/],
    ["**Evidence:** State.", /[Oo]rphan/],
    ["**(add | one-item):** **Given** a; **When** c; **Then** d. **Proof:** e.", /no evidence/],
  ] as const) assert.match(parseMap(MAP(bad)).errors.join("\n"), expected);
});

// A fake app: the cart, the visitor's page (never touched), and evidence adapters that read the cart.
type Cart = { items: string[]; broken: boolean };
const fakePage = {} as Page;
const adapterFor = (cart: Cart, source = "state", assertive = true): EvidenceAdapter => ({
  source, assertive, ext: "json", unavailable: () => null,
  capture: async () => ({ result: [...cart.items], artifact: { items: [...cart.items] } }),
});
const memoryStore = () => {
  const saved = new Map<string, string | Uint8Array>();
  const store: ArtifactStore = { async save({ scenario, check, source, ext, data }) { const path = `${scenario}/${check}.${source}.${ext}`; saved.set(path, data); return path; } };
  return { saved, store };
};
const hostFor = (cart: Cart, features: ReturnType<typeof defineFeature>[], options: Partial<RunHost> & { adapters?: EvidenceAdapter[] } = {}) => {
  const { saved, store } = memoryStore();
  const adapters = options.adapters ?? [adapterFor(cart)];
  const host: RunHost = {
    app: "shop", appUrl: "http://shop.test", apiUrl: null, surfaces: ["web"], store, adapters, revision: async () => "rev1",
    visitor: async () => ({ page: fakePage, events: { step: -1, entries: [] }, close: async () => {} }), ...options,
  };
  return { host, saved, registry: buildRegistry(features, adapters) };
};

const addToCart = defineFlow("add-to-cart", async env => {
  const cart = env.vars.cart as Cart;
  if (!cart.broken) cart.items.push("mug");
  return {};
});
const cartHasOne = defineProof("cart-has-one", ["state"], async ctx => {
  const items = await ctx.observe<string[]>("state");
  return { pass: items.length === 1, expected: 1, actual: items.length, hint: "Adding a product must show it in the cart." };
});
const cartFeature = (cart: Cart) => defineFeature("cart", feature => {
  feature.touches("src/");
  feature.subFeature("add", sub => sub.scenario("one-item", scenario => scenario
    .flow(defineFlow("seed", async () => ({ cart })))
    .flow(addToCart).proof(cartHasOne)));
});

test("a cart that is broken fails with evidence, a fixed one passes, and a source that moves is stale", async () => {
  const cart: Cart = { items: [], broken: true };
  const feature = cartFeature(cart);
  const { host, saved, registry } = hostFor(cart, [feature]);
  const failing = await runScenarios(selectScenarios(registry), host);
  assert.equal(failing.verdict, "FAIL");
  assert.equal(exitCode(failing), 1);
  assert.equal(failing.scenarios[0].checks[0].evidence[0].artifact, "cart.add.one-item/cart-has-one.state.json");
  assert.ok(saved.has("cart.add.one-item/cart-has-one.state.json"));
  assert.match(failing.next.join("\n"), /Adding a product must show it in the cart/);

  cart.items.length = 0;
  cart.broken = false;
  const passing = await runScenarios(selectScenarios(registry), host);
  assert.equal(passing.verdict, "PASS");
  assert.equal(exitCode(passing), 0);

  cart.items.length = 0;
  let calls = 0;
  const moving = await runScenarios(selectScenarios(registry), { ...host, revision: async () => `rev${calls++ < 2 ? 1 : 2}` });
  assert.equal(moving.scenarios[0].verdict, "STALE");
  assert.equal(moving.verdict, "ERROR");
  assert.equal(exitCode(moving), 2);
});

test("a check that returns pass without capturing its evidence can only ERROR", async () => {
  const cart: Cart = { items: ["mug"], broken: false };
  const lazy = defineProof("lazy", ["state"], async () => ({ pass: true, expected: 1, actual: 1 }));
  const feature = defineFeature("cart", f => { f.touches("src/"); f.subFeature("add", sub => sub.scenario("one-item", s => s.proof(lazy))); });
  const { host, registry } = hostFor(cart, [feature]);
  const result = await runScenario(selectScenarios(registry)[0], host);
  assert.equal(result.verdict, "ERROR");
  assert.match(result.error ?? "", /without evidence from state/);
});

test("a check cannot capture evidence it did not declare", async () => {
  const cart: Cart = { items: ["mug"], broken: false };
  const sneaky = defineProof("sneaky", ["state"], async ctx => {
    await ctx.observe("state");
    await ctx.observe("other");
    return { pass: true, expected: 1, actual: 1 };
  });
  const feature = defineFeature("cart", f => { f.touches("src/"); f.subFeature("add", sub => sub.scenario("one-item", s => s.proof(sneaky))); });
  const { host, registry } = hostFor(cart, [feature], { adapters: [adapterFor(cart), adapterFor(cart, "other")] });
  const result = await runScenario(selectScenarios(registry)[0], host);
  assert.equal(result.verdict, "ERROR");
  assert.match(result.error ?? "", /did not declare/);
});

test("an evidence source that fails to capture is an ERROR with a diagnostic, never a PASS", async () => {
  const cart: Cart = { items: ["mug"], broken: false };
  const failing: EvidenceAdapter = { ...adapterFor(cart), capture: async () => { throw new Error("database is down"); } };
  const feature = cartFeature(cart);
  const { host, saved, registry } = hostFor(cart, [feature], { adapters: [failing] });
  const result = await runScenario(selectScenarios(registry)[0], host);
  assert.equal(result.verdict, "ERROR");
  assert.match(result.error ?? "", /database is down/);
  assert.ok([...saved.keys()].some(path => path.endsWith(".diagnostic.txt")));
});

test("the first step that is not PASS stops the scenario and the rest are NOT_REACHED", async () => {
  const cart: Cart = { items: [], broken: true };
  const failing = defineFlow("break", async () => { throw new Failure("the shop is closed"); });
  const feature = defineFeature("cart", f => { f.touches("src/"); f.subFeature("add", sub => sub.scenario("one-item", s => s.flow(failing).proof(cartHasOne))); });
  const { host, registry } = hostFor(cart, [feature]);
  const result = await runScenario(selectScenarios(registry)[0], host);
  assert.equal(result.verdict, "FAIL");
  assert.deepEqual(result.steps.map(step => step.verdict), ["FAIL", "NOT_REACHED"]);
  assert.equal(result.checks[0].verdict, "NOT_REACHED");
});

test("the registry refuses a scenario with no proof, undeclared or unknown evidence, or only a screenshot", () => {
  const adapters = [adapterFor({ items: [], broken: false }), adapterFor({ items: [], broken: false }, "shot", false)];
  const bad = (evidence: string[]) => defineFeature("cart", f => {
    f.touches("src/");
    f.subFeature("add", sub => sub.scenario("one-item", s => s.proof(defineProof("p", evidence, async () => ({ pass: true, expected: 1, actual: 1 })))));
  });
  assert.throws(() => buildRegistry([bad(["nope"])], adapters), /nope/);
  assert.throws(() => buildRegistry([bad(["shot"])], adapters), /assertive|screenshot/i);
  assert.throws(() => buildRegistry([defineFeature("cart", f => { f.touches("src/"); f.subFeature("add", sub => sub.scenario("one-item", s => s.flow(addToCart))); })], adapters), /proof/);
  assert.doesNotThrow(() => buildRegistry([bad(["state", "shot"])], adapters));
});

test("a verdict is the worst scenario: FAIL over ERROR over PASS, and nothing is an ERROR", () => {
  const scenario = (verdict: "PASS" | "FAIL" | "ERROR" | "STALE") => ({ verdict }) as Parameters<typeof aggregate>[0][number];
  assert.equal(aggregate([scenario("PASS"), scenario("PASS")]), "PASS");
  assert.equal(aggregate([scenario("PASS"), scenario("STALE")]), "ERROR");
  assert.equal(aggregate([scenario("ERROR"), scenario("FAIL")]), "FAIL");
  assert.equal(aggregate([]), "ERROR");
});
