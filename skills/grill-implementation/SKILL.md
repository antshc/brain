---
name: grill-implementation
description: Interview the user until implementation choices are resolved, then print a concise list of approved implementation decisions. Use when the user wants to define, clarify, or stress-test how a feature, fix, or design should be implemented.
disable-model-invocation: true
---

# Grill Implementation

<HARD-GATE>

Do not invoke implementation skills, write code, scaffold projects, modify files, or perform implementation work.

</HARD-GATE>

## 1. Reach shared understanding

Interview the user relentlessly about the requested implementation until reaching a shared understanding.

Resolve decisions one at a time. Ask only one question at a time and wait for the user's answer before continuing.

Research discoverable facts from the repository, documentation, or available tools instead of asking the user.

Implementation decisions and trade-offs belong to the user.

For every question:

1. State why the decision matters.
2. Provide your recommended answer.
3. Ask the user to confirm, reject, or refine it.

Follow dependencies between decisions. Revisit earlier answers when new information creates a conflict.

Keep this checklist active internally. Do not print it unless requested.

### Implementation grilling coverage

#### Behavior

- [ ] Define the behavior being implemented.
- [ ] Define inputs, outputs, and observable results.
- [ ] Identify important edge cases and invariants.

#### Scope

- [ ] Define what is included.
- [ ] Define explicit non-goals.
- [ ] Define affected components and boundaries.
- [ ] Identify external systems and dependencies.

#### Structure

- [ ] Assign responsibilities to components or modules.
- [ ] Define interfaces and contracts.
- [ ] Define control flow and data flow.
- [ ] Define ownership of state and business rules.

#### Data

- [ ] Define data models and persistence changes.
- [ ] Define consistency and transaction boundaries.
- [ ] Define validation and compatibility requirements.
- [ ] Define migration or backfill requirements.

#### Failure handling

- [ ] Define expected failure modes.
- [ ] Define error handling and error propagation.
- [ ] Define retry, timeout, cancellation, and idempotency behavior.
- [ ] Define degraded behavior and recovery.

#### Security

- [ ] Define authorization and trust boundaries.
- [ ] Define input validation and sensitive-data handling.
- [ ] Identify applicable security or compliance constraints.

#### Operations

- [ ] Define configuration and feature-flag requirements.
- [ ] Define logging, metrics, tracing, and alerts.
- [ ] Define deployment, rollout, migration, and rollback behavior.
- [ ] Identify operational and maintenance risks.

#### Verification

- [ ] Define unit, integration, contract, and end-to-end testing needs.
- [ ] Define acceptance conditions.
- [ ] Identify assumptions or unknowns requiring validation.

Do not force irrelevant checklist items. Cover only decisions that materially affect the implementation.

Stop grilling when:

- all implementation-impacting choices are resolved;
- no blocking unknown remains;
- the implementation boundaries and expected behavior are clear.

## 2. Print proposed implementation decisions

Print only the implementation decisions. Do not print a separate decision brief, interview summary, or approach comparison.

Use one numbered item per independent decision.

```markdown
## Implementation Decisions

1. **Decision:** ...
   - **Implementation:** ...
   - **Alternatives considered:** ... <!-- optional -->
   - **Trade-offs:** ...
   - **Risks / unknowns:** ... <!-- optional -->
```

### Field rules

- **Decision:** State the selected implementation choice in one sentence.
- **Implementation:** Describe how the choice should be applied, without writing code.
- **Alternatives considered:** Briefly describe rejected alternatives in one to three sentences. Omit when no meaningful alternative was considered.
- **Trade-offs:** State what is gained and what is sacrificed.
- **Risks / unknowns:** Include unresolved assumptions, operational risks, or required validation. Omit when empty.

Keep decisions concrete enough to guide implementation.

Avoid:

- broad architectural principles without implementation consequences;
- requirements already established by the user;
- minor coding details that can safely be left to the implementer;
- duplicate or overlapping decisions.

## 3. Request approval

Ask the user to approve, reject, or refine each proposed decision.

When there are multiple decisions, allow them to be reviewed independently.

Do not proceed to implementation.

## 4. Print approved implementation decisions

After approval, print the same compact list containing only approved decisions.

Incorporate all accepted refinements.

Exclude rejected, superseded, or unresolved decisions.

Preserve:

- the selected implementation choice;
- the implementation direction;
- accepted trade-offs;
- brief alternatives when useful;
- unresolved risks that do not block approval.

Keep the final record concise.

Do not implement the approved decisions.
