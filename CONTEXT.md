# Leading words
<!--
 **Leading Word**- A compact concept — also called a _Leitwort_ — already living in the model's pretraining, that the agent thinks with while running the skill. It encodes a behavioural principle in the fewest possible tokens by invoking priors the model already holds (e.g. _lesson_, _proximal zone of development_, _fog of war_, _tracer bullets_). Repeated as a token, never as a sentence, it accumulates a distributed definition across the skill and anchors a whole region of behaviour. Coining your own works if you define it clearly, but a made-up word recruits no priors — you pay in definition tokens what a pretrained word gives free. Reach for an existing word first.

A leading word serves **predictability** twice. In the body it anchors **execution** — the agent reaches for the same behaviour every time the concept appears, and inside flat reference it focuses attention on a class of thing to look for, recruiting the right checks each run. In the **description** it anchors **invocation** — and not only within the skill: when the same word lives in your prompts, your docs, and your codebase, the agent links that shared language to the skill and fires it more reliably. Word a description with the leading words you actually use when you want the skill.
-->

**Facet**
one particular aspect, side, or feature of something.

**Fact**:
Information discoverable by exploring the codebase (validation rules, constraints, domain concepts, data models, contracts, schemas, relationships, business logic) — looked up directly during grilling, never asked of the user.
_Avoid_: assumption, guess
_Plugins_set_: wf

**Decision**:
A resolved choice that is the user's call, not derivable from the codebase — put to the user during grilling and captured only once they confirm it.
_Avoid_: fact, assumption
_Plugins_set_: wf

**Seam**:
A place in the codebase where a test can observe or alter behavior without changing the code at that point. Existing seams are preferred over new ones, and the highest seam through which a feature can still be verified is preferred over a lower one — the fewer seams a change introduces, the better.
_Avoid_: test point, hook, injection point
_Plugins_set_: wf

**Prior art**:
Existing tests in the codebase of the same type as the ones being planned for a change — surfaced and followed as the pattern for new tests instead of inventing a new testing style.
_Avoid_: existing tests, precedent
_Plugins_set_: wf

**Verbatim**:
Copied exactly as written, with no paraphrasing, summarizing, or restructuring — used to mark content (a template, a settings block) that must be reproduced word-for-word rather than reinterpreted.
_Avoid_: as-is, unmodified
_Plugins_set_: wf

# Contexts
## Shared

Location: plugins/

Terms used across more than one plugin — not owned by a single plugin's context.

### Language
**Harness Root**:
The repository that owns the milestone/issues, convention docs, and agent state files. Droid resolves `CODE.md`, `VERIFY.md`, `MEMORY.md`, and `LOG.md` recursively beneath it once during INPUT; when no log exists, it creates `.droid/LOG.md`. Distinct from the `Worktree Path`, though it can be the same repo.
_Avoid_: repo root, home repo
_Plugins_set_: ralph, droid, wf

**Harness Configuration File**:
The optional `.harness.env` file at a repository root that must declare its `HARNESS_ROOT` and may declare additional harness settings. A resolver searches ancestor directories for the nearest file without changing the filesystem; when none exists, the caller uses its documented fallback.
_Avoid_: environment file, repo configuration
_Plugins_set_: harness, ralph, droid

**Harness Settings**:
The complete set of `KEY=VALUE` entries returned verbatim by `resolve-harness` from the nearest Harness Configuration File. A caller retains the set for its invocation; without a resolver or configuration file, it uses only its current directory as `HARNESS_ROOT`.
_Avoid_: environment variables, process environment
_Plugins_set_: harness, ralph, droid

**Worktree Path**:
The git worktree Ralph uses for code, Git, build, test, and PR operations. Ralph launches Droid from it when applicable; Droid treats its invocation directory as its workspace and does not receive this path.
_Avoid_: working directory, checkout
_Plugins_set_: ralph, droid, wf

**Ledger**:
A session-scoped record, persisted via the memory tool at `/memories/session/domain-model-ledger.md`, of every Concept/ADR/service doc opened so far in the session — one line per record, checked before discussing any module, boundary, or service to avoid re-opening or re-scanning the index.
_Avoid_: log, history
_Plugins_set_: wf

**Trigger Indexer**:
The mechanism that owns an index table end to end — abstract over any table with a Trigger condition column (not limited to Concepts/ADRs): keeps each record's row in sync with its Trigger condition and summary on add/supersede/retire, and on the read side scans the table, matches its Trigger condition clauses against the current change's touched surface, and opens only the matching full records before they inform generation.
_Avoid_: local RAG, index scanner, retrieval index
_Plugins_set_: wf

## ralph
### Language

## droid
### Language

**Problem Log**:
An append-only `LOG.md` record of conflicts, access failures, or other friction an agent hit during a session (convention conflicts, directory/tool access issues). Its path is resolved during INPUT; it is written by the agent at the end of a session and curated by a human into Guardrails.
_Avoid_: decision log, decisions.jsonl

**Guardrails**:
Curated, human-reviewed directives stored in the `MEMORY.md` resolved during INPUT, distilled from recurring entries in the Problem Log. Read-only from the agent's perspective — applied before implementation, never written by the agent.
_Avoid_: decisions, durable decisions

**Module**:
The unit of code plus its build config, identified by walking up from a changed file to the nearest build-config marker — discovered from the repo's own structure during `droid-feedback`, never assumed or named by the skill.
_Avoid_: project, package

**Verification counterpart**:
The sibling/child unit that verifies a Module (tests, specs, or whatever the repo calls it), discovered the same way as its Module during `droid-feedback`.
_Avoid_: test project, test suite

## wf

### Language

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

- **ralph → droid**: `ralph` creates the `Worktree Path` and launches the `droid` plugin's `droid` agent from that directory. Droid independently resolves `Harness Settings` during INPUT, then resolves its convention/state file paths under the resulting `Harness Root`.
- **droid ↔ Shared**: `droid` resolves `Guardrails` (`MEMORY.md`) and the `Problem Log` (`LOG.md`) under `Harness Root` during INPUT; it creates `.droid/LOG.md` only when no existing log is found.

