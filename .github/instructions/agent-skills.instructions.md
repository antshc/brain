---
description: How to write a skill, agent, or convention file in this repo — frontmatter, invocation, disclosure, and pruning.
applyTo: "**/skills/**/*.md,**/agents/*.agent.md,.crew/*.md,.github/copilot-instructions.md"
---

# Writing agent-facing documents

Applies to every document whose reader is an agent: a `SKILL.md`, a bundled `references/` or `*-FORMAT.md`
file, an `*.agent.md`, and the `.crew/` convention files.

This file is **write-time** guidance — how to word the file in front of you. **Design-time** questions (which
building block to reach for, how skills compose) are answered by the Crosscutting Concepts indexed in
[ARCHITECTURE.md](../../ARCHITECTURE.md).

## Style

**Writing style:** be terse, concise, no fillers.

**Section references:** name a section by its title only — drop the `#` heading markers. Write `Building blocks`, not `## Building blocks`.

**Skill invocation:** every step that runs another skill reads ``Run `/{{skillName}}` skill `` or ``Follow `/{{skillName}}` skill `` — backticked, slash-prefixed skill name, verb is *run* or *follow*, never "call" or "invoke". Target a named section as ``Run `/index-docs`' skill **Sync index row** `` or ``Follow `/crew-gotchas`' skill **Read Workflow** ``. Naming a skill as an owner rather than running it takes the plain backticked name.

**Line wrapping:** one physical line per paragraph/bullet/table cell, however long — no fixed-column hard-wrap, keeps grep and diffs clean. Rejoin any line an editor's auto-rewrap splits.

**Syntax legend** — use when writing or updating skills, templates, and agent instruction files:

| Syntax | Meaning | Example |
|---|---|---|
| **bold**|Emphasis in prose, labels, warnings, required rules|**Required:** Run tests before commit.|
| `camelCase` | Conceptual value resolved and maintained by the agent | Resolve `camelCase` from Git; reference it as `$camelCase`. |
| `camelCase := instruction` | Runtime assignment evaluated by the agent | `NAME := generate a unique kebab-case name` |
| `{{camelCase}}` | Placeholder in input, a markdown template, in prose, an inline template, replaced with a resolved runtime value | `{{input}}`, `Your name {{userName}}`, `reports/{{camelCase}}.md` |
| `{{camelCase\|(hint|inline one-liner instruction applicable to camelCase)}}` | Bracketed placeholder with an inline default/hint, pipe-delimited, when the hint is short | `{{priority\| One of (MVP|Should have) }}`, `summary| one-liner` |
| `<!-- ... -->` | Hidden template instruction not rendered in Markdown preview | `<!-- Remove this comment after population. -->` |
| `[optional]` | Optional input or argument | `[target-path]` |
| `value1 \| value2` | Allowed values | `completed \| failed \| blocked` |
| `` `literal` `` | Fixed command, path, identifier, or value | Run `dotnet test`. |
| `$VARIABLE` | Shell environment variable | `cd "$REPOSITORY_ROOT"` |
| `${VARIABLE}` | Braced shell environment variable | `${REPOSITORY_ROOT}/src` |

## Frontmatter

| Key | Required | Value |
|-----|----------|-------|
| `name` | yes | Lowercase, hyphens, matches the folder name. |
| `description` | yes | Third person. States what it does **and** the triggers for reaching it. |
| `disable-model-invocation` | no | `true` makes the skill user-invoked. |

Name skills by their **verb-prefix family**, not the gerund form other guides recommend:
`to-*` (produces an artifact), `record-*` (writes one record), `setup-*` / `init-*` (one-time scaffolding),
`fetch-*` (reads an external resource), `manage-*` (owns a backend), `crew-*` (shared by the crew agents).
A new skill joins an existing family unless it genuinely starts one.

Register every new plugin in [marketplace.json](../plugin/marketplace.json) in the same change.

## Invocation

The `description` is the skill's always-loaded pointer: it costs tokens on every turn whether or not it fires.

- **Model-invoked** (omit `disable-model-invocation`) — the agent can fire it, and other skills can reach it.
  Choose this only when the agent must reach it on its own, or another skill must.
- **User-invoked** (`disable-model-invocation: true`) — only a human typing its name reaches it. Costs no
  context, but you become the index that has to remember it exists.

Write the description in third person, front-loading the word you actually type when you want the skill. One
trigger per distinct case; synonyms that rename the same case are one case written twice — collapse them. Cut
identity the body already carries.

## What goes in the file

A document is **steps** (ordered actions) and **reference** (rules and facts consulted on demand). They mix
freely — all steps, all reference, or both. Rank each piece by how immediately the agent needs it:

1. In-file steps — what the agent does, in order.
2. In-file reference — consulted on demand.
3. Disclosed reference — a sibling file reached by a pointer, loaded only when the pointer fires.

Keep `SKILL.md` under 500 lines; move material out well before that. Disclose what only some runs need and
inline what every run needs. When a skill has steps, in-file reference that should be disclosed buries them.

Bundle resources by how the agent uses them:

| Folder | Holds |
|--------|-------|
| `scripts/` | executable automation the agent runs |
| `references/` | documentation the agent reads to decide |
| `assets/` | files used unchanged in the output |
| `templates/` | scaffolds the agent fills in and modifies |

One or two files in a category live directly in the skill folder; more than that earns a subfolder.

Write commands in Python rather than bash- or PowerShell-only syntax, so they run unmodified on every OS
 Use  `python` is not available here.

## Steps and completion criteria

Every step ends on a condition that tells the agent it is done. Make it checkable — can the agent tell done
from not-done? — and, where it matters, exhaustive: "every modified record accounted for" drives real work
where "produce a list" does not.

Reserve numbered steps for procedures where the sequence genuinely matters. For open-ended work (debugging,
review, refactoring) give decision criteria instead, so the agent can adapt.

## Wording

Reach for a **leading word** — a compact concept the model already holds (*ledger*, *sweep*, *drift*,
*tracer bullet*) — and repeat the token, never the sentence. It anchors the same behaviour every time it
appears and costs one word.

**Prompt the positive.** Steering by prohibition drags the banned behaviour into context and makes it more
available: *don't think of an elephant*. State the target instead — "write one-line comments" rather than
"never write verbose comments". Keep a prohibition only as a hard guardrail you cannot phrase positively, and
pair it with the positive target.

Write a `## Gotchas` section whenever the skill touches an external tool, API, or platform quirk. Bold the
constraint, then say why. Treat it as living: every time the agent gets something wrong, add a line. This is
distinct from `## Troubleshooting`, which fixes things after they break.

## Pruning

- **One meaning, one place.** The same rule in two files costs maintenance, costs tokens, and inflates the
  rule's apparent rank. Shared procedure belongs to one skill that the others invoke.
- **The environment is a source of truth too.** A document restating `pyproject.toml`, a folder layout, or
  `--help` output is a cache of a lookup, and earns its load only when the lookup is expensive. Write down what
  the agent cannot find by looking: the unwritten convention, the reason behind a choice, the gotcha no config
  confesses.
- **Cut no-ops.** A line the model already obeys by default pays load to say nothing. Test each sentence: does
  it change behaviour versus the default? When one fails, delete the whole sentence rather than trim it. The
  same test grades a leading word — *be thorough* is a no-op when the agent is already thorough-ish.
- **Check relevance.** A line goes stale as the behaviour it describes changes. Without a pruning pass, stale
  layers settle because adding feels safe and removing feels risky.

## Before finishing

- Frontmatter has `name` and `description`; the description carries triggers, not just identity.
- Every line teaches something the agent would otherwise get wrong — nothing restates common knowledge.
- Body under 500 lines; bulky or occasional material disclosed to `references/`.
- Shared procedure is invoked, not duplicated.
- No credentials, tokens, or secrets in any file.
