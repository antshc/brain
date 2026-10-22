# Proof v2 — Dynamic feature verification with Mole

Status: planned. Target repository: `antshc/brain`. This is a new `plugins/proofv2` plugin; `plugins/proof` remains unchanged.

## Goal

Use a Markdown feature map with sub-features and compact plain-language BDD scenarios. An agent composes persisted TypeScript Page Objects, components, flows, and proof checks. A refactored TypeScript Mole imports these dynamically built features, executes real user journeys, collects evidence at checkpoints, and writes revision-bound receipts.

## Decisions

1. **Copy TypeScript Mole, not Snack.** Start from `plugins/proof/skills/init-proof/templates/typescript/mole/`. Make Mole v2 the single high-level navigation, scenario execution, evidence collection, and receipt runtime. Adopt the useful Snack responsibilities from the handoff without adding a second CLI.
2. **Preserve the reference feature-map layout.** One Markdown file per feature with `Sub-features`, `How to get to it (user POV)`, `Driving it with Mole`, and `Gotchas`. Under `Driving it with Mole`, write one unbulleted paragraph per scenario, labeled `(sub-feature-id | scenario-id):`. Use compact **Given**, **When**, **Then** clauses separated by semicolons, followed inline by **Proof** and **Evidence**; no separate Flow/Proof/Evidence lists, pipes between clauses, selectors, method names, or YAML manifest.
3. **Run checks from dynamically built scenarios.** The agent authors persisted TypeScript feature-builder modules. Each sub-feature owns one or more named scenarios, each composing reusable flows and attaching proof checks at the correct step. Mole imports the feature registry and executes those checks; it does not infer acceptance rules from the app's current output.
4. **One implementation of each action.** Interactive `mole flow` and automated `mole run` call the same Page Objects and flows. Proof checks observe state; they do not duplicate navigation.
5. **Reusable components are code.** A discovery subagent extracts observed controls (dropdowns, modals, tables, forms, tabs, pagination, date pickers, etc.) into project-local TypeScript. Reuse before creating new abstractions.
6. **Pluggable evidence.** Browser, network, storage, and API collectors ship in the MVP. Database, logs, and test-result collectors use project-owned adapters. Prefer durable business-state readback over screenshots or transient events.
7. **Fresh, auditable runs.** Interactive exploration can reuse a named session; a proving run gets a fresh isolated visitor context, a pinned app revision, step-scoped observations, and append-only receipts. A changed revision makes prior PASS stale.
8. **Playwright CLI supports authoring and troubleshooting.** The Verify skill tells the agent to explore reachable UI with Playwright CLI before implementing new or changed scenario flows. It also supports investigation of failing scenarios, broken selectors, and Mole diagnostics. Persist discoveries in Page Objects/components/flows; Mole remains the executable scenario/proof/evidence runtime.
9. **TypeScript for all Proof v2 code.** Mole CLI/runtime, dynamic builders, reusable components, Page Objects, flows, checks, collectors/adapters, scripts, and automated tests MUST be authored in TypeScript. Do not introduce Python or handwritten JavaScript implementations for Proof v2. Markdown instructions/feature maps and JSON tooling configuration remain declarative files; generated JavaScript build output is not source.
10. **Keep `proof` v1 intact.** Do not overwrite its templates or generated project files. `proofv2` installs side-by-side with distinct names and paths.

## TypeScript implementation boundary

- **Runtime:** Copy and refactor the existing Node.js TypeScript Mole implementation. Keep one CLI and shared runtime contracts in `.ts` files; reuse its current TypeScript execution/build tooling where suitable.
- **Generated project code:** `verify/features`, `components`, `pages`, `flows`, `checks`, `adapters`, and any executable `scripts` MUST contain TypeScript source (`.ts`), including project-specific database/log/test-result adapters.
- **Plugin tooling and tests:** Scaffolding/generation helpers, CLI tests, scenario tests, component tests, adapter tests, and contract validation MUST be TypeScript. Run TypeScript type checking and relevant tests as completion gates.
- **Non-code files:** `SKILL.md`, `agent.md`, feature maps, receipts, `package.json`, and `tsconfig.json` may use Markdown/JSON. Application repositories may use any language; only Proof v2's integration code is TypeScript. Generated JavaScript distribution files, if required by Node, are build artifacts and MUST NOT be manually maintained.
- **Playwright CLI:** CLI exploration can run its documented commands, but persisted reusable navigation and proof logic MUST be TypeScript imported by Mole.

## Runtime responsibilities

| Existing Mole TypeScript | Mole v2 change |
| --- | --- |
| `up`, `down`, `doctor` | Keep app startup, readiness, CDP browser lifecycle, and revision validation. |
| `snapshot`, `console`, `network`, `storage`, `screenshot`, `api get` | Keep exploration commands; expose evidence collector adapters and per-step capture windows. |
| Static `FEATURES` and `drive` hooks | Replace with a registry of builder-authored features, sub-features, named scenarios, and reusable flows. |
| `proveFeatures` invokes independent proofs | `run` executes the selected scenario's ordered flows and checkpoint checks in one context, isolating each scenario run. |
| `runProof` always creates its own page | Move browser-context ownership to the scenario runner; checks observe the active scenario context. |
| Latest and historical receipts | Keep; add scenario/sub-feature ID, step, flow trace, expected/actual, observation provenance, and artifact references. |

Mole uses Playwright's TypeScript API directly for imported scenarios. The agent MUST use Playwright CLI to inspect the reachable UI before authoring new/changed browser flows, when a live UI is available; it MAY use the CLI during scenario troubleshooting and Mole failure diagnosis. Playwright CLI is an agent-side inspection tool, not a runtime dependency or substitute for Mole's proof checks. This avoids the `run-code` restriction on imports in reusable multi-file flows.

## Generated project structure

```text
.github/skills/verify-<app>/
  SKILL.md
  features/
    README.md
    shopping-cart.md
  scripts/
    agent.md               # explicitly loaded scenario-authoring instructions
    setup.ts               # TypeScript project bootstrap, if needed
verify/
  features/
    index.ts               # generated/maintained registry
    shopping-cart.ts       # executable dynamic feature builder
  components/              # reusable UI controls
  pages/                   # app-specific Page Objects
  flows/                   # reusable business actions
  checks/                  # durable assertion functions
  adapters/                # project-specific evidence sources
  .runs/                   # gitignored observations and receipts
mole/                      # TypeScript CLI/runtime copied/refactored from TypeScript Mole
  *.ts                     # command, browser, collector, receipt, and runner source
package.json               # Node scripts and dependencies
tsconfig.json              # strict TypeScript type checking
```

The plugin sources live under `plugins/proofv2/` with `plugin.json`, `skills/init-proofv2`, `skills/verify`, `skills/maintain-proofv2`, templates, and `agents/component-extractor.agent.md`. Register the new plugin in `.github/plugin/marketplace.json`.

## Feature-map format

```md
# Shopping Cart

Customers can add products to their shopping cart and manage its contents.

## Sub-features

- `add-product` — Add an available product.
- `update-quantity` — Change product quantity.
- `remove-product` — Remove a product.
- `persist-cart` — Preserve cart after reload.

## How to get to it (user POV)

Open the product catalog, select a product, and navigate to the shopping cart.

## Driving it with Mole

**(add-product | success):** **Given** product is available; **When** customer adds it to cart; **Then** cart contains product. **Proof:** API contains product and UI displays product. **Evidence:** API response, screenshot.

**(add-product | out-of-stock):** **Given** product is unavailable; **When** customer attempts to add it; **Then** cart remains unchanged. **Proof:** Cart API contains no new item. **Evidence:** API response.

**(update-quantity | success):** **Given** cart contains product; **When** customer changes quantity to 2; **Then** quantity and total are updated. **Proof:** API returns expected quantity and total. **Evidence:** API response, screenshot.

**(remove-product | success):** **Given** cart contains product; **When** customer removes it; **Then** product disappears. **Proof:** API and UI no longer contain product. **Evidence:** API response, screenshot.

**(persist-cart | reload):** **Given** cart contains product; **When** customer reloads page; **Then** cart retains its contents. **Proof:** API and UI retain product and quantity. **Evidence:** API response, screenshot.

## Gotchas

- A success notification is not proof of persistence.
- Match relevant API fields instead of entire responses.
- Use an isolated customer session.
- Start network capture before actions whose requests matter.
```

The Markdown contract is authoritative. Each `(sub-feature-id | scenario-id):` is a stable, unique key within its feature: `shopping-cart.add-product.success`. The single pipe separates IDs **only in the label**; do not use pipes to separate **Given**, **When**, **Then**, **Proof**, or **Evidence**. Scenario entries MUST be unbulleted, with no `Scenario:` prefix. **Proof** describes the observable assertion; **Evidence** names the required artifacts. Flow details belong in reusable TypeScript code, while the BDD clauses state behavior.

The map validator MUST require one **Given**, **When**, **Then**, **Proof**, and **Evidence** in every scenario paragraph. The builder MUST reject duplicate IDs, scenarios referencing unknown sub-features, missing/extra/stale mapped scenarios, or proof/evidence requirements without corresponding executable checks/collectors. Preserve the Markdown text and revision/hash in each receipt.

## Dynamic feature builder

Illustrative API (to be implemented; not existing):

```ts
export default defineFeature("shopping-cart", feature => {
  feature.subFeature("add-product", sub => {
    sub.scenario("success", scenario => scenario
      .flow(openCatalog)
      .flow(selectAvailableProduct)
      .flow(addProductToCart)
      .proof(cartApiContainsSelectedProduct)
      .flow(openCart)
      .proof(cartDisplaysSelectedProduct)
      .proof(noUnexpectedBrowserErrors));

    sub.scenario("out-of-stock", scenario => scenario
      .flow(openUnavailableProduct)
      .flow(attemptAddToCart)
      .proof(cartApiRemainsUnchanged));
  });
});
```

- `Feature` groups sub-features; `SubFeature` groups named `Scenario` definitions; `Scenario` supplies ordered `Flow` and `Proof` steps.
- `FlowContext` holds the active Playwright page, named browser session, typed scenario variables (e.g. selected product ID), and safe runtime helpers.
- `Flow` performs actual user interactions and returns serializable context additions; it MUST NOT decide business acceptance.
- `Proof` receives the active context plus evidence adapter access, records focused expected/actual values, and MUST NOT navigate or mutate the app.
- `EvidenceAdapter` declares availability, scope, read/capture methods, and artifact metadata. Missing required adapters produce ERROR, never PASS.
- The builder produces a registry keyed by stable `feature.sub-feature.scenario` IDs from Markdown labels. `mole run <feature>.<sub-feature>.<scenario>` runs one; `mole run <feature>.<sub-feature>` runs all mapped scenarios of that sub-feature; `mole run <feature>` runs all scenarios, with a fresh isolated context for each.
- A check is authored before implementing the feature. The agent may modify a locator/flow after UI changes, but MUST NOT loosen acceptance criteria to turn red into green.

## Evidence checkpoints and receipts

1. Select feature/sub-feature/scenario IDs and confirm Markdown-to-registry synchronization.
2. Run `doctor`; confirm app readiness, prerequisites, enabled collectors, and matching built revision.
3. Start an isolated visitor and initialize collectors **before** actions whose network or log events matter.
4. Execute each selected scenario's flows in order. At a `.proof(...)` checkpoint, collect observations from the same run, evaluate checks matching its inline **Proof**, and store artifacts required by inline **Evidence**.
5. Save step results, flow traces, screenshots/API readbacks and failures as immutable run artifacts; persist one aggregate receipt plus per-check details.
6. Detect a source or served-build revision change during the run: ERROR/STALE; never reuse the earlier PASS.
7. Close only run-owned resources; preserve all receipts, including failed attempts.

Verdicts: `PASS` (all required checks and artifacts), `FAIL` (observed requirement violated), `ERROR`/`CAN'T TELL` (environment/collector cannot verify), `NOT_REACHED` (later checkpoint skipped after an earlier stop). An absent required UI control can produce FAIL when the app and scenario preconditions are valid; missing infrastructure produces ERROR. Screenshots may need separate human/agent semantic review and are not automatically proof of behavior.

Prefer narrow API/resource matching (e.g. selected product ID and quantity) over entire JSON equality. Use database readback only when a suitable public API cannot establish the result. Explicitly assert browser errors if they affect completion; merely collecting them does not fail a scenario.

## Component discovery subagent

`agents/component-extractor.agent.md` is called during initialization and whenever a flow needs a missing or stale UI capability. It:

1. Reads the current component/Page Object/flow inventory.
2. Uses Playwright CLI to inspect reachable live UI (accessibility snapshots, roles, navigation, and control behavior), alongside source inspection. If the UI does not exist yet, records the missing surface and leaves selectors unverified.
3. Reuses or creates project-local components for controls such as dropdowns, modals, tables, forms, tabs, pagination, and date pickers.
4. Persists scoped TypeScript files, focused component tests, and a concise inventory/usage report.
5. Reports unverified components when the GUI does not yet exist; never invents observed selectors or silently weakens proofs.

Prefer semantic locators and stable test IDs; never persist ephemeral snapshot element references such as `e12`. Parent agent validates the returned files and composes flows. Keep subagent file-write ownership distinct from the scenario agent's active files.

## Verify skill `scripts/agent.md`

The generated Verify skill MUST explicitly read `scripts/agent.md` (a reference file, not an automatically registered agent). Its rules:

1. Read the feature map and select relevant scenarios under their sub-features.
2. Search existing components, Page Objects, flows, and checks before authoring anything.
3. **Before authoring new or changed browser scenarios/flows, use Playwright CLI to explore the available app:** navigate as a user, inspect accessibility snapshots, verify stable locators and control behavior, and identify reusable parts. If the target GUI is not implemented yet, inspect source instead; define expected behavior, mark UI selectors unverified, and do not fabricate observations.
4. Call the discovery subagent for missing reusable controls; pass CLI observations and component inventory. Persist verified discoveries in TypeScript Page Objects/components/flows rather than ephemeral CLI snapshots.
5. Persist new flows and builder definitions; write unbulleted `(sub-feature-id | scenario-id):` Markdown lines with compact **Given**/**When**/**Then**/**Proof**/**Evidence** clauses. Keep flows in TypeScript, not Markdown.
6. Execute `mole doctor`, then selected scenario(s). **Use Playwright CLI when useful to troubleshoot failed steps, missing elements, navigation, and Mole errors**; compare its observations with Mole receipts, then repair flows/checks without weakening acceptance rules.
7. Rerun proving through Mole on a fresh isolated context/revision. CLI exploration MUST NOT produce PASS verdicts or replace required Mole evidence. Do not declare completion with stale, partial, or missing required evidence. After two failed repair attempts at the same check, return the receipt and ask for human input.

## Proposed CLI

```text
mole up --start              Start app and interactive browser
mole doctor                  App/build/collector health
mole features                List mapped features, sub-features, and scenarios
mole features --changed      Select affected features from source changes
mole flow catalog.open       Execute a reusable flow for exploration
mole run shopping-cart.add-product.success  Run one scenario
mole run shopping-cart.add-product          Run sub-feature's scenarios
mole run shopping-cart                      Run all mapped scenarios
mole receipts shopping-cart.add-product.success
mole down                    Stop only resources started by Mole
```

`flow` and `run` MUST use the same persisted TypeScript implementations. Keep `mole snapshot`, `console`, `network`, `storage`, and `api get` for diagnosis. All CLI commands emit structured JSON and actionable errors.

## Work packages

1. Create `plugins/proofv2` skeleton, marketplace entry and separate `init-proofv2` scaffold. Copy v1 TypeScript Mole source without touching v1; keep all new executable plugin/scaffold logic in TypeScript.
2. Preserve Mole lifecycle, doctor, revision, CDP/event logging and receipt history; add TypeScript regression tests before refactoring.
3. Introduce typed `Feature`, `SubFeature`, `Scenario`, `ScenarioStep`, `FlowContext`, `Flow`, `ProofCheck`, `EvidenceAdapter`, and `Receipt` contracts.
4. Replace static feature drive/proof wiring with imported feature builders and a validated registry, including scenario-level coverage and Markdown-to-builder matching.
5. Implement shared interactive-flow/scenario execution, isolated proving contexts, checkpoint timing, collectors, and receipts.
6. Implement reusable component/Page Object/flow directories and `component-extractor` subagent, with Playwright CLI exploration guidance and generated-code validation.
7. Generate compact feature maps with the four required sections and unbulleted `(sub-feature | scenario):` entries, project-local Verify skill and `scripts/agent.md` requiring Playwright CLI UI exploration where available and allowing scenario/Mole troubleshooting; add map-to-registry consistency tests.
8. Test an e-commerce cart feature with TypeScript tests across failing-before-implementation, passing-after-implementation and stale-revision runs; exercise a dropdown, modal, and table reused across scenarios.
9. Run TypeScript type checking and relevant tests for the runtime, generated flows, checks, adapters, and scaffold; verify no handwritten JavaScript/Python logic was introduced.

## Completion criteria

- The new plugin installs independently; Proof v1 still installs and passes its tests.
- All Proof v2 executable source and tests (Mole, builders, UI components, flows, checks, adapters, and scaffolding) are TypeScript and pass type checking.
- Feature maps retain four reference sections; unbulleted `(sub-feature | scenario):` lines contain **Given**, **When**, **Then**, **Proof**, and **Evidence** inline, with no pipe delimiters inside scenario clauses.
- Dynamically built scenarios run their registered checks at the correct checkpoints, including multiple scenarios per sub-feature, not through a duplicate test path.
- The Verify skill instructs Playwright CLI exploration before new/changed browser scenario code (when the GUI exists) and allows CLI-assisted troubleshooting; these observations never replace Mole proof evidence.
- The discovery subagent persists reusable TypeScript controls and the agent reuses them across flows.
- Interactive navigation and proof runs share flow implementations but proof runs use isolated visitor state.
- Browser/API evidence and actionable receipts survive cleanup and are bound to a single revision.
- Missing UI, missing prerequisites, incomplete evidence and stale receipts cannot yield PASS.

## Non-goals

- Python runtime, Python scaffolding, or handwritten JavaScript runtime modules in the v2 MVP.
- Runtime LLM interpretation of uncompiled Markdown as an executable test; Markdown remains the acceptance contract, not the runner.
- Replacing existing unit/integration/E2E test suites.
- A second Snack executable or Playwright-control stack.
- Automatically treating a screenshot, toast or model confidence as success.

References: [Proof v1 Mole template](https://github.com/antshc/brain/tree/main/plugins/proof/skills/init-proof/templates/typescript/mole), [WorkOS Beyond Done lab](https://github.com/workos/beyond-done/tree/main/lab), [Playwright Page Objects](https://playwright.dev/docs/pom), [Playwright CLI script limits](https://playwright.dev/agent-cli/commands/console-eval).
