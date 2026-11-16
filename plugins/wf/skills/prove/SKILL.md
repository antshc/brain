---
name: prove
description: >-
  Confirm or refute one or more technical claims with reproducible evidence. Use for /prove, 'run an experiment', 'try it and see'. Not for adversarial change review → `challenge-this`; broken or slow behavior → `diagnosing-bugs`.
---

# Prove

Router. Read the request, frame each claim, isolate proof checkouts, select one route per claim, spawn one `prover` worker per claim in parallel, verify, and deliver one saved report per claim. Test each uncertainty with the smallest executable artifact exercising the actual mechanism. A failed assumption is a valid result; passing cases establish only their exercised conditions. The router reads only framing facts; probing, code reading and execution happen in `prover` workers, keeping the caller's context clean. Only this skill spawns `prover`; workers never spawn subagents. Callers load this skill in their own session, never inside a wrapper subagent; a caller with many claims (`challenge-this`, `review` blast radius) collects them first and passes them in one batch.

## Request

Discover from the request; ask only when it holds no claim.

- **Claims** — one or more. Per claim:
  - **ID** — the caller's claim ID; none → `P1`, `P2`, ….
  - **Question** (`@question`) — one uncertain technical claim; split compound claims.
  - **Criteria** (`@criteria`) — falsifiable assumption, expected behavior, observable confirm/refute conditions. Infer from the request when omitted.
  - **Route** — a named route (`Route: Logic | Runtime | Integration | UI`) wins; otherwise infer per Routing.
  - **Baseline** — optional ref; the prover runs the same proof against baseline and target to attribute a regression.
  - **Group** — optional; claims sharing a mutable resource (database, queue, port, cloud resource) run sequentially within the group.
- **Facts** (`@repoFacts`) — stack, runtime, runnable target, suites/commands and test discovery, cloud account/region, research/grounding or sketch paths, prior evidence. Shared or per claim; the worker discovers gaps. A supplied sketch is context, not required input.
- **Limits** (`@limits`) — safety/runtime constraints, exclusions, writable paths, permitted edits (tests, temporary instrumentation), authorized resources, credential limits.
- **Checkout** — a supplied verified checkout, an explicit run-in-place request, or none → owned worktrees.
- **Framing** (`@outputShape`) — caller's role lens and extra per-claim return fields (e.g. verdict vocabulary, ladder level, likelihood/impact); preserve verbatim and pass to every worker.
- **Destination** (`@outputPath`, base `@outputBase`) — report file for one claim or folder for several.
- **Retention** — keep worktrees and runnable state for a named follow-up; default remove after Delivery.

## Frame

Run once per request, before Routing.

1. **Intent.** *Load and follow the `principles` skill to load indexed engineering principles by name*; select `In your own words`. *Done when* each claim's intent is restated.
2. **Checkout.** Set `@repoRoot` to `git rev-parse --show-toplevel` from the launch folder; record branch, HEAD and scoped dirty inputs. *Done when* target revision and dirty state are recorded.
3. **Reuse.** Valid evidence for the same claim, revision and environment → reuse with provenance; that claim skips to Delivery. *Done when* reuse is decided per claim.
4. **Isolate.** Supplied verified checkout or run-in-place request → use it as `@proofRoot` for every claim and run writing claims sequentially. Otherwise *Load and follow the `git` skill to run worktree lifecycle and creation* using Worktrees: one owned worktree per claim from the target revision with only scoped dirty inputs, plus one per Baseline ref; keep ownership records outside the worktrees. Isolation unavailable → that claim is blocked. *Done when* every claim has `@proofRoot`, optional `@baselineRoot`, and a cleanup owner.

Frame shape, one per claim, passed verbatim in its Brief and kept in its report:

```text
ID: <claim id>
Question: <original claim>
Assumption: <falsifiable assumption>
Criteria: <confirm observation> | <refute observation>
Route: <route> — <reason>
Checkout: <@repoRoot> @ <branch>/<sha> [+dirty: <paths>] → proof: <@proofRoot> (<owned | supplied | in place>)
Baseline: <ref> → <@baselineRoot>
Facts: <supplied facts with sources>
Limits: <limits>
Destination: <absolute report path>
```

Omit empty lines.

## Routing

Select one route per claim; pass its playbook, and Integration's when a Runtime harness crosses a real external boundary, as absolute paths from this skill's base directory. The router does not read playbooks; workers read them in full.

| Route | Select when | Playbook | Result |
|---|---|---|---|
| Logic | Pure logic, state/transitions, reducers, transformations | [Logic](playbooks/logic.md) | Per-case actual vs expected state |
| Runtime | Framework/runtime, lifecycle, concurrency, hosting, serializer, process | [Runtime](playbooks/runtime.md) | Observed mechanism behavior |
| Integration | SDK/API, cloud, broker, database, service boundary | [Integration](playbooks/integration.md) | Selected seam with executed assertions or probe output |
| UI | Page/component appearance or interaction | [UI](playbooks/ui.md) | Observed variants and selection |

Requester needs example requests → read [Examples](README.md).

## Spawning provers

The worker prompt is [Prover](agents/prover.md), discovered through this skill, never a registered agent. `prover` is the spawn's display name, never an agent type.

1. Read `agents/prover.md` in full and fill one Brief per claim: Frame, `@proofRoot`, `@baselineRoot`, selected playbook absolute paths, evidence/patch destinations outside the worktrees, requested framing. *Done when* no placeholder remains.
2. *Load and follow the `subagents` skill to select the model and effort for a named subagent role* with role `prover`, once per request. Never skip this step or drop the model to harness defaults; omit `model` and `reasoning_effort` only when `subagents` resolves to `auto`, `inherit-parent`, or an unknown role. *Done when* model and effort are resolved.
3. Spawn one skill-capable `general-purpose` worker per claim with its filled prompt as the whole task, the resolved `model` and `reasoning_effort`, `name` `prover-<id>`, and a description starting with `prover:`; writes limited to its `@proofRoot`, `@baselineRoot` and Brief destinations. Batch independent claims in one parallel response; run each Group sequentially. Parallel execution unavailable → run the same Briefs sequentially and report the limitation. Spawn failed → that claim is blocked with its consequence. *Done when* every claim returned its Return or a blocker.

Give a follow-up to a fresh `prover` with the original Brief, the prior Return and the bounded gap. A worker's newly discovered claims return to the caller; Prove does not expand scope.

## Verify

Per claim, rerun the worker's exact deciding command in its `@proofRoot` against the recorded target/patch; keep the conclusion only when actual output reproduces it. A changed environment, zero tests, missing assertion or unreproducible observation cannot confirm the claim; mark it inconclusive. *Done when* every conclusion is reproduced or marked inconclusive.

## Delivery

- Always save one Markdown report per claim. Return only the pointers:

  ```text
  Prove reports — read each in full before using its conclusion:
  - <id>: <claim> → <absolute path> (<route>; confirmed | refuted | inconclusive: <reason>)
  ```

  Present paths as clickable links.
- Default location: the agent harness session workspace, `<session>/files/prove/<id>-<claim-slug>.md`; no session workspace → `@repoRoot/tmp/prove/<id>-<claim-slug>.md`. Save outside owned worktrees.
- Request names a location → save there; resolve a relative path against `@outputBase`, else `@repoRoot`; a folder gets `<id>-<claim-slug>.md` per claim. Conflicting locations → ask before writing.
- Workers return evidence inline. Only the router writes reports.

Report sections: **Question** (Frame block, intent, exclusions), then the worker's **Method**, **Observation**, **Conclusion**, **Evidence** and requested framing fields, with the Verify rerun added to Observation, then **Cleanup** (owned resources, removed/retained status, cleanup owner, leftovers).

## Cleanup

Save reports, logs and proof patches outside worktrees before removal. Retention requested → keep worktrees and runnable state and hand them back with ownership records. Otherwise remove only Prove-owned resources: workers' reported scratch files, probes, authorized cloud resources and owned worktrees via *Load and follow the `git` skill to run verified worktree lifecycle* using Worktrees. Never remove supplied checkouts or caller resources. Report cleanup failures and leftovers.

## Guardrails

- Keep state local or in authorized sandboxes; never use destructive production targets or expand credentials/permissions. Redact secrets from commands, output and artifacts.
- Do not commit, push, apply design corrections or promote proof code to production. The caller owns implementation decisions and risk judgment.
- Subjective UI preferences remain human judgments; observed behavior and variant comparisons are evidence, not universal proof.

## Completion criteria

- Every claim has a saved report with a supported, scoped conclusion or explicit inconclusive/blocked reason, and a returned pointer.
- Every observed conclusion includes the actual deciding output and the router's rerun.
- Every created patch/resource, including owned worktrees, has a cleanup or retention outcome; runnable evidence survives declared consumers.
- Every evidence claim came from a `prover` worker; no worker spawned another.
