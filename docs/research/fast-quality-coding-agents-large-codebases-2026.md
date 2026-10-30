# Research: Fast, High-Quality Coding Agents for Large Codebases

**Research date:** 2026-10-30  
**Scope:** Coding-agent implementation loops, large repositories, TDD alternatives, incremental feedback, and independent verification.  
**Status:** Completed — recommendations not yet implemented.

## Question

How should a coding implementer agent work quickly in a large, established codebase without weakening correctness or maintainability? Is mandatory red–green–refactor the best default?

## Bottom line

**Recommendation (synthesis, not an industry standard):** Use risk-based, evidence-driven implementation. Make verification mandatory, but select test ordering and scope by the nature of the change. Use TDD for bug regressions and complex/uncertain behavior; use focused test-after implementation when behavior and boundaries are clear; use characterization tests before behavior-preserving refactors. Run the fastest meaningful checks during development and broader independent verification before delivery.

There is **no measured evidence in the sources below** that replacing TDD universally improves end-to-end delivery speed without affecting defect rates. The proposal should be evaluated on comparable tickets.

## Findings from primary sources

1. **Map the repository; load context progressively.** OpenAI's harness-engineering team describes short agent entry-point instructions that link to authoritative architecture, plans, and detailed documentation. Overloading agents with one large instruction file causes context crowding and drift. [OpenAI, Harness Engineering](https://openai.com/index/harness-engineering/).
2. **Use scoped work units.** OpenAI recommends a plan before large changes and focused coding tasks. Cursor's long-running agent experiments separated planners from workers, with workers owning specific tasks; these are practitioner results, not proof of universal optimality. [OpenAI, How OpenAI Uses Codex](https://openai.com/business/guides-and-resources/how-openai-uses-codex/); [Cursor, Scaling Agents](https://cursor.com/blog/scaling-agents).
3. **Give the agent executable feedback.** Anthropic describes test-first red–green loops as effective when expected inputs and outputs are known, and also emphasizes independent review and observable targets. It does not establish that TDD is required for every change. [Anthropic, Claude Code Best Practices](https://www.anthropic.com/research/claude-code-best-practices).
4. **Enforce architectural invariants mechanically.** OpenAI uses architecture/structural tests, custom linters, and restricted dependency directions so agents can work autonomously within constraints. [OpenAI, Harness Engineering](https://openai.com/index/harness-engineering/).
5. **Provide build/test instructions and prepared environments.** GitHub recommends repository instructions and preinstalled dependencies so Copilot can compile, test, and validate reliably without slow discovery through trial and error. [GitHub, Get the Best Results](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results).
6. **Independent review benefits from whole-repository tools.** OpenAI reports better detection of critical issues and fewer false positives when code reviewers can navigate and execute repository code, versus only reading a diff. [OpenAI, Verifying Code at Scale](https://alignment.openai.com/scaling-code-verification/).
7. **Optimize test time without deleting test coverage.** In an October 2026 report, OpenAI describes reducing median CI from about 10 to 4.5 minutes; one 63-test suite improved from 592.6 to 29.8 seconds after a missing mock was added. These are case studies, not general speed guarantees. [OpenAI, Maintaining Software with GPT-6](https://developers.openai.com/blog/maintaining-software-with-the-gpt-6-family).
8. **Test at multiple seams.** Google's testing guidance supports unit, integration, and critical-journey E2E testing as complementary layers. [.Google Testing Blog, How Much Testing Is Enough?](https://testing.googleblog.com/2021/06/how-much-testing-is-enough.html).

## Options

| Strategy | Good fit | Main risk |
| --- | --- | --- |
| Mandatory TDD for each increment | Uncertain domain behavior, critical logic | Repeated agent/tool loops; may over-specify internals |
| Test-after with behavioral checks | Straightforward feature, existing stable contracts | Implementation-biased tests; incomplete negative cases |
| Characterization first | Legacy refactoring | Characterizing accidental behavior as desired |
| Contract-first | Public APIs, serialization, service boundaries | Contract alone may miss runtime integration |
| Existing checks only | Truly mechanical edits with proven coverage | Missed behavior if change is misclassified |
| **Risk-based combination** | General-purpose implementer | Requires explicit classification and a dependable verifier |

**Inference:** Risk-based selection is likely to reduce unnecessary iteration while retaining the necessary correctness checks. Validate this empirically rather than assuming it.

## Recommended implementer flow

1. **Explore scope.** Read the ticket and acceptance criteria. Find affected symbols, callers, external boundaries, nearby conventions, actual test counterparts, and the smallest project/build boundary. Stop when the relevant context is sufficient.
2. **Select a strategy.** Identify changed behavior and classify risk. Choose TDD for bug reproduction/high-risk uncertain logic; characterization before refactoring; contracts for interface changes; focused test-after for straightforward features.
3. **Implement a thin, coherent slice.** Prefer existing models, utilities, test fakes, layering, and naming; avoid speculative abstractions and unrelated cleanup.
4. **Run fast feedback.** Compile the affected project and run filtered tests after meaningful increments, not after every trivial edit. Confirm that the intended tests actually ran and passed. The .NET CLI supports test selection with `dotnet test --filter`. [Microsoft, Selected Unit Tests](https://learn.microsoft.com/en-us/dotnet/core/testing/selective-unit-tests).
5. **Complete behavioral coverage.** Add regression, boundary, and integration tests as needed, including failure paths and impacted interfaces. A passing local test is evidence only for the behavior it actually exercises.
6. **Handoff evidence.** Report changed behavior, commands executed, results, tests not run, and any unresolved risks. Never report an intended or skipped check as passed.

### Verification levels

| Level | Owner | Scope | Trigger |
| --- | --- | --- | --- |
| Fast feedback | Implementer | Affected project, selected tests, diagnostics | Meaningful implementation increments |
| Focused completion | Implementer | All relevant changed behavior and affected integrations | Before handoff |
| Independent verification | Verifier and code review | Acceptance criteria, boundary behavior, architecture, omissions | After implementation |
| Broad regression | CI/delivery workflow | Required broader suites and system checks | Before merge/release according to repository policy |

### Non-negotiable constraints

- **MUST** verify every material changed behavior with suitable observed evidence. *Rationale:* Test order may vary; confidence must not.
- **MUST** run relevant integration tests when changed boundaries can invalidate them. *Rationale:* Unit success does not prove external behavior.
- **MUST NOT** weaken or rewrite a valid test merely to obtain a green result, even if faster. *Rationale:* Prevents adapting the oracle to a bug.
- **MUST** preserve architectural constraints and existing conventions, even if a shortcut seems simpler. *Rationale:* Large-codebase consistency limits maintenance cost.
- **MUST NOT** run full solution suites on every edit unless the change's impact requires it. *Rationale:* Repeated expensive feedback reduces throughput without adding proportional evidence.
- **MUST NOT** skip required checks merely to improve runtime, even if faster. *Rationale:* Speed optimization cannot silently reduce the acceptance bar.
- **MUST** distinguish passed, failed, unavailable, and unexecuted checks. *Rationale:* The next stage needs trustworthy evidence.

## Specific implications for antshc/brain

The current [implementer agent](https://github.com/antshc/brain/blob/main/plugins/wf/skills/implement-spec/agents/implementer.md) already:

- Uses red–green–refactor **where applicable**, not unconditionally.
- Discovers the affected build/test boundary and actual test counterparts.
- Runs filtered unit/integration tests and skips solution-wide suites by default.
- Requires higher-seam integration verification for changed external boundaries.
- Reports observed verification and gaps.

**Do not replace this existing contract wholesale.** If optimizing it later, focus on making test-strategy selection more explicit and measuring repeated test/build costs. Preserve integration gates, failure handling, the one-commit rule, and the JSON handoff contract.

The adjacent verifier and code-review stages should remain independent. A change to the implementer must not silently weaken their checks.

## Evaluation plan

Run comparable ticket sets under the existing and proposed policies (ideally on the same repository snapshots). Track:

- End-to-end ticket time, not only first-code time.
- Agent tool calls, tokens, and execution cost.
- Build and test duration, including repeated runs.
- First-pass verifier success and review defects.
- Rework rounds and escaped regressions.
- Acceptance-criteria coverage and integration gaps.

Accept the proposed policy only if it improves throughput while maintaining or improving quality metrics. Use high-risk tickets separately; averages can hide regressions in critical changes.

## Open questions

1. Which change classes in the target repository require test-first behavior regardless of speed?
2. Can impacted test projects be selected reliably from dependency graph and test history?
3. Which checks belong to implementer, independent verifier, and CI without redundant execution?
4. What baseline distribution of ticket time and defects should be used for evaluation?

## Sources

- [OpenAI — Harness Engineering (2026)](https://openai.com/index/harness-engineering/)
- [OpenAI — How OpenAI Uses Codex (2026)](https://openai.com/business/guides-and-resources/how-openai-uses-codex/)
- [OpenAI — A Practical Approach to Verifying Code at Scale (2025)](https://alignment.openai.com/scaling-code-verification/)
- [OpenAI — Maintaining Software with the GPT-6 Family (2026)](https://developers.openai.com/blog/maintaining-software-with-the-gpt-6-family)
- [Anthropic — Claude Code Best Practices (2025)](https://www.anthropic.com/research/claude-code-best-practices)
- [GitHub — Get the Best Results with Copilot Cloud Agent](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results)
- [Cursor — Scaling Long-running Autonomous Coding (2026)](https://cursor.com/blog/scaling-agents)
- [Google Testing Blog — How Much Testing Is Enough?](https://testing.googleblog.com/2021/06/how-much-testing-is-enough.html)
- [Microsoft — Run Selected Unit Tests](https://learn.microsoft.com/en-us/dotnet/core/testing/selective-unit-tests)
