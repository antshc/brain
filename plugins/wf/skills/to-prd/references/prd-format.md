### Problem Statement & Solution sections
- No technical language; understandable to a non-technical stakeholder.

### Behavior Rules section
- No implementation details: rules describe observable external behavior, not internal details or class structure.
- Plain words only: no backticks, code formatting, or type names; refer to types and methods by descriptive role (e.g., "the break duration", "a circuit-open error", "the pipeline execute").
- Single-responsibility: each rule covers exactly one scenario or transition; do not combine two independent behaviors in one bullet.
- Rule format: use one of the three formats below; one cause-effect pair per rule.
  1. `<triggering condition>` → `<resulting behavior>`
  2. The system MUST/SHOULD `<behavior>` when `<condition>`
  3. `<subject>` `<behavior>`
- The list must be extensive and cover all aspects of the feature.

### Implementation Decisions section
- Preserve integration constraints and assumptions required for implementation.
- No specific file paths or code snippets (they become outdated quickly).

### Testing Decisions section
- Describe what makes a good test (only test external behavior, not implementation details).
- List which modules will be tested and prior art for the tests.

## Template

```markdown

{Writing style: concise, no-fluff, Terse}

**Target Branch:** `<target-branch>`
**Jira Ticket:** `<jira-ticket>`

## Problem Statement

The problem from the user's perspective. No technical language.

## Solution

The solution from the user's perspective. No technical language.

## Behavior Rules

A numbered list of behavior rules following the formats above.

## Implementation Decisions

{Writing style: concise, no-fluff, Terse, technical tone.}

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions
- Configuration options that will be added/modified

## Testing Decisions

A list of testing decisions that were made. This can include:

- Which modules will be tested
- What makes a good test
- Prior art for the tests

## Out of Scope

What is explicitly out of scope.

## Further Notes

Any additional notes.
```
