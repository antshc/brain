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
**Harness environment**:
The repository that owns the milestone/issues and hosts the docs. Separate from the **Codebase Repo Path** when a **Harness Repo Path**/workspace folder exists; otherwise the two are the same.
**Harness Repo Path**:
The repository that owns the milestone/issues and hosts the repo-local development workflow, resolved once by the entry-point skill (`resolve-harness`/`setup-harness`) and passed explicitly downstream rather than re-derived by each component. Distinct from the `Codebase Repo Path` and `Worktree Path`, though one repository can serve all three roles.
_Avoid_: repo root, home repo, harness root
_Plugins_set_: ralph, crew, wf

**Codebase Repo Path**:
The Git repository containing the source code Ralph develops, resolved once alongside the `Harness Repo Path` by the entry-point skill and supplied explicitly to `/create-worktree`. Distinct from the `Harness Repo Path` and `Worktree Path`, though it can also be the Harness Repo Path.
_Avoid_: codebase, source checkout, source repository
_Plugins_set_: ralph, wf

**Worktree Path**:
The git worktree Ralph uses for code, Git, build, test, and PR operations. Ralph launches the crew agents from it when applicable; each agent treats its invocation directory as its workspace and does not receive this path.
_Avoid_: working directory, checkout
_Plugins_set_: ralph, crew, wf

**Ledger**:
A session-scoped record, persisted via the memory tool at `/memories/session/domain-model-ledger.md`, of every Concept/ADR/service doc opened so far in the session — one line per record, checked before discussing any module, boundary, or service to avoid re-opening or re-scanning the index.
_Avoid_: log, history
_Plugins_set_: wf

**Trigger Indexer**:
The mechanism that owns an index table end to end — abstract over any table with a Trigger condition column (Services, ADRs, Concepts, or custom tables): generates concise, domain-specific phrases natural to grilling, keeps caller-supplied row cells in sync on add/supersede/retire, and semantically matches clauses against the current change's touched surface and grilling context before opening linked records. Blank Trigger condition cells never match, and columns the caller did not name are preserved.
_Avoid_: local RAG, index scanner, retrieval index
_Plugins_set_: wf

## ralph
### Language

## crew
### Language

**Codey**:
The implementation agent. Implements one task in its invocation directory and returns the five-field report that alone governs `ralph:dev`'s distill, commit, and issue-handling steps.
_Avoid_: droid, implementer, coder

**Chorey**:
The maintainability-review agent. Reviews the change set for behavior-preserving refactors — Codey's checkpoint commit (named by a trusted `BASELINE_COMMIT`) inside the loop, or uncommitted work standalone — runs only behind a Codey `STATUS: complete` gate, reports informationally, and discards its own refactors (git-native revert against the checkpoint, or a manual snapshot standalone) when its verification cannot pass.
_Avoid_: reviewer, refactorer, cleanup agent

**Convention folder**:
The per-repo `.crew/` directory under the `Harness Repo Path` holding `CODE.md`, `VERIFY.md`, `CHORE.md`, and `GOTCHAS.md` — the single location a crew agent resolves them from, never discovered or searched for.
_Avoid_: .droid, config folder, settings directory

**Gotchas**:
Reusable directives stored with the `crew-gotchas` skill. Read and applied before implementation; after feedback loops pass, the agent distills session friction (convention conflicts, directory/tool access issues) into new directives or extensions of existing ones and writes them back directly — no human curation step.
_Avoid_: decisions, durable decisions, problem log

**Module**:
The unit of code plus its build config, identified by walking up from a changed file to the nearest build-config marker — discovered from the repo's own structure during `crew-feedback`, never assumed or named by the skill.
_Avoid_: project, package

**Verification counterpart**:
The sibling/child unit that verifies a Module (tests, specs, or whatever the repo calls it), discovered the same way as its Module during `crew-feedback`.
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

- **ralph → crew**: Consumers install `ralph` in the `Harness Repo Path` to use its development workflow. Ralph resolves the `Harness Repo Path` and `Codebase Repo Path` once via `resolve-harness`, creates the `Worktree Path`, and launches `Codey` from that directory — falling back to a general-purpose agent when Codey is unavailable — handing it `HARNESS_REPO_PATH` through a trusted `## HARNESS` prompt section. `Chorey` follows only on a Codey `STATUS: complete`, and is skipped when unavailable. Each agent treats its invocation directory as its workspace and validates the supplied path rather than discovering it.
- **crew ↔ Shared**: crew agents read skill-owned implementation, verification, and review guidance from the `Convention folder` before changing code, then write distilled `Gotchas` back to the reference owned by `crew-gotchas` after feedback loops pass.

