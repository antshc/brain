## Writing Style

- **Compressed**: compress wording, not meaning.
- **High-density**: every sentence carries unique information — if a word can be removed without losing meaning, remove it.
- No filler, explanations, marketing wording, repetition, or generic statements.
- Keep sections short and direct.

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
- Use short technical statements and implementation-oriented language.
- No specific file paths or code snippets (they become outdated quickly).

### Testing Decisions section
- Describe what makes a good test (only test external behavior, not implementation details).
- List which modules will be tested and prior art for the tests.

## Template

```markdown
**Target Branch:** `<target-branch>`
**Jira Ticket:** `<jira-ticket>`

## Problem Statement

The problem from the user's perspective. No technical language.

## Solution

The solution from the user's perspective. No technical language.

## Behavior Rules

A numbered list of behavior rules following the formats above.

## Implementation Decisions

A list of implementation decisions: modules to build/modify, interfaces, architectural decisions, schema changes, API contracts, configuration options.

## Testing Decisions

Which modules will be tested, what makes a good test, prior art.

## Out of Scope

What is explicitly out of scope.

## Further Notes

Any additional notes.
```

## Formatting Instructions

When formatting or updating a PRD:

1. Preserve all existing meaning and decisions.
2. Remove bloat: filler words, redundant explanations, verbose phrasing.
3. Ensure every section matches the writing style above.
4. Do not add new content unless the user provides it.
5. Do not remove sections even if empty — keep the heading with a brief note if nothing applies.
