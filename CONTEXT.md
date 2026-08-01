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
The repository the loop is invoked from — it owns the milestone and issues, the docs, and the installed Ralph skills. When it contains no `workspace/` folder it is also the `Source Repository`, and development happens in it directly. When `workspace/` exists, the Harness Root holds only the harness and delegates all code to the `Source Repository` beneath it.
_Avoid_: repo root, home repo
_Plugins_set_: ralph, wf

**Source Repository**:
The Git repository holding the codebase Ralph develops, and the parent of its worktrees. It is the repository under `workspace/` when that folder exists (e.g. `workspace/ecom/.git`, with worktrees at `workspace/ecom.worktrees/`), otherwise the `Harness Root` itself. Never the location of milestones, issues, or installed skills unless it is also the Harness Root.
_Avoid_: codebase, source checkout
_Plugins_set_: ralph, wf

**Worktree Path**:
The git worktree Ralph uses for code, Git, build, test, and PR operations, created as a sibling of the `Source Repository` under `<Source Repository>.worktrees/<feature-branch>`. Ralph launches Codey and Chorey from it; each agent treats its invocation directory as its workspace and does not receive this path.
_Avoid_: working directory, checkout
_Plugins_set_: ralph, wf

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

**Codey**:
Ralph's technology-agnostic implementation agent.
_Avoid_: coding agent
_Plugins_set_: ralph

**Chorey**:
Ralph's technology-agnostic refactoring agent.
_Avoid_: review agent, cleanup agent
_Plugins_set_: ralph

**Gotchas**:
Reusable directives shared by Codey and Chorey through the `ralph-gotchas` skill.
_Avoid_: decisions, durable decisions, problem log
_Plugins_set_: ralph

**Module**:
The unit of code plus its build config, identified by walking up from a changed file to the nearest build-config marker — discovered from the repo's own structure during `ralph-feedback`, never assumed or named by the skill.
_Avoid_: project, package
_Plugins_set_: ralph

**Verification counterpart**:
The sibling or child unit that verifies a Module, discovered with its Module during `ralph-feedback`.
_Avoid_: test project, test suite
_Plugins_set_: ralph

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

- **ralph ↔ Shared**: Ralph resolves the `Source Repository` and `Worktree Path`; Codey and Chorey treat their invocation directory as the workspace and share skill-owned guidance and `Gotchas`.

