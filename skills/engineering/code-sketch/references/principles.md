# Principles

Design principles cited by heading across this skill. Each section opens with when it applies.

## Contents

- Boundary discipline
- Encode lessons in structure
- Exhaust the design space
- Foundational thinking
- Laziness protocol
- Make operations idempotent
- Minimize reader load
- Outcome-oriented execution
- Redesign from first principles
- Separate before serializing shared state
- Subtract before you add

## Boundary discipline

Apply when wiring validation, error handling, or framework adapters.

Validate, narrow types, and handle errors at system boundaries (CLI args, config files, external APIs, network protocols): return errors, handle defensively. Trust internal code: typed data, error propagation, no re-validation. Business logic lives in pure functions; the shell is thin and mechanical.

**Why:** Scattered validation is noisy, redundant, and falsely reassuring. Logic outside framework wiring is testable without the framework.

- Validate config at parse time, not inside business logic.
- Parse raw data into domain types at the boundary; parse functions are pure transforms from raw bytes to typed state.
- Expose domain concepts across the boundary, not its private representation. Keep general-purpose mechanism inside and special-purpose policy at the edge.
- Do not re-export transport, storage, framework, or wire types through the public surface.
- No redundant nil checks deep in call chains once the boundary validated.
- Keep pure: prompt construction (structured state in, string out), scoring and assessment (state to results).

**The tests:**
- "Is this data crossing a system boundary right now?" If not, validation is redundant.
- "Can this be a pure function that the shell just calls?" If yes, extract it.

## Encode lessons in structure

Apply when writing the same instruction a second time or noticing a recurring correction. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text.

If the lesson needs judgment and cannot be encoded, make the instruction more prominent and add an example of the failure mode.

**Corollary:** when the fix is structural, use only the structural fix; the instruction is the symptom.

## Exhaust the design space

Apply when facing a novel UI interaction, an architectural decision with no precedent in the codebase, or a product design decision where experience depends on feel, not logic. Consider competing whole-shape designs before committing; record the rejected shapes in the rationale's Alternatives considered.

## Foundational thinking

Apply before writing logic: choosing core types and data structures, sequencing scaffold-vs-feature work.

**Structural decisions** protect option value. **Code-level decisions** protect simplicity.

**Data structures first.** Define core types early, trace every access pattern, and choose structures that match the dominant paths before writing logic.

DRY the structure, not every line; types and data models converge. Three similar statements beat a premature abstraction. Prefer explicit over clever. Test behavior and edge cases, not line counts.

**Scaffold first.** Do first what helps every later phase (CI, linting, test infrastructure, shared types); ask "does every subsequent phase benefit from this existing?" Sequence for option value: setup before features, tests before fixes. Keep commits small and single-purpose.

Each increment lands a coherent abstraction or deepens one that exists; do not spread a new capability across callers as special-case coordination.

## Laziness protocol

Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. Bias toward deletion and the smallest change that solves the problem.

- **Consolidate decisions.** Put each choice behind one source of truth and pass the result as a simple flag.
- **Minimize the diff.** Fewer lines beat "elegant" boilerplate.

## Make operations idempotent

Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries.

Design operations to converge to the correct state however many times they run or wherever the previous run stopped. Every state-mutating operation answers: "What happens if this runs twice? What happens if the previous run crashed halfway?"

**Why:** If partial state changes the next run's outcome, every restart becomes a debugging session.

Derive each step from the state that exists, not from what the previous run meant to do: read the current state, compare it to the goal, apply only the difference. A repeat then finds nothing left to do.

Anything a run leaves behind (lock, temporary file, half-written record, claimed job) must be recognizable as stale by the next run. Judge staleness by evidence that stays true wherever the previous run could have stopped, not only in the common case. A marker the next run cannot judge turns every crash into manual cleanup. For example, write to a temporary path and rename it into place, or compare artifacts by content instead of creation order.

**The test:**
1. What happens if this runs twice in a row?
2. What happens if the previous run crashed at every possible point?
3. Does re-execution converge to the same end state?

If any answer is "it depends on what state was left behind," add a reconciliation step.

## Minimize reader load

Apply when reviewing or shaping code that is hard to trace.

Maintainability is the work a reader must do to understand code. Track two independent axes: **layers to trace** (indirections between the question and the answer) and **state to hold** (hidden or mutable context the reader must keep in their head). LOC, cyclomatic complexity, and "clean architecture" are proxies. A flat file with 50 globals can be as hard to reason about as a 6-layer adapter stack. Guard both.

- **Collapse layers** that cost more than they save: wrappers with one caller, adapters with no second implementation, speculative indirection. Inline them.
- **Shrink state scope:** prefer pure functions (returns over mutations), locals over fields, fields over module state, and module state over globals. Derive instead of sync.
- **Name the invariant at the boundary,** not in every consumer, so the reader learns it once.
- Before adding a layer or state, ask: does it reduce reader load elsewhere by at least as much?

**The test:** can a new reader answer "where does X come from?" and "what can change X?" in under 30 seconds? If not, cut layers or cut state.

## Outcome-oriented execution

Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; skip throwaway compatibility code that preserves smooth intermediate states.

**Why:** Keeping every intermediate step fully stable creates temporary compatibility code that becomes long-lived debt.

- Prioritize end-state integrity over transitional stability.
- Intermediate breakage is acceptable when planned, scoped, and reversible; declare where.
- Keep high-signal checks for actively touched areas while migrating.
- Require full static and runtime verification at plan completion.

## Redesign from first principles

Apply when integrating a new requirement into an existing design. Redesign as if the requirement had been a foundational assumption from the start; do not bolt it on.

- Read all affected files and understand the current design.
- Ask: "if we were writing this from scratch with this new requirement, what would we build?"
- Propagate the change through every reference: types, docs, examples, rationale sections.
- Think about the whole redesign, then deliver it incrementally.

## Separate before serializing shared state

Apply when concurrent actors might write to the same file, branch, key, or state object.

First ask whether they need the same mutable object. If not, eliminate the sharing. When sharing is real, enforce serialization structurally: lockfiles, sequential phases, exclusive ownership. Instructions and conventions are not concurrency control.

**Why:** Concurrent writes to shared state create intermittent, hard-to-reproduce race conditions.

1. **Identify shared mutable state** (files both read and write, branches both push to, APIs both define and consume).
2. **Default: eliminate the shared write target.** Ask: do these actors need one canonical object, or are they publishing independent facts? Give each actor its own owned file, key, branch, or state directory, and merge only at the read/reporting boundary. Two workers writing their own `lastX` field into one `state.json` is still shared mutation. `indexer-state.json` + `metrics-state.json` is not.
3. **Only when one shared write target is a real invariant, serialize access structurally** (lockfiles, sequential phases, single-writer actor, or atomic compare-and-swap). Treat "we need a lock" as a design smell to check, not the default answer.

## Subtract before you add

Apply when sequencing an addition, refactor, or rewrite. Default to subtraction: remove complexity first, then build. Leave the design slightly simpler and more capable behind the same or smaller surface than you found it.

- Sequence removal before construction; remove dead code before laying foundations.
- Cut before you polish: reach the minimum before investing in quality.
- Design for observed usage, not speculative edge cases.
- Add no speculative validators, parsers, or guards beyond what the spec demands.
