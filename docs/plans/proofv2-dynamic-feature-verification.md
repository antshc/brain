# Proof v2 — Dynamic feature verification with Mole

Status: planned. Target repository: `antshc/brain`. This is a new `plugins/proofv2` plugin; `plugins/proof` remains unchanged.

## Goal

Use a Markdown feature map with sub-features and compact plain-language BDD scenarios. An agent composes persisted TypeScript Page Objects, components, flows, and proof checks. A refactored TypeScript Mole imports these dynamically built features, executes real user journeys, collects evidence at checkpoints, and writes revision-bound receipts.

## Decisions

1. **Copy TypeScript Mole, not Snack.** Start from `plugins/proof/skills/init-proof/templates/typescript/mole/`. Make Mole v2 the single high-level navigation, scenario execution, evidence collection, and receipt runtime. Adopt the useful Snack responsibilities from the handoff without adding a second CLI.
2. **Preserve feature/sub-feature maps.** One Markdown file per feature, with `Sub-features`, `Scenarios`, and `Gotchas`. Scenario `Flow`, `Proof`, and `Evidence` are plain text; no Given/When/Then, selectors, implementation method names, or YAML manifest.
3. **Run checks from dynamically built features.** The agent authors persisted TypeScript feature-builder modules. Each sub-feature composes reusable flows and attaches proof checks at the correct step. Mole imports the feature registry and executes those checks; it does not infer acceptance rules from the app's current output.
4. **One implementation of each action.** Interactive `mole flow` and automated `mole run` call the same Page Objects and flows. Proof checks observe state; they do not duplicate navigation.
5. **Reusable components are code.** A discovery subagent extracts observed controls (dropdowns, modals, tables, forms, tabs, pagination, date pickers, etc.) into project-local TypeScript. Reuse before creating new abstractions.
6. **Pluggable evidence.** Browser, network, storage, and API collectors ship in the MVP. Database, logs, and test-result collectors use project-owned adapters. Prefer durable business-state readback over screenshots or transient events.
7. **Fresh, auditable runs.** Interactive exploration can reuse a named session; a proving run gets a fresh isolated visitor context, a pinned app revision, step-scoped observations, and append-only receipts. A changed revision makes prior PASS stale.
8. **Keep `proof` v1 intact.** Do not overwrite its templates or generated project files. `proofv2` installs side-by-side with distinct names and paths.

## Runtime responsibilities

| Existing Mole TypeScript | Mole v2 change |
| --- | --- |
| `up`, `down`, `doctor` | Keep app startup, readiness, CDP browser lifecycle, and revision validation. |
| `snapshot`, `console`, `network`, `storage`, `screenshot`, `api get` | Keep exploration commands; expose evidence collector adapters and per-step capture windows. |
| Static `FEATURES` and `drive` hooks | Replace with a registry of builder-authored features, sub-features, and reusable flows. |
| `proveFeatures` invokes independent proofs | `run` executes the selected sub-feature's ordered flows and checkpoint checks in one context. |
| `runProof` always creates its own page | Move browser-context ownership to the scenario runner; checks observe the active scenario context. |
| Latest and historical receipts | Keep; add scenario/sub-feature ID, step, flow trace, expected/actual, observation provenance, and artifact references. |

Mole uses Playwright's TypeScript API directly for imported scenarios. Playwright CLI remains an optional exploration/discovery instrument. This avoids the `run-code` restriction on imports in reusable multi-file flows.

## Generated project structure

```text
.github/skills/verify-<app>/
  SKILL.md
  features/
    README.md
    shopping-cart.md
  scripts/
    agent.md               # explicitly loaded scenario-authoring instructions
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
mole/                      # v2 runtime copied/refactored from TypeScript Mole
```

The plugin sources live under `plugins/proofv2/` with `plugin.json`, `skills/init-proofv2`, `skills/verify`, `skills/maintain-proofv2`, templates, and `agents/component-extractor.agent.md`. Register the new plugin in `.github/plugin/marketplace.json`.

## Feature-map format

```md
# Shopping Cart

## Sub-features
- Add product
- Update quantity
- Remove product
- Persist cart

## Scenarios

### Add product
Flow:
1. Open catalog and select an available product.
2. Add the product to cart.
3. Open cart.

Proof:
- Cart displays the selected product with quantity 1.
- Cart API contains the selected product with quantity 1.
- No unexpected browser errors.

Evidence:
- API response
- Screenshot
- Browser errors

### Persist cart
Flow:
1. Add an available product to cart.
2. Reload the page.

Proof:
- Product and quantity persist after reload.

Evidence:
- API response
- Screenshot

## Gotchas
- A success notification is not proof of persistence.
- Use an isolated customer session.
```

The Markdown contract is authoritative. An agent maps its sub-features to stable internal IDs in TypeScript; the map does not need technical identifiers. Validation MUST flag a missing, extra, or stale sub-feature implementation. Preserve the Markdown text and its revision/hash in each receipt.

## Dynamic feature builder

Illustrative API (to be implemented; not existing):

```ts
export default defineFeature("shopping-cart", feature => {
  feature.subFeature("add-product", scenario => scenario
    .flow(openCatalog)
    .flow(selectAvailableProduct)
    .flow(addProductToCart)
    .proof(cartApiContainsSelectedProduct)
    .flow(openCart)
    .proof(cartDisplaysSelectedProduct)
    .proof(noUnexpectedBrowserErrors));
});
```

- `Feature` groups sub-features; `SubFeature` supplies ordered `Flow` and `Proof` steps.
- `FlowContext` holds the active Playwright page, named browser session, typed scenario variables (e.g. selected product ID), and safe runtime helpers.
- `Flow` performs actual user interactions and returns serializable context additions; it MUST NOT decide business acceptance.
- `Proof` receives the active context plus evidence adapter access, records focused expected/actual values, and MUST NOT navigate or mutate the app.
- `EvidenceAdapter` declares availability, scope, read/capture methods, and artifact metadata. Missing required adapters produce ERROR, never PASS.
- The builder produces a registry keyed by stable internal feature/sub-feature IDs. `mole run <feature>.<sub-feature>` resolves one entry; `mole run <feature>` runs all of its sub-features in isolated runs.
- A check is authored before implementing the feature. The agent may modify a locator/flow after UI changes, but MUST NOT loosen acceptance criteria to turn red into green.

## Evidence checkpoints and receipts

1. Select the feature and confirm map/implementation synchronization.
2. Run `doctor`; confirm app readiness, prerequisites, enabled collectors, and matching built revision.
3. Start an isolated visitor and initialize collectors **before** actions whose network or log events matter.
4. Execute each flow in order. At a `.proof(...)` step, collect observations from the same run and evaluate the registered checks.
5. Save step results, flow traces, screenshots/API readbacks and failures as immutable run artifacts; persist one aggregate receipt plus per-check details.
6. Detect a source or served-build revision change during the run: ERROR/STALE; never reuse the earlier PASS.
7. Close only run-owned resources; preserve all receipts, including failed attempts.

Verdicts: `PASS` (all required checks and artifacts), `FAIL` (observed requirement violated), `ERROR`/`CAN'T TELL` (environment/collector cannot verify), `NOT_REACHED` (later checkpoint skipped after an earlier stop). An absent required UI control can produce FAIL when the app and scenario preconditions are valid; missing infrastructure produces ERROR. Screenshots may need separate human/agent semantic review and are not automatically proof of behavior.

Prefer narrow API/resource matching (e.g. selected product ID and quantity) over entire JSON equality. Use database readback only when a suitable public API cannot establish the result. Explicitly assert browser errors if they affect completion; merely collecting them does not fail a scenario.

## Component discovery subagent

`agents/component-extractor.agent.md` is called during initialization and whenever a flow needs a missing or stale UI capability. It:

1. Reads the current component/Page Object/flow inventory.
2. Inspects source and live UI with Playwright, including accessibility roles, behavior, and repeated patterns.
3. Reuses or creates project-local components for controls such as dropdowns, modals, tables, forms, tabs, pagination, and date pickers.
4. Persists scoped TypeScript files, focused component tests, and a concise inventory/usage report.
5. Reports unverified components when the GUI does not yet exist; never invents observed selectors or silently weakens proofs.

Prefer semantic locators and stable test IDs; never persist ephemeral snapshot element references such as `e12`. Parent agent validates the returned files and composes flows. Keep subagent file-write ownership distinct from the scenario agent's active files.

## Verify skill `scripts/agent.md`

The generated Verify skill MUST explicitly read `scripts/agent.md` (a reference file, not an automatically registered agent). Its rules:

1. Read the feature map and select relevant sub-features.
2. Search existing components, Page Objects, flows, and checks before authoring anything.
3. Call the discovery subagent for missing reusable controls.
4. Persist new flows and builder definitions; keep Markdown steps natural-language and concise.
5. Execute `mole doctor`, then the selected sub-feature, inspect every failed/missing check and its artifacts, and re-run on a fresh revision.
6. Do not declare completion with stale, partial, or missing required evidence. After two failed repair attempts at the same check, return the receipt and ask for human input.

## Proposed CLI

```text
mole up --start              Start app and interactive browser
mole doctor                  App/build/collector health
mole features                List mapped features and sub-features
mole features --changed      Select affected features from source changes
mole flow catalog.open       Execute a reusable flow for exploration
mole run shopping-cart.add-product
mole run shopping-cart       Run all registered sub-features
mole receipts shopping-cart.add-product
mole down                    Stop only resources started by Mole
```

`flow` and `run` MUST use the same persisted TypeScript implementations. Keep `mole snapshot`, `console`, `network`, `storage`, and `api get` for diagnosis. All CLI commands emit structured JSON and actionable errors.

## Work packages

1. Create `plugins/proofv2` skeleton, marketplace entry and separate `init-proofv2` scaffold. Copy v1 TypeScript Mole source without touching v1.
2. Preserve Mole lifecycle, doctor, revision, CDP/event logging and receipt history; add regression tests before refactoring.
3. Introduce typed `Feature`, `SubFeature`, `ScenarioStep`, `FlowContext`, `Flow`, `ProofCheck`, `EvidenceAdapter`, and `Receipt` contracts.
4. Replace static feature drive/proof wiring with imported feature builders and a validated registry, including sub-feature coverage reporting.
5. Implement shared interactive-flow/scenario execution, isolated proving contexts, checkpoint timing, collectors, and receipts.
6. Implement reusable component/Page Object/flow directories and `component-extractor` subagent, with generated-code validation.
7. Generate compact feature maps, project-local Verify skill and `scripts/agent.md`; add map-to-registry consistency tests.
8. Test an e-commerce cart feature across failing-before-implementation, passing-after-implementation and stale-revision runs; exercise a dropdown, modal, and table reused across scenarios.

## Completion criteria

- The new plugin installs independently; Proof v1 still installs and passes its tests.
- Feature maps retain sub-features and plain-language Flow/Proof/Evidence descriptions.
- A dynamically built feature runs its own registered checks at the correct points, not a separate duplicate test path.
- The discovery subagent persists reusable TypeScript controls and the agent reuses them across flows.
- Interactive navigation and proof runs share flow implementations but proof runs use isolated visitor state.
- Browser/API evidence and actionable receipts survive cleanup and are bound to a single revision.
- Missing UI, missing prerequisites, incomplete evidence and stale receipts cannot yield PASS.

## Non-goals

- Python runtime in the v2 MVP.
- Runtime LLM interpretation of uncompiled Markdown as an executable test.
- Replacing existing unit/integration/E2E test suites.
- A second Snack executable or Playwright-control stack.
- Automatically treating a screenshot, toast or model confidence as success.

References: [Proof v1 Mole template](https://github.com/antshc/brain/tree/main/plugins/proof/skills/init-proof/templates/typescript/mole), [WorkOS Beyond Done lab](https://github.com/workos/beyond-done/tree/main/lab), [Playwright Page Objects](https://playwright.dev/docs/pom), [Playwright CLI script limits](https://playwright.dev/agent-cli/commands/console-eval).
