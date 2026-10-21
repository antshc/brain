// Keeps the registry, the feature maps and the app config in step. Run with: pnpm test:proof
// Add your own adapter tests to proof/features.test.ts; this file belongs to the mole and is replaced on upgrade.
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";
import { APP } from "../proof/app";
import { FEATURES } from "../proof/features";
import { CONTRACTS } from "../proof/contracts";
import { ALL_SURFACES, featureNames, featuresFor, selectFeatures, selectSurfaces, surfacesFor } from "../proof/kit";
import { COMMANDS } from "./commands";
import { ROOT } from "./runtime";

const SURFACES = APP.surfaces;

const MAPS = join(ROOT, APP.featureMaps ?? ".github/skills/verify-mole/features");

// The frontmatter of a map: `key: value` lines, and `key:` followed by `  - item` lines.
function frontmatter(file: string) {
  const match = readFileSync(join(MAPS, file), "utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
  assert.ok(match, `${file} has no frontmatter`);
  const data: Record<string, string | string[]> = {};
  let list: string[] | null = null;
  for (const line of match[1].split(/\r?\n/)) {
    const item = line.match(/^\s+-\s+(.*)$/);
    if (item && list) { list.push(item[1].trim()); continue; }
    const pair = line.match(/^(\w+):\s*(.*)$/);
    if (!pair) continue;
    if (pair[2]) { data[pair[1]] = pair[2].trim(); list = null; } else { list = data[pair[1]] = []; }
  }
  return data;
}

const maps = readdirSync(MAPS).filter(file => file.endsWith(".md") && file !== "README.md");
const index = readFileSync(join(MAPS, "README.md"), "utf8");
const BANNED = [/localStorage/, /querySelector/, /page\.locator/, /getByRole/, ...(APP.mapBanned ?? [])];

test("app config names a supported set of surfaces", () => {
  assert.ok(SURFACES.length > 0, "APP.surfaces is empty");
  for (const surface of SURFACES) assert.ok(ALL_SURFACES.includes(surface), `APP.surfaces has the unknown surface "${surface}"`);
  assert.ok(APP.sourcePaths.length > 0, "APP.sourcePaths is empty: the revision would cover the whole repo");
});

test("every feature has a map, and every map has a feature", () => {
  assert.deepEqual(maps.map(file => file.replace(/\.md$/, "")).sort(), Object.keys(FEATURES).sort());
});

test("a feature name is a plain word that no built-in command already uses", () => {
  for (const name of featureNames(FEATURES)) {
    assert.match(name, /^[a-z][a-z0-9-]*$/, `"${name}" must be lowercase words joined by hyphens`);
    assert.ok(!(name in COMMANDS), `"${name}" is a built-in mole command`);
  }
});

for (const [name, feature] of Object.entries(FEATURES)) {
  test(`${name}: the map names its feature, files, surfaces and proof command`, () => {
    const data = frontmatter(`${name}.md`);
    assert.equal(data.feature, name);
    assert.equal(data.prove, `pnpm mole prove --feature ${name}`);
    assert.deepEqual(data.touches, feature.touches);
    assert.deepEqual(data.surfaces, feature.surfaces);
  });
  test(`${name}: the feature only uses surfaces this repo supports`, () => {
    assert.ok(feature.surfaces.length > 0, `${name} has no surfaces`);
    for (const surface of feature.surfaces) assert.ok(SURFACES.includes(surface), `${name} uses ${surface}, which APP.surfaces does not list`);
    assert.ok(feature.touches.length > 0, `${name} touches nothing, so \`features --changed\` can never select it`);
  });
  test(`${name}: the map states a contract, not selectors, routes or wire details`, () => {
    const text = readFileSync(join(MAPS, `${name}.md`), "utf8");
    for (const banned of BANNED) assert.ok(!banned.test(text), `${name}.md mentions ${banned}: that belongs in the surface adapter`);
    assert.ok(/^## Contract$/m.test(text), `${name}.md has no Contract section`);
    assert.equal((text.match(/^## Driving it$/gm) ?? []).length, 1, `${name}.md needs exactly one "Driving it" block`);
  });
  test(`${name}: the feature map index links its map and its proof command`, () => {
    assert.ok(index.includes(`(${name}.md)`), `features/README.md does not link ${name}.md`);
    assert.ok(index.includes(`pnpm mole prove --feature ${name}`), `features/README.md does not show the proof command for ${name}`);
  });
}

test("changed files select the features they touch", () => {
  for (const [name, feature] of Object.entries(FEATURES)) assert.ok(featuresFor(FEATURES, [`${feature.touches[0]}x.file`]).includes(name));
  assert.deepEqual(featuresFor(FEATURES, ["no/such/place.txt"]), []);
});

test("an unknown feature is refused and no names means all", () => {
  assert.throws(() => selectFeatures(FEATURES, ["no-such-feature"]), /Unknown feature "no-such-feature"/);
  assert.deepEqual(selectFeatures(FEATURES), featureNames(FEATURES));
});

test("--surface is validated against the surfaces a feature has", () => {
  assert.throws(() => surfacesFor(FEATURES, featureNames(FEATURES), SURFACES, ["ftp"]), /Unknown surface "ftp"/);
  assert.deepEqual(selectSurfaces([], ["web"]), ["web"]);
  assert.throws(() => selectSurfaces(["api"], ["web"]), /no "api" surface/);
});


test("evidence contracts name existing features and supported surfaces", () => {
  assert.equal(new Set(CONTRACTS.map(c => c.feature)).size, CONTRACTS.length);
  for (const contract of CONTRACTS) {
    assert.ok(Object.hasOwn(FEATURES, contract.feature), `Unknown evidence feature: ${contract.feature}`);
    for (const surface of contract.surfaces) assert.ok(FEATURES[contract.feature].surfaces.includes(surface));
  }
});
