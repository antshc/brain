# Leading words
<!--
 **Leading Word**- A compact concept — also called a _Leitwort_ — already living in the model's pretraining, that the agent thinks with while running the skill. It encodes a behavioural principle in the fewest possible tokens by invoking priors the model already holds (e.g. _lesson_, _proximal zone of development_, _fog of war_, _tracer bullets_). Repeated as a token, never as a sentence, it accumulates a distributed definition across the skill and anchors a whole region of behaviour. Coining your own works if you define it clearly, but a made-up word recruits no priors — you pay in definition tokens what a pretrained word gives free. Reach for an existing word first.

A leading word serves **predictability** twice. In the body it anchors **execution** — the agent reaches for the same behaviour every time the concept appears, and inside flat reference it focuses attention on a class of thing to look for, recruiting the right checks each run. In the **description** it anchors **invocation** — and not only within the skill: when the same word lives in your prompts, your docs, and your codebase, the agent links that shared language to the skill and fires it more reliably. Word a description with the leading words you actually use when you want the skill.
-->

**Fact**:
Information discoverable by exploring the codebase (validation rules, constraints, domain concepts, data models, contracts, schemas, relationships, business logic) — looked up directly during grilling, never asked of the user.
_Avoid_: assumption, guess
_Plugins_set_: wf

**Decision**:
A resolved choice that is the user's call, not derivable from the codebase — put to the user during grilling and captured only once they confirm it.
_Avoid_: fact, assumption
_Plugins_set_: wf

# Contexts
## Shared

Location: plugins/

Terms used across more than one plugin — not owned by a single plugin's context.

### Language
**Harness Root**:
The repository that owns the milestone/issues, the convention docs (`CODE.md`, `VERIFY.md`), and the agent state files (`agent/LOG.md`, `agent/MEMORY.md`). Distinct from the `Worktree Path`, though it can be the same repo.
_Avoid_: repo root, home repo
_Plugins_set_: ralph, pet, wf

**Worktree Path**:
The git worktree the agent executes all code, git, build, and test commands in. The agent `cd`s into it as its first action when provided.
_Avoid_: working directory, checkout
_Plugins_set_: ralph, pet, wf

## ralph
### Language

## pet
### Language

**Problem Log**:
An append-only record in `agent/LOG.md` of conflicts, access failures, or other friction an agent hit during a session (convention conflicts, directory/tool access issues). Written by the agent at the end of a session; curated by a human into Guardrails.
_Avoid_: decision log, decisions.jsonl

**Guardrails**:
Curated, human-reviewed directives stored in `agent/MEMORY.md`, distilled from recurring entries in the Problem Log. Read-only from the agent's perspective — applied before implementation, never written by the agent.
_Avoid_: decisions, durable decisions

## wf

### Language

**Ledger**:
A session-scoped record, persisted via the memory tool at `/memories/session/domain-model-ledger.md`, of every Concept/ADR/service doc opened so far in the session — one line per record, checked before discussing any module, boundary, or service to avoid re-opening or re-scanning the index.
_Avoid_: log, history
_Plugins_set_: wf

**Completeness sweep**:
A closing check, run before concluding a session that opened at least one full Concept/ADR record, that outputs one disposition line (`Applied`, `Not applicable`, `Violated`, or `Superseded`) per row in `ARCHITECTURE.md`'s Crosscutting Concepts and Architecture Decision Records index tables.
_Avoid_: final review, wrap-up
_Plugins_set_: wf

## review

### Language

**Review comment**:
A finding one review axis discovered and returned, anchored to the change (`AXIS`, `FILE_PATH`, `LINE_NUMBER`, `LABEL`), with its body phrased `issue → impact → fix`.
_Avoid_: comment, finding, issue

**Review axis**:
One independent review dimension performed by its own standalone skill (`quality`, `smells`, `reqs`) — each parses the PR, fetches the diff, reviews inline, and posts its own comments.
_Avoid_: review type, review category, sub-agent

**Review guidance file**:
The `<axis>-review-guidance.md` co-located with a review axis skill, holding that axis's checklist/baseline, LSP workflow, review rules, and output contract.
_Avoid_: checklist.md, agent instructions

# Relationships

- **ralph → pet**: `ralph`'s `dev` skill resolves `Harness Root` and `Worktree Path` and passes them to the `pet` plugin's `csdroid` agent, which cds into `Worktree Path` and derives all `pet` state paths from `Harness Root`.
- **pet ↔ Shared**: `pet`'s `Guardrails` (`agent/MEMORY.md`) and `Problem Log` (`agent/LOG.md`) are both persisted at fixed paths under `Harness Root`, a `Shared` term.

