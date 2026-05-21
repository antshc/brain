---
name: to-prd
description: Create a PRD through user interview, codebase exploration, and module design, then submit as a GitHub issue. Use when user wants to write a PRD, create a product requirements document, or plan a new feature.
argument-hint: '<target-branch> <jira-ticket> <feature description>'
---

This skill will be invoked when the user wants to create a PRD. You may skip steps if you don't consider them necessary.

The skill accepts positional arguments: `<target-branch> <jira-ticket> <feature description>`. If provided, skip the questions in step 1.

1. **Before anything else**, establish the release context:
   - **Target branch**: Which release branch should this work be based on? (e.g. `release/1.1.10`)
   - **Jira ticket**: What is the Jira ticket number for this work? (e.g. `PROJ-1234`)

   If these were provided as positional arguments, use those values and confirm with the user. Otherwise, ask explicitly before proceeding.

2. Ask the user for a long, detailed description of the problem they want to solve and any potential ideas for solutions.

3. Explore the repo to verify their assertions and understand the current state of the codebase.

4. Interview the user relentlessly about every aspect of this plan until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

5. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

6. Once you have a complete understanding of the problem and solution, use the template below to write the PRD. The PRD should be submitted as a GitHub issue with the `prd` label.

<prd-template>

**Target Branch:** `<target-branch>`
**Jira Ticket:** `<jira-ticket>`

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## Behavior Rules

**Writing style for behavior rules**
- No implementation details: rules describe observable external behavior, not internal details or class structure.
- Plain words only: no backticks, code formatting, or type names; refer to types and methods by descriptive role (e.g., "the break duration", "a circuit-open error", "the pipeline execute").
- Single-responsibility: each rule covers exactly one scenario or transition; do not combine two independent behaviors in one bullet.
- Rule format: use one of the three formats below; one cause-effect pair per rule.

A LONG, numbered list of Behavior Rules. Each behavior rule should be in one of the formats:

1. <triggering condition> → <resulting behavior>
2. The system MUST/SHOULD <behavior> when <condition>
3. <subject> <behavior>

<behavior-rule-example>
1. Customer opens the accounts screen → the current balance is displayed for each account
2. The system must display the current balance for each account when the customer opens the accounts screen
3. The accounts screen shows the current balance for each account
</behavior-rule-example>

This list of behavior rules should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions
- New configuration options, changes to existing configuration options

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this PRD.

## Further Notes

Any further notes about the feature.

</prd-template>
