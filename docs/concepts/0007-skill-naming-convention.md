# Skill Naming Convention

## Purpose

A skill's `name` is how it gets referenced in documentation, in conversation, and in search across a growing collection. A vague, generic, or inconsistently patterned name (`helper`, `utils`, `tools`) forces readers to open the skill to learn what it does, and makes the collection harder to search and organize as it grows.

## Design Guidance

- The `name` field must use lowercase letters, numbers, and hyphens only.
- Prefer **gerund form** (verb + `-ing`) — it names the activity/capability at a glance: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`, `testing-code`, `writing-documentation`.
- Acceptable alternatives when gerund form reads awkwardly:
  - Noun phrases: `pdf-processing`, `spreadsheet-analysis`.
  - Action-oriented (imperative verb + object): `process-pdfs`, `analyze-spreadsheets`.
- Avoid:
  - Vague names: `helper`, `utils`, `tools`.
  - Overly generic names: `documents`, `data`, `files`.
  - Reserved/vendor words: `anthropic-helper`, `claude-tools`.
  - Mixing patterns within the same skill collection — pick one convention (gerund, noun phrase, or action-oriented) and apply it consistently across all skills in the collection.

## Examples

- Good: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`.
- Acceptable: `pdf-processing`, `process-pdfs`.
- Avoid: `helper`, `utils`, `tools`, `documents`, `data`, `files`, `anthropic-helper`, `claude-tools`.
