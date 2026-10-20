---
name: to-spec
description: "Synthesises the current conversation into a feature spec with user stories, implementation decisions, and testing seams, then publishes it as a GitHub issue through gh."
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview the user about requirements; synthesize what you already know. Confirm testing seams and explicitly collect all three publication-routing inputs below.

**MUST** load the bundled [GitHub reference](./github.md) before any GitHub action, including reads. Execute GitHub actions through `gh` according to its prerequisites, procedures, and failure handling. If the reference cannot be loaded, stop and report the blocker. No setup-generated tracker configuration is required.

**Required inputs:** Ask the user for each value, one question at a time; confirm any already supplied value. Wait for valid explicit answers before GitHub actions; never infer or default routing from the checkout, remotes, issue URLs, or default branch.

- `TRACKER_REPOSITORY`: GitHub repository for the spec and tickets, in `OWNER/REPO` format.
- `repo:target`: development/PR repository, in `OWNER/REPO` format; record as `SOURCE_REPOSITORY`.
- `repo:base`: target base branch in that source repository; record as `BASE_BRANCH`.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Read root `GLOSSARY.md` when present and use its vocabulary throughout the spec; proceed normally when absent.

2. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

3. Write the spec using the template below. Validate the three user-confirmed routing inputs using the GitHub reference. Publish it as a GitHub issue with the `spec`, `repo:target:<owner/repo>`, and `repo:base:<branch>` labels, creating missing labels first. Read the published issue back to confirm the full body and all three labels, then report its URL.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>

## Completion criteria

- The spec reflects the conversation and codebase, with testing seams confirmed by the user.
- A GitHub issue in the user-supplied `TRACKER_REPOSITORY` contains the complete spec and the `spec` label plus the confirmed `repo:target:<owner/repo>` and `repo:base:<branch>` labels; its URL is reported.
