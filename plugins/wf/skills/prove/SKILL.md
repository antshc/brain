---
name: prove
description: >-
  Confirm or refute one technical claim with reproducible evidence. Use for /prove, 'run an experiment', 'try it and see'. Not for adversarial change review → `interrogate`; broken or slow behavior → `diagnosing-bugs`.
---

# Prove

Test the uncertainty with the smallest executable artifact exercising the actual mechanism. A failed assumption is a valid result. Passing cases establish only their exercised conditions.

## Inputs

Callers supply facts and limits; Prove owns method selection. Fill omitted framing from the request; ask only when the claim or intent remains unclear.

- `@question` — one uncertain technical question.
- `[@criteria]` — falsifiable assumption, expected behavior and observable confirm/refute conditions.
- `[@option]` — `logic | runtime | integration-local | integration-cloud | ui`; infer from uncertainty when omitted.
- `[@repoFacts]` — original launch/harness root, explicit source/proof checkout, revision and scoped dirty inputs, stack, runtime, runnable target, suites/commands, cloud account/region, research/sketch paths and prior evidence. Reuse applicable facts; discover gaps only.
- `[@limits]` — safety/runtime constraints, exclusions, writable paths, authorized resources and credential limits.
- `[@outputPath]`, `[@outputBase]`, `[@outputShape]` — exact final report destination, absolute base for relative paths, and content framing. No save requested → inline. Persistence without an exact destination → return inline and report the missing destination. Forward these unchanged to Research fallback.
- Execution ownership — assigned checkout, artifact destinations, cleanup owner and retention needs. Reuse a supplied verified worktree. Preserve runnable state through all coordinator reruns and any caller-requested follow-up review.

## Actions

| Action | Caller | Return |
|---|---|---|
| **Prove**, default | User or workflow coordinator | Independently reproduced evidence, conclusion and cleanup/retention record. |
| **Execute** | Assigned general-purpose prover or adversary | Evidence and exact rerun command from the assigned environment; cleanup handed to its coordinator. |

Execute never re-enters Prove orchestration or starts another proof/review worker. Prove never invokes its adversarial reviewer; the caller sequences requested proof and follow-up review.

Prove follows Workflow. Execute follows only Execute, Result and Cleanup with its supplied Frame. Resolve relative report paths only against `@outputBase`; missing/ambiguous base blocks saving, not independent checks.

## Workflow

1. **Frame.** State question, assumption, intent, expected behavior, criteria and exclusions; *run `principles` skill to load indexed engineering principles by name*, selecting `In your own words` for intent. A supplied sketch is context, not required input. Done when one claim can be refuted by a named observation.
2. **Reuse or read.** Valid evidence for the same revision/environment settles it → reuse with provenance. Reading or deterministic reasoning suffices → *run `research` skill to investigate primary sources and return cited findings*, passing the original question, output destination/base and framing. Stop with evidence labeled observed, source-based or inferred; do not claim a new run. Done when the deciding fact is supported or the empirical unknown remains explicit.
3. **Isolate, Prove only.** *Run `subagents` skill to dispatch independent workers with isolated outputs* using Dispatch, one general-purpose `prover` role. Supply Frame, facts/limits, explicit artifact destinations, and the Execute action. Request an owned git worktree with only scoped dirty inputs unless a verified checkout is supplied. Preserve its ownership record outside the worktree. Required isolation unavailable → report blocker. Done when the worker has its bounded writable environment and cleanup owner.
4. **Execute.** The assigned worker follows Execute below; default Prove collects its report. Done when every attempt has evidence or a named blocker.
5. **Reproduce, Prove only.** Independently rerun the exact command in the worker environment against the recorded target/patch. A changed environment, zero tests, missing assertion or unreproducible observation cannot confirm the claim. Done when reproduced output supports the conclusion or it is marked inconclusive.
6. **Report and finalize.** Apply Result and Cleanup. Done when evidence is retained and every owned resource is removed or explicitly handed back for retention.

## Execute

1. **Discover gaps.** Reuse stack, dependencies, clients, test infrastructure and conventions. For missing source facts, *run `research` skill to investigate primary sources and return cited findings* using Explore request: literal files/projects/SDK/config → `@shape=literal`, `@depth=quick`; named `Type.Member` → `symbol`, `medium`; unknown ownership/call path → `relationship`, `medium`. Send each independent request verbatim to `hunter` with the explicit checkout. Hunter unavailable → record blocker and continue independent checks. Done when needed facts have citations or are unknown.
2. **Choose.** Load only triggered tactics from Methods in full. Integration questions **MUST** invoke Testing Integrations Select through the integration tactic; reuse applicable selection/discovery for the same claim, revision and environment. Else prefer an existing command/test, CLI/API call, script, simulation or minimal prototype. CLI-only requires no app or patch. Done when method, deciding boundary and reason are stated.
3. **Run.** Use a selected tactic's captured execution when already run; otherwise execute its prepared command once. Exercise the real code/mechanism; stub only irrelevant dependencies. Prefer one-command reproducibility; expose relevant inputs, state transitions and failures. Simulation conclusions are limited to modeled behavior. Done when actual output and deciding assertions are captured, or execution is explicitly blocked.
4. **Return.** Fill Result, preserving proof code, patches and runnable resources for the coordinator. Use `confirmed | refuted | inconclusive`; missing evidence is inconclusive. Done when the coordinator can rerun and knows ownership/retention needs.

## Methods

Resolve from this skill base; read selected tactics in full. Combine runtime and integration when the harness crosses an external boundary.

| Uncertainty | Tactic |
|---|---|
| Pure logic, state/transitions, transformations | [Logic](tactics/logic.md) |
| Framework/runtime, lifecycle, concurrency, hosting | [Runtime](tactics/runtime.md) |
| SDK/API, cloud, broker, database, service boundary | [Integration](tactics/integration.md) |
| UI appearance or interaction | [UI](tactics/ui.md) |
| User needs example requests | [Examples](README.md) |

## Result

- **Question** — claim, intent, expected behavior and exclusions.
- **Method** — selected method and rationale; integrations include selected seam, speed rationale, prerequisites, actual boundary and rejected insufficient alternatives.
- **Observation** — exact command, working directory, environment/version, target revision/dirty state, patch identity, actual and expected output; tests include executed names and total/passed/failed/skipped counts. Include coordinator rerun or pending verification owner.
- **Conclusion** — confirmed/refuted/inconclusive for stated conditions, evidence source (observed/source-based/inferred), limitations/blockers and next check.
- **Evidence** — report/log paths, sources and code patch when created; implication for implementation/design, without applying it.
- **Cleanup** — owned resources, removed/retained status, cleanup owner and leftovers.

## Cleanup

Preserve report, logs and optional proof patch outside disposable worktrees before removal. Execute defers cleanup to its coordinator. Default Prove removes only its owned worktree/scratch resources after independent rerun; caller-requested follow-up review or preservation defers removal with an explicit handoff. *Use `git` skill for verified worktree lifecycle* using Worktrees. Never remove caller-owned checkouts/resources. Report cleanup failures and leftovers.

## Guardrails

- Keep state local or in authorized sandboxes; never use destructive production targets or expand credentials/permissions. Redact secrets from commands/output/artifacts.
- Change code only within assigned writable paths; follow supplied sketch types/signatures where relevant. No production abstractions, unrelated tests or polish.
- Record patches; changes to production behavior cannot prove the original target safe. Keep candidate fixes separate from evidence.
- Do not commit, push, apply design corrections or promote proof code to production. The caller owns implementation decisions.
- Subjective UI preferences remain human judgments; observed behavior and variant comparisons are evidence, not universal proof.

## Completion criteria

- One framed claim has a supported, scoped conclusion or explicit inconclusive reason.
- An observed conclusion includes the actual deciding output; default Prove includes independent reproduction.
- Requested artifacts exist at the supplied destinations, or missing destinations/artifacts are reported.
- Every created patch/resource has an ownership and cleanup/retention outcome; runnable evidence survives all declared consumers.
