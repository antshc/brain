# Verification Probes

These probes inspect and propose coverage; code and tests remain read-only. "Change" means a design change, not a source edit.

## Coverage categories

Trigger: a design answer changes behavior, persistence, or an integration boundary.

Check the `Crosscutting Concepts` index for a matching testing/verification Concept. *Run `explore-codebase` skill for read-only lookups locating tests and how a flow works* to compare existing tests/conventions against that Concept. If none matches, use evidenced code/test conventions alone.

Identify relevant test categories, reusable coverage, gaps, and proposed additions/updates/deletions. Cite evidence for existing coverage; unknown coverage stays unknown. Ask unresolved category decisions through the parent's decision flow.

## Functional-slice automation

Trigger: the design establishes or changes observable behavior; revisit a settled automation decision only when new behavior changes its scope.

Inspect functional-slice tests through the lookup contract. Discover applicable `testing-*` skills across available repository, user, and installed scopes. Invoke each selected skill by its exact name followed by `skill`, with 3–6 distinctive description keywords; use its test kinds, setup, commands, and seams as design guidance, not authorization to edit or execute tests.

Offer spec-wide automated verification through the highest existing useful seams. Propose observable scenario bullets; separate reusable coverage from gaps and ask for unresolved automation scope. Record approved, declined, or deferred scope through the parent's decision flow.

No applicable testing skill → use existing evidenced conventions. An inaccessible scope or failed required lookup → report the limitation and use the parent's failure protocol, not a claim that no skill/coverage exists.

Repository/accessor/proxy integration verification remains coding-agent work; the coverage-category probe may identify its needs without treating those tests as functional-slice automation.

Persist automation scope and scenario bullets for the handoff. Carry observable scenarios, decisions, and unknowns into the spec without test-file paths or fixed test-method names; keep source evidence in the ledger.
