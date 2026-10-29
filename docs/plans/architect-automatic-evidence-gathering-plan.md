# Architect Automatic Evidence Gathering Plan

**Status:** Planned  
**Repository:** `antshc/brain`  
**Scope:** `plugins/wf/skills/architect/` only; reuse the existing `/research` and `/experiment` skills without modifying them.

## Goal

Make `/architect` proactively resolve technical questions through delegated research, runnable experiments, and adversarial verification. Keep the current Arena count (1–3; default 1), Judge behavior, sketch artifacts, review loop, `accept` → `/to-spec` handoff, and explicit `implement` gate.

## Constraints

1. **MUST** use existing `/research`, `/experiment`, and `interrogate/interrogate.md` procedures. **MUST NOT** restate their internal instructions, even if a duplicated shortcut looks simpler. *Rationale:* one source of truth per mechanism.
2. **MUST** trigger evidence gathering from deterministic conditions, not solely from an optional user reply. *Rationale:* identical questions should follow the same route.
3. **MUST** delegate documentation/source research through the `/research` skill. Architect passes the question and output expectations; Research discovers specialists and owns its subagent fan-out. *Rationale:* avoid a second research dispatcher.
4. **MUST** use `/experiment` for questions that require observation; that skill chooses the smallest executable method, including a CLI command, script, existing test, simulation, or throwaway application. **MUST NOT** require an app or code patch for CLI-only experiments. *Rationale:* measure the real uncertainty with minimal machinery.
5. **MUST** use `/experiment` from Interrogate when adversaries need a runnable probe. Reuse existing reproductions where valid, and independently rerun reported commands. *Rationale:* verification requires actual evidence, not conjecture.
6. **MUST NOT** apply Interrogate or Experiment proposals automatically to the sketch. The user still accepts design corrections, and only `implement` permits production code. *Rationale:* preserve existing human design authority.
7. **MUST** keep experiment code isolated and disposable; do not use destructive production targets or expand credentials/permissions. *Rationale:* evidence gathering is not production implementation.
8. **MUST** make targeted changes only; do not reformat or rewrite existing skill procedures unless the new contract requires it. *Rationale:* minimize regression risk.

## Updated flow

```text
Flow: Architect

1. Ground
   → Inspect repo docs, architecture, and existing code via current how/why flow.
   → Identify factual and empirical technical questions.
   → For each source-fact question: Run /research.
   → For each executable question: Run /experiment.

2. Sketch
   → Run existing Arena (1 agent by default).
   → Screen and synthesize the design.

3. Resolve questions and challenge assumptions
   → Check each open question against existing evidence.
   → Source fact unknown: Run /research.
   → Runtime behavior unknown: Run /experiment.
   → Material falsifiable design risk: Run Interrogate.
       → Reviewers use /experiment to select and execute probes.
   → Question needs user intent/tradeoff: Leave open for review.

4. Review
   → Present sketch, evidence, unresolved questions, and proposed corrections.
   → User accepts corrections or requests another round.
   → Recheck only evidence invalidated by a material change.

5. User decision
   → accept: Hand off to /to-spec.
   → implement: Implement accepted sketch.
   → otherwise: Continue existing review loop.
```

## Evidence routing

Choose the first applicable route, then reevaluate after evidence arrives.

| Condition | Route | Example |
|---|---|---|
| Reliable existing evidence already answers it | Record answer; no new agent | A tested invariant with unchanged context |
| Needs source facts from codebase, installed package, cloud, API, or web docs | `/research` | GitHub GraphQL capability or SDK-version contract |
| Needs actual behavior observed | `/experiment` | SQLite transaction behavior under concurrent connections |
| A CLI command can answer it | `/experiment` chooses CLI | Inspect a CLI/API operation directly |
| Needs a small program, integration setup, or simulation | `/experiment` chooses artifact | Race, retry, lifecycle, framework behavior |
| A material design assumption can be challenged by an executable counterexample | Interrogate with `/experiment` | Duplicate writes on retry, authorization bypass |
| Requires preference, product policy, acceptable tradeoff, or unavailable authority | Ask user or report blocker | Choose consistency-versus-latency policy |

Research can reveal an empirical uncertainty; reroute that question to Experiment. Prototype experiments already call Interrogate, so do not invoke a duplicate independent review for the same scope and revision.

### Research skill handoff

Invoke `plugins/wf/skills/research/SKILL.md` with:

```yaml
@question:
  question: <one sharp question>
  context: <decision, current sketch, repo constraints and relevant version>
  evidenceNeeded: <fact whose answer changes the architecture>

@outputShape:
  format: markdown
  count: one result per research topic/source part
  location: <repo-root>/tmp/architect-<slug>/research/
  required:
    - answer and architecture implications
    - primary-source citations
    - version/applicability constraints
    - unknowns or blockers
    - output artifact path
```

Pass the `@outputShape` constraints verbatim to Research, which in turn passes them to every delegated specialist. Honor a specialist's stronger artifact-location contract when applicable; keep the resulting report path in Architect's artifact index. Do not manually select or spawn a parallel set of research agents from Architect; Research owns classification, discovery, fan-out, and verification.

Architect reads the final research artifacts, checks cited conclusions and applicable versions, and adds their findings to the grounding/rationale before Arena or review.

### Experiment skill handoff

Invoke `plugins/wf/skills/experiment/SKILL.md` with:

```yaml
question: <one technical question>
assumption: <falsifiable claim>
successCriteria: <observable confirmation/refutation>
context: <repo, current sketch, earlier research evidence>
constraints: <runtime, environment, safety limits, out-of-scope behavior>
```

The Experiment skill, not Architect or Interrogate, selects the smallest mechanism:

- CLI/API: existing CLI, `curl`, or direct commands.
- SDK/integration: existing tests or a minimal script.
- Runtime/state/concurrency: minimal simulation, process set, or throwaway app.
- Database/broker/cloud: local or authorized sandbox boundary.
- UI: existing frontend/route where possible.

Expected result: question, method, exact command, observed output, conclusion (confirmed/refuted/inconclusive), evidence paths, architectural implication, and cleanup. A reproducible command and report are mandatory; a code patch is present only if code was created.

Update `prototype/prototype.md` only as needed to accommodate this method-neutral output. Its existing Experiment → Interrogate sequence remains.

### Interrogate with Experiment

Automatic trigger: the synthesized sketch contains an important falsifiable claim whose failure would affect correctness, security, reliability, compatibility, or an expensive-to-reverse architectural boundary, and a safe runnable target is available.

1. Architect identifies the specific intent, scope, material claim, and runnable target.
2. Existing Interrogate fans out independent adversaries.
3. Each adversary invokes `/experiment` to choose a CLI probe, test, simulation, or minimal throwaway app and attempt to refute the claim.
4. Each adversary reports only executed findings: command, actual output, expected output, relevance to intent.
5. The Interrogate coordinator independently reruns evidence, drops unverified claims, and merges shared root causes.
6. Architect records verified findings as proposed corrections; it does not silently rewrite the sketch.

If a Prototype/Experiment run is already interrogated, reuse that review rather than executing it twice. No findings is valid. When no runnable target can safely establish the claim, record the limitation and seek input only if a meaningful permission or business choice is required.

## Evidence outcomes and repeat policy

| Outcome | Architect action |
|---|---|
| Confirmed and compatible | Close factual question; cite evidence in rationale |
| Refuted/verified finding | Present proposed correction; wait for user acceptance |
| Inconclusive | Preserve unknown with missing evidence and impact |
| Unavailable tool/permission/sandbox | Record blocker; do not invent a result |
| Materially changed sketch | Recheck only invalidated assumptions |
| Same question and unchanged dependencies/sketch | Reuse earlier evidence; do not rerun |

Bound retries to avoid loops. Track question, sketch revision, environment/version, evidence path, and outcome in the existing artifact root/review log.

## Minimal implementation scope

| File | Change |
|---|---|
| `architect/SKILL.md` | Reference a new routing procedure and trigger it in Ground and review; keep existing phases and approval wording |
| `architect/references/evidence-routing.md` | **New:** routing conditions, skill handoff inputs/outputs, precedence, deduplication, and validity rules |
| `architect/interrogate/interrogate.md` | Tell reviewers to use `/experiment` for executable attacks; preserve independent verification and no-auto-fix contract |
| `architect/prototype/prototype.md` | Accept CLI-only/no-code Experiment reports; patch conditional, same existing review procedure |
| `architect/README.md` | Update the short human-facing flow and automatic trigger examples |

Leave `/research`, `/experiment`, Arena, `models.md`, `references/subagents.md`, `how/`, and `why/` unchanged. No new research-model role: `/research` owns its subagents.

## Implementation steps

1. Add the concise evidence-routing reference and link it from `SKILL.md`'s bundled-file table.
2. Add Ground and Phase C calls at points where questions or risks are known. Run evidence before presenting the next review round.
3. Add the Experiment handoff to Interrogate without replacing its adversarial selection or verification logic.
4. Make Prototype's output method-neutral while retaining worktree isolation and cleanup when code is created.
5. Update README examples and validate existing relative links and file references.
6. Test routing using mocked scenarios and review diffs for duplicated instructions or changed acceptance semantics.

## Acceptance criteria

- [ ] Missing external facts automatically invoke `/research` with explicit `@question` and `@outputShape`.
- [ ] Research delegates through its discovered specialists/subagents; Architect verifies returned evidence.
- [ ] CLI-resolvable uncertainty invokes `/experiment` and needs no throwaway application or patch.
- [ ] Runtime uncertainty can select a script, test, simulation, or throwaway app.
- [ ] Material, falsifiable design risks automatically invoke Interrogate.
- [ ] Interrogate reviewers use Experiment for executed proof and the coordinator independently reruns findings.
- [ ] Prototype's built-in Interrogate review is not duplicated.
- [ ] Unchanged evidence is reused; changed assumptions trigger focused reevaluation.
- [ ] Verified failures become proposed corrections, never unapproved sketch edits.
- [ ] Existing Arena 1–3 configuration, single-runner Judge behavior, human review, `accept` handoff, and `implement` gate are unchanged.
- [ ] Only the minimum necessary Architect files change; research/experiment internals remain untouched.
