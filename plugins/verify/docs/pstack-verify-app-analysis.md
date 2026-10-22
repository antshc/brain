# How pstack `verify-<app>` works

Source analysis, 21 October 2026. This describes the original implementation and distinguishes its requirements from example adaptations.

## Summary

`verify-<app>` is a **project-local Agent Skill**, not a standalone test runner. An agent reads instructions and a feature map, launches the real application, executes user-facing journeys with an existing or generated control harness, captures observable evidence, and cleans up. The harness can use browser/CDP, Playwright/Cypress, a CLI/PTY, or HTTP.

There are four separate concerns:

| Concern | Responsibility |
|---|---|
| Feature map | Describe features, sub-features, entry points, and observable results |
| `verify-<app>/SKILL.md` | Explain launch, doctor, drive, evidence, cleanup, and helpers |
| App control harness | Execute interactions (commands, browser controls, HTTP) |
| Agent | Select the relevant map entries, follow recipes, inspect results, report gaps |

## Creation and layout

Running `/create-verification-skill` inspects the repository to discover its application surface, startup procedure, existing harness, evidence sources, and support for isolated concurrent instances. It prefers existing test and control tools. It then creates a project-local skill, for example:

```text
.agents/skills/verify-shop/
├── SKILL.md
├── features/
│   ├── README.md
│   ├── catalog.md
│   ├── shopping-cart.md
│   └── checkout.md
└── scripts/                 # optional documented helpers
```

The base path depends on the host agent: `.cursor/skills/`, `.claude/skills/`, `.pi/skills/`, or `.agents/skills/`.

The generated `SKILL.md` must document:

1. **Launch:** Exact startup and usable-readiness procedure, migrations/seed data, teardown.
2. **Doctor:** Read-only validation of instance identity, build, process, auth, and readiness.
3. **Drive:** Exact repo-specific controls and stable selectors/commands.
4. **Evidence:** What to capture, where to preserve it, and the behavioral proof standard.
5. **Cleanup:** Only stop instances and remove scratch state owned by the run; preserve evidence.
6. **Helpers:** Exact invocations for scripts, when present.

The generator seeds approximately 3–5 prominent features, discovered from routes, commands, menus, or docs. It **proves the generated skill once**: launch, doctor, drive **one** mapped feature, capture evidence, cleanup, confirm evidence survived. That is a harness acceptance check, **not** complete feature coverage.

Source: [create-verification-skill/SKILL.md](https://github.com/backnotprop/pstack/blob/main/skills/create-verification-skill/SKILL.md).

## Feature map and sub-features

The feature map is Markdown, not a machine-executed test registry. Its `README.md` indexes one file per user-facing feature. Each feature file has exactly four H2 sections:

- `Sub-features`: Stable short identifiers and one-line behavior descriptions.
- `How to get to it (user POV)`: User-facing entry points.
- `Driving it with <harness>`: Preconditions, precise actions/commands, and observable outcomes.
- `Gotchas`: Prerequisites, eligibility, state traps, and other reasons a run could mislead.

An illustrative e-commerce feature:

```markdown
# Shopping cart

Products can be added to, changed in, and removed from the cart.

## Sub-features
- add-product: Add a product from its detail page.
- change-quantity: Change an existing line quantity.
- remove-product: Remove a line from the cart.
- persistence: Reload and see the saved cart.

## How to get to it (user POV)
- Open a product page and select Add to cart.
- Open the cart from the navigation bar.

## Driving it with control-shop
Preconditions: seeded, in-stock product; isolated authenticated user.
- Open a product, click Add to cart; observe cart badge and line item.
- Read the cart through the public API; observe product ID and quantity.
- Reload the browser; observe the line still present.

## Gotchas
- Use a unique user/session to avoid cart contamination.
- Inventory and authentication must be ready before driving.
```

This is **an adaptation**, not a literal file in pstack. The author's real [Atlas feature map](https://github.com/poteto/verification-skill-example/blob/main/.cursor/skills/verify-atlas/references/features/README.md) has roughly 30 files. Its [new-session.md](https://github.com/poteto/verification-skill-example/blob/main/.cursor/skills/verify-atlas/references/features/new-session.md) has nine sub-features and uses exact `control-atlas.mjs` commands.

The upstream [Notes feature-map example](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/references/feature-map-example/README.md) asks the runner to read the index before driving, start from isolated baseline state, record feature IDs and entry points with artifacts, and report unreachable or skipped paths without falsely marking them verified.

## How test cases execute

The agent reads the feature recipe and executes the documented harness calls. This is **not necessarily a precompiled test method**. The recipe may call existing tests or issue browser, CLI, or HTTP actions; the agent observes outcomes and captures evidence.

Typical sequence:

1. Start application with isolated seeded state.
2. Run read-only doctor checks.
3. Execute the user path using stable selectors or commands.
4. Inspect action and resulting visible state; read back side effects through an independent surface when applicable.
5. Store screenshots, terminal transcripts, HTTP responses, DB observations, logs, or recordings.
6. Report pass/failure/unreachable scope, clean up owned resources, preserve artifacts.

The original proof standard requires using the real user path, not test-only setters. A screenshot alone does not establish persistence. Mocks may replace dependencies at an existing production boundary, but must not bypass the path under test.

## How sub-features are selected

There is **no specified deterministic code-diff-to-sub-feature algorithm** in the original skill. The agent uses the task description, affected feature file, user entry points and behavioral variants to choose relevant coverage. Selection therefore depends on its reasoning and on the accuracy of the map.

| Mode | Coverage requirement |
|---|---|
| Generate skill | Drive one mapped feature end-to-end to prove the harness works |
| Verify fix/new feature | Use the relevant feature file; exercise reachable affected entry points, modes, gated variants and relevant success/error/cancel/empty/persistence paths |
| Full regression | Traverse the full feature-map index, including cross-surface journeys |
| Maintain skill | Read every feature from source and exercise each mapped **feature** at least once live; not necessarily every sub-feature bullet |

The Atlas example expressly says that a fix's relevant feature file defines the coverage set, while a full sweep walks the whole map. The maintenance skill calls the **feature**, not each sentence or sub-feature bullet, its unit of coverage.

Consequences:

- Editing an `AddItem` handler does **not automatically** select `add-product` and `persistence` through a prescribed dependency graph.
- A live pass over a feature does **not guarantee** all sub-features were individually executed.
- An unreachable path must be reported with its attempted entry point and missing prerequisite, not silently counted as a pass.

Sources: [Atlas map](https://github.com/poteto/verification-skill-example/blob/main/.cursor/skills/verify-atlas/references/features/README.md), [maintain-verification-skill](https://github.com/backnotprop/pstack/blob/main/skills/maintain-verification-skill/SKILL.md).

## Maintenance

`/maintain-verification-skill` reconciles the map with source and the live app:

1. Check README index against feature files.
2. Analyze each feature from source.
3. Reconcile missing or stale behavior.
4. Drive every mapped feature in a live pass; doctor after unexpected failures and preserve evidence.
5. Classify problems as map drift, harness gap, or product regression.
6. Return **clean**, **changed** (one PR confined to verification-skill files), or **blocked**.

It never silently fixes product code or weakens a journey to make it pass.

## Comparison with this repository's Proof kit

The local Proof design already includes `init-verify`, `verify-mole`, a feature map, explicit executable feature checks, surface adapters, and durable receipts. The systems are complementary.

| Aspect | pstack | Proof kit |
|---|---|---|
| Verification selection | Agent interprets feature map | Feature metadata and registered checks can explicitly select cases |
| Test execution | Agent-driven harness recipes | Executable checks through adapters |
| Evidence | Screenshots/responses/logs and reported observations | Structured evidence and receipts |
| Repeatability | Depends on prompt, harness and recorded controls | Explicit checks can be repeatable with deterministic assertions |
| Coverage inventory | User-facing map with sub-features | Map plus executable feature registry |

**Potential adoption:** Keep the Proof kit's check contracts and receipts. Use pstack's user-POV feature-map discipline to improve discovery and impact analysis. Map stable sub-feature IDs to registered Proof checks when deterministic selection and per-sub-feature coverage are required. This mapping is a proposed extension, **not an existing pstack guarantee**.

## Original sources

- [pstack: Verify and ship guide](https://github.com/backnotprop/pstack/blob/main/docs/guide/06-verify-and-ship.md)
- [pstack: Create verification skill](https://github.com/backnotprop/pstack/blob/main/skills/create-verification-skill/SKILL.md)
- [pstack: Maintain verification skill](https://github.com/backnotprop/pstack/blob/main/skills/maintain-verification-skill/SKILL.md)
- [pstack: Notes feature-map template](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/references/feature-map-example/README.md)
- [poteto: Atlas verification-skill example](https://github.com/poteto/verification-skill-example)
- [poteto: Atlas feature map](https://github.com/poteto/verification-skill-example/blob/main/.cursor/skills/verify-atlas/references/features/README.md)
- [poteto: New-session feature](https://github.com/poteto/verification-skill-example/blob/main/.cursor/skills/verify-atlas/references/features/new-session.md)
- [Original X post](https://x.com/poteto/status/2094457600259842065) (not independently readable during research; GitHub files above were inspected)
