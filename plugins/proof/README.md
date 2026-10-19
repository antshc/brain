# Proving AI Agent Work: Verification, Evidence, and Receipts

## 1. Overview

AI coding agents can generate implementations, pass unit tests, and successfully build applications while still failing to deliver the requested behavior.

The fundamental problem is that **an agent claiming completion is not evidence of correctness**.

The solution is to equip agents with deterministic verification tools that exercise the actual system, inspect observable outcomes, and produce reusable evidence.

This approach is discussed in two complementary sources:

- **Lauren Tan (@poteto):** The *Prove It Works* principle and project-specific verification skills in pstack.
- **Nick Nisi and Zack Proser (WorkOS):** The *Beyond Done* workshop, demonstrating a CLI-driven verification loop, structured receipts, and agent self-correction.

The central practice:

> Define what success means, execute a check against the real artifact, and require observable evidence before declaring the task complete.

This changes agent-driven development from an implementation-oriented process into an **outcome-oriented verification loop**.

## 2. Verify the Real Artifact, Not a Proxy

### The real-artifact principle

The *Prove It Works* principle requires verifying the actual result instead of trusting indirect signals.

For example:

- An application compiles, but its endpoint returns incorrect data.
- A unit test passes, but the real HTTP route is misconfigured.
- A browser displays a success message, but the submitted data is lost.
- A GitHub workflow reports success, but the expected release artifact was never published.

All four illustrate the same problem: **the available evidence does not establish the desired outcome**.

Verification must target the real artifact relevant to the claim.

| Claim | Appropriate verification target |
|---|---|
| A REST endpoint works | Running API over HTTP |
| An order is persisted | Actual database state and successful readback |
| A React feature works | Running application through browser interactions |
| A CLI command works | Actual executable with representative inputs |
| A migration preserves data | Migrated database and resulting records |
| A GitHub PR was created | GitHub API response |
| An application was deployed | Deployed endpoint and deployment state |
| A performance improvement exists | Comparable measured executions |

### Does proof require a real application?

**Yes, when the claim concerns application behavior.**

For a REST API, this normally means making requests to the running API rather than merely invoking service methods. For a React application, it means interacting with the running frontend, using a real browser when browser behavior matters.

However, a real application does not mean a production environment. Valid verification environments include:

- Local development instances.
- Containerized integration-test environments.
- Ephemeral preview deployments.
- Staging environments.
- Production, when appropriate and safe.

The important distinction is between executing actual application behavior and simulating it through a substitute that bypasses the behavior under test.

### Are mocked dependencies allowed?

Yes. The verification boundary depends on the requirement.

| Setup | What it establishes |
|---|---|
| Mocked order service called by a unit test | Controller or component behavior under controlled conditions |
| Real API and real application services | HTTP and service-layer behavior |
| Real API and PostgreSQL test container | HTTP behavior and database persistence |
| Real API, PostgreSQL, and mocked payment provider | Order behavior excluding the actual payment-provider integration |
| Real API, PostgreSQL, and payment-provider sandbox | Additional evidence of external integration behavior |

**Mocks may replace dependencies outside the verification boundary, but must not bypass the behavior the proof claims to test.**

The verifier must record which dependencies were real and which were simulated.

## 3. Define the Verification Contract Before Implementation

An agent cannot reliably prove completion without knowing what completion means.

Each task should define an observable result and an executable or inspectable way to verify it.

Example requirement:

> Creating an order must persist it, and subsequent requests must return the same order.

**Preconditions**

- The application is running.
- The database is initialized.
- A test user is authenticated.
- Required inventory exists.

**Actions**

1. Submit an order using the public HTTP API.
2. Retrieve the order through the API.
3. Verify the persisted database record.

**Expected outcomes**

- Creation returns HTTP 201.
- The response contains a valid order identifier.
- Retrieving the order returns submitted values.
- The database contains the corresponding record.

**Failure conditions**

- The API reports success without persisting the order.
- The retrieved order has incorrect values.
- The order disappears after restart, where durability is required.
- An unexpected error is observed.

This is a behavioral specification rather than a description of implementation details.

### Feature maps

Lauren Tan's [verification-skill example](https://github.com/poteto/verification-skill-example) and the WorkOS workshop demonstrate organizing application behavior into small feature descriptions.

A feature map typically identifies:

- What the feature does.
- How a user reaches it.
- How an agent can execute it.
- What observable result establishes success.
- Known pitfalls and misleading success signals.

For a large application, feature maps provide targeted context rather than requiring an agent to read an entire architecture or requirements document. The maps should evolve with the application: a feature change may require updating both the implementation and verification contract.

## 4. Evidence: What It Is and What It Establishes

**Evidence is recorded, observable information about what actually happened during verification.**

Evidence is not necessarily proof by itself. It becomes useful when evaluated against a defined requirement.

| Evidence | Example | What it establishes |
|---|---|---|
| HTTP trace | POST /orders returns 201 | The API accepted a request |
| HTTP readback | GET /orders/123 returns 200 | The API returned an order |
| Database record | SELECT returns the order | The record exists in the inspected database |
| Browser interaction | User clicks Submit | The intended UI action was executed |
| Screenshot | Confirmation page | What the application displayed |
| DOM snapshot | Order status = Confirmed | The rendered document's state |
| Browser storage | Stored email and status | Values present in browser storage |
| Console output | No observed exceptions | No exceptions captured during the observation window |
| Application logs | Request processed | Recorded application execution events |
| Test results | All assertions passed | Specified assertions were satisfied |
| External API response | GitHub confirms a PR exists | The PR exists in the queried repository |

### Evidence has limited scope

A screenshot of a success message does not prove data persistence.

An HTTP 201 response does not necessarily prove that the correct record was committed.

A database record does not necessarily prove that the user can retrieve it through the public API.

A passing test does not prove anything outside the behavior covered by its assertions.

Effective verification combines independent observations that support the required outcome.

### Positive and negative evidence

Evidence is useful even when verification fails.

Positive evidence might show that a record was created and retrieved successfully.

Negative evidence might show:

- No database record exists after a successful response.
- Browser state disappears after reload.
- A request unexpectedly returns HTTP 500.
- An operation emits an exception.
- A required assertion fails.

Negative evidence is especially valuable because it gives the coding agent concrete information for diagnosing and correcting an implementation.

## 5. Evidence, Verification, Proof, and Receipts

These concepts serve different purposes.

**Evidence:** Raw observations collected from the system: HTTP responses, database results, screenshots, logs, and browser storage snapshots.

**Verification:** Executing the system and evaluating its observations against expected outcomes.

~~~text
Expected: HTTP 201
Actual:   HTTP 201
Result:   PASS

Expected: Database contains order
Actual:   No matching record
Result:   FAIL
~~~

**Proof result:** The verifier's conclusion about a particular claim:

- **PASS:** Required checks completed and their assertions passed.
- **FAIL:** An observation contradicted at least one required assertion.
- **INCONCLUSIVE:** The verifier could not establish the outcome.

A failure to start the app, unavailable database, or missing test credentials may produce an inconclusive result rather than demonstrate a product defect.

**INCONCLUSIVE must never be treated as PASS.**

**Receipt:** A persisted, inspectable record connecting the verification result to supporting evidence.

A useful receipt includes:

- The claim being verified.
- Code revision or artifact digest.
- Verification environment and dependencies.
- Commands and inputs executed.
- Expected and actual results.
- PASS, FAIL, or INCONCLUSIVE.
- References to evidence artifacts.
- Execution time and relevant tool versions.

### Example receipt

~~~json
{
  "claim": "Creating an order persists data",
  "revision": "a7b93cf",
  "environment": "local-integration",
  "status": "PASS",
  "checks": [
    {
      "name": "Create order",
      "expected": 201,
      "actual": 201,
      "status": "PASS"
    },
    {
      "name": "Read order",
      "status": "PASS"
    },
    {
      "name": "Verify persistence",
      "status": "PASS"
    }
  ],
  "evidence": [
    "http-trace.json",
    "database-check.json",
    "application.log"
  ]
}
~~~

This illustrates a possible receipt format, not a mandated industry schema.

A receipt establishes the outcome only for the recorded scope, environment, inputs, and revision.

### How receipts relate to existing REST API E2E tests

**A receipt is not another test and does not execute assertions.** E2E tests check whether the running application behaves as expected. A receipt identifies **which tests ran, for which task and revision, what happened, and where the test evidence can be found**.

| Item | Responsibility |
|---|---|
| E2E test | Executes real application behavior and evaluates assertions |
| Evidence | Test results, HTTP traces, database checks, logs, or screenshots |
| Receipt | Compact record of the task, revision, environment, verdict, and evidence references |
| Proof workflow | Selects relevant verifiers, executes them, collects results, and returns an actionable completion verdict |

For example, an agent fixes issue **#123 — Order creation does not persist to PostgreSQL** and runs the existing suite:

~~~bash
dotnet test --filter "Category=Orders" \
  --logger "trx;LogFileName=results.trx"
~~~

The tests report **12 passed, 0 failed**. A minimal receipt could be a few lines of Markdown instead of a custom JSON schema:

~~~markdown
## Verification — Issue #123

Status: PASS (executed checks)
Commit: a7b93cf
Environment: Local ASP.NET Core API + PostgreSQL test container
Command: dotnet test --filter "Category=Orders"
Tests: 12 passed, 0 failed
Evidence: results.trx, application.log
~~~

The receipt does **not** mean that every requirement is satisfied merely because 12 tests passed. The agent or verifier must also establish that those tests cover the issue's acceptance criteria.

### What do you do with a receipt?

- **Pull request:** Link the receipt or CI run so reviewers can see exactly what was verified without trusting the agent's "done" message.
- **Agent implementation loop:** Read the PASS/FAIL/INCONCLUSIVE verdict. Use failure details to fix and rerun the relevant checks. PASS is meaningful only if required behavior is covered.
- **Later debugging:** Trace a historical result to a commit, environment, test selection, and available logs.
- **Continuous improvement:** Aggregate recurring failure categories or missing checks to improve tests, instructions, and tooling.

### When an existing CI run is already the receipt

If CI retains a **commit-linked test run, its logs, execution environment, and test artifacts**, it already provides most of the receipt's value.

For example, the agent's final verification summary can simply be:

~~~text
Issue: #123
Commit: a7b93cf
Verification: Orders E2E — 12 passed
Evidence: GitHub Actions run #456 (test results and logs)
~~~

Use an actual run URL in practice; the numbers above are illustrative. Do not duplicate TRX reports, screenshots, or logs merely to create a second set of files.

**Recommended minimal implementation for a Proof plugin:**

1. Select existing E2E/integration tests that cover the task's acceptance criteria.
2. Execute those tests using the existing runner or CI system.
3. Collect the verdict, commit SHA, environment, and references to retained artifacts.
4. Return a terse verification summary to the agent and optionally attach it to the PR.
5. Introduce a separate machine-readable receipt file **only if** cross-tool aggregation, historical comparison, or automated analysis needs one.

**A CI run can function as a receipt; a dedicated receipt schema is optional.** Preserve evidence where the testing infrastructure already stores it.

## 6. The WorkOS Example: A Feature That Looks Correct but Is Broken

The [Beyond Done workshop](https://github.com/workos/beyond-done) demonstrates verification using a fictional waitlist application called Midnight Snack Lab.

A visitor enters an email address and clicks the waitlist button. The interface displays a success message, but the implementation does not persist the email. After a reload, the waitlist information disappears.

### How the verifier finds the problem

The workshop introduces **snack**, a small application-specific CLI. Its commands drive a running Chromium browser using the Chrome DevTools Protocol.

~~~bash
pnpm snack reset
pnpm snack join ada@example.test
pnpm snack storage
pnpm snack reload
pnpm snack snapshot
pnpm snack prove
~~~

The critical observations are:

1. The user submits an email.
2. The application displays success.
3. The verifier inspects browser storage.
4. The verifier reloads the application.
5. The submitted email is missing.
6. Verification fails.

**Important:** This workshop app is intentionally browser-local. Its persistence contract uses **localStorage**, not PostgreSQL or a backend API. It is a real running application, but not a production registration system.

The demo illustrates why verification must match the actual application contract.

### The prove command

The workshop's prove command executes deterministic checks in a fresh browser context and saves a receipt.

| Exit code | Meaning |
|---|---|
| 0 | PASS |
| 1 | FAIL |
| 2 | INCONCLUSIVE |

The verifier associates receipts with the application's source revision. After source changes, the previous receipt is no longer accepted as proof of the new revision.

### The judge command

The workshop also demonstrates a model-based judge.

An application could persist an email correctly but display misleading text, such as a guaranteed seat confirmation. A deterministic persistence check might pass while the application violates the intended business meaning.

The judge evaluates that semantic discrepancy.

- **Deterministic assertions** check explicit technical conditions.
- **Model-based evaluation** can identify meaning-level mismatches.
- **Human review** remains useful for ambiguous, high-risk, or subjective requirements.

A model judge's answer is an evaluation signal, not independently conclusive proof.

## 7. Build a Small, Application-Specific Proof CLI

A proof tool should expose the minimum capabilities needed to operate and inspect the real application.

### Lifecycle

Start, stop, and diagnose the application and test dependencies.

~~~bash
proof up
proof doctor
proof down
~~~

### Drivers

Execute actions through relevant system interfaces:

- Send REST API requests.
- Navigate browser pages and click controls.
- Run CLI commands.
- Trigger supported application workflows.

### Observers

Collect state and execution information:

- HTTP request and response traces.
- Browser DOM and screenshots.
- Browser console and storage.
- Application logs.
- Database query results.
- External service responses.

### Assertions

Compare observed outcomes against the verification contract:

~~~text
HTTP status must be 201.
Saved order must match submitted values.
Email must survive a browser reload.
No unexpected console exception must occur.
~~~

### Receipts

Persist results and evidence for humans and agents to inspect or rerun.

An illustrative organization:

~~~text
proof/
  cli/
  drivers/
    http/
    browser/
  observers/
    database/
    logs/
  checks/
    orders/
    authentication/
  receipts/
~~~

The actual implementation can be much smaller. Reuse existing libraries rather than reimplementing HTTP clients, browser automation, database drivers, or test frameworks.

For .NET and React applications, common underlying tools include ASP.NET Core test infrastructure, HttpClient, Playwright, Testcontainers, and structured application logging.

The CLI primarily provides a stable, repeatable interface for agents.

## 8. Practical Example: .NET REST API and React

Consider:

- React frontend.
- ASP.NET Core REST API.
- PostgreSQL database.
- External payment provider.

The requirement is to verify an order-creation feature.

### Verification environment

Run:

- The real React application.
- The real ASP.NET Core API.
- An isolated PostgreSQL instance.
- A controlled payment-provider test double or sandbox.

Production is not required for local functional verification. Choose dependencies based on the claim under test.

### Example agent-facing commands

These commands illustrate a **proposed CLI**, not an existing WorkOS or pstack command interface.

~~~bash
proof doctor
proof up

proof orders create
proof orders read
proof orders persisted

proof orders verify

proof report
~~~

**Step 1 — API creation:** POST to the running API; check the status code and returned order ID.

**Step 2 — API readback:** GET the created order and compare the result with submitted values.

**Step 3 — Persistence:** Query the isolated PostgreSQL instance for the corresponding record.

**Step 4 — Frontend journey:** If frontend behavior is in scope, use Playwright to create an order through React; inspect the visible state and relevant reload/navigation behavior.

**Step 5 — Evidence capture:** Save HTTP traces, database assertions, browser observations, and application logs.

**Step 6 — Receipt:** Save a structured result that references all relevant evidence.

### Select verification depth by task

Not every change requires the entire stack.

- Pure function change: execute with actual representative inputs and deterministic output checks.
- API route change: HTTP-level verification.
- Persistence change: storage-level verification.
- Frontend workflow: browser-level verification.
- Deployment change: deployed-environment checks.

Use the narrowest boundary that directly establishes the claim, then add broader regression checks when risk warrants them.

## 9. Integrate Proof Into the Agent Development Loop

1. **Define the outcome.** Specify behavior and acceptance conditions.
2. **Establish a baseline.** Reproduce a bug or run current verification.
3. **Implement.** Let the coding agent modify the application.
4. **Run proof.** Execute the verifier against the resulting revision.
5. **Collect evidence.** Capture actual observations and failed assertions.
6. **Evaluate.** Return PASS, FAIL, or INCONCLUSIVE.
7. **Correct failures.** Feed specific failures to the coding agent and repeat.
8. **Preserve the receipt.** Keep passing evidence and run appropriate regressions.

Completion is determined by the verifier's results, not the agent's narration.

### Example feedback

~~~text
FAIL: Order persistence

POST /api/orders returned 201.
GET /api/orders/123 returned 404.
Database query found 0 matching records.

Expected:
Created order can be retrieved.

Observed:
Order is missing.

Evidence:
http-trace.json
database-check.json
application.log
~~~

This gives the agent actionable observations rather than a vague instruction to fix the feature.

### When the loop stops

The agent should report successful completion only when required checks pass for the current revision.

If the verifier cannot run, the result is inconclusive. The agent may fix the environment or report a clear blocker.

If a verification condition appears wrong, the agent must not silently weaken or delete it to get a passing result. Treat changes to verification contracts separately from application fixes.

## 10. Protect the Integrity of Proof

A verification system is trustworthy only if evidence reliably corresponds to the implementation.

### Bind evidence to a revision

Record a Git commit, artifact digest, or relevant source revision. A receipt becomes stale after code changes and must not automatically be reused.

### Isolate verification state

Use fresh browser contexts, test users, databases, and test data where necessary to prevent previous runs from causing false positives.

### Prevent verification bypasses

An agent should not be able to claim success by editing the proof result.

For stronger assurance:

- Keep required verification contracts reviewed or access-controlled.
- Run authoritative verification separately from the coding agent.
- Protect or independently validate verification scripts.
- Generate verdicts from executed assertions, not agent-authored prose.

### Test the verifier

A verifier that always passes is not useful.

The WorkOS workshop intentionally introduces bugs to see whether proof catches them.

Useful negative controls:

- Remove persistence and expect failure.
- Return the wrong email and expect failure.
- Display misleading confirmation text and expect detection.
- Introduce a console error and expect the appropriate check to fail.

### Handle sensitive evidence

Receipts may capture credentials, personal information, HTTP authorization headers, or database records. Minimize collection, redact sensitive values, and apply retention and access policies.

## 11. Use Receipts for Regression Testing and Agent Improvement

Receipts are useful beyond one task. Over time, recorded failures can reveal recurring weaknesses:

- Agents repeatedly omit persistence checks.
- Authentication breaks after certain refactors.
- Frontend changes trigger the same console failures.
- Integration tests miss a recurring deployment defect.

These patterns can improve:

- Verification contracts and regression tests.
- Agent instructions.
- Proof tooling.
- Development and release workflows.

For example, repeated cases where unit tests pass but persistence proof fails may justify adding an API-and-database verification scenario to the team's default workflow.

Historical receipts can also become datasets for future agent evaluation and self-improvement. However, they describe historical revisions and environments; they do not prove that the current application still works.

## 12. Recommended Engineering Practices

The following normative rules are practical recommendations informed by the sources, not verbatim requirements imposed by the authors.

### Verification contract

- **MUST** define observable completion criteria before implementation.
- **MUST** verify the actual artifact relevant to the claim.
- **MUST NOT** treat an agent's completion statement as proof.
- **MUST NOT** treat compilation or passing unit tests as sufficient for an untested end-to-end claim.

### Application execution

- **MUST** execute real application behavior when proving application functionality.
- **MAY** use isolated databases, test containers, staging, and controlled external dependencies.
- **MUST** disclose simulated dependencies that limit the claim.
- **SHOULD** verify observable behavior rather than implementation details.

### Evidence

- **MUST** compare expected and actual results.
- **MUST** distinguish PASS, FAIL, and INCONCLUSIVE.
- **MUST NOT** convert missing evidence or inconclusive results to PASS.
- **SHOULD** retain relevant requests, responses, state observations, logs, and artifacts.
- **SHOULD** capture enough context for diagnosis.

### Receipts

- **MUST** associate proof with the implementation revision.
- **MUST NOT** reuse stale receipts as current verification.
- **SHOULD** provide machine-readable results and supporting artifacts.
- **SHOULD** make verification independently repeatable.
- **MUST** protect sensitive evidence.

### Agent integration

- **SHOULD** provide a small, application-specific CLI or verification skill.
- **SHOULD** return explicit, actionable errors.
- **SHOULD** reuse existing test infrastructure.
- **SHOULD** protect authoritative checks from silent modification.
- **SHOULD** turn recurring failures into regression tests or tool improvements.

## 13. Conclusion

Reliable AI-assisted development requires separating **implementation from verification**.

An agent can write code, run tests, and propose that a task is complete. The completion decision should be grounded in observable behavior.

Effective proof needs four things:

1. **A clear contract:** What outcome must be true?
2. **A relevant execution:** What real artifact or behavior must be exercised?
3. **Observable evidence:** What facts demonstrate the result?
4. **A reproducible receipt:** What was checked, against which revision, and with what outcome?

A project-specific verification CLI turns these ideas into an executable development workflow.

Instead of asking an agent to explain why its implementation works, require it to demonstrate the result through repeatable checks.

**The objective is not to eliminate human judgment. It is to make routine correctness claims independently testable, observable, and auditable so humans can focus on genuinely uncertain decisions.**

## References

### WorkOS — Beyond Done

- [Workshop recording: Teach Your Agent to Prove It's Done](https://www.youtube.com/watch?v=q4WC4TowkBo)
- [Workshop repository](https://github.com/workos/beyond-done)
- [Waitlist verification contract](https://github.com/workos/beyond-done/blob/main/lab/verify/features/waitlist.md)

### Lauren Tan (@poteto) — Verification Practices

- [pstack: Verify and Ship guide](https://github.com/backnotprop/pstack/blob/main/docs/guide/06-verify-and-ship.md)
- [Verification Skill Example](https://github.com/poteto/verification-skill-example)
- [The Complete Guide to pstack — X post](https://x.com/poteto/status/2094457600259842065)

The .NET/React implementation scenario, proposed CLI interface, receipt schema, and normative checklist are illustrative engineering recommendations, not verbatim specifications from the referenced authors.
