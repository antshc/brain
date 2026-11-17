---
name: write
description: >-
  Write or edit plain prose for guides, how-tos, GitHub text, reports and messages; sharpen or rephrase prompts. Use for 'unslop this', 'tighten this prose', 'sharpen this prompt', 'rephrase my ask'. Not for work items → `write-work`. Not for specs → `write-document`. Not for skills → `skill-author`.
---

# Write

Router. Select one route, read each listed reference fully (no previews), then run Pipeline unless the route supplies its own output. Load nothing the route does not list. Resolve paths from this skill's base directory.

## Top rules

- **Cut words that add no information.**
- **Prefer everyday words.** Use a longer word when it is more precise.
- **When a rule makes a sentence worse, fix the sentence another way or leave it alone.** A sentence that follows every rule and sounds machine-written has failed.
- **The codebase is the word list.** Write the real symbol, file, flag, or command name, not a synonym or a description.
- **Describe the operation in plain language.** Define named patterns on first use.
- **Protected text.** Keep code, commands, citations, identifiers, quotations, captured output, and caller-required structure, subjects, and markers exactly as supplied.

## Routing

| Route | Text kind | Read, in order | Output |
|---|---|---|---|
| `guide` | README, RFC, guide, explanation, spec or HLD prose | [modes-diataxis.md](references/modes-diataxis.md) (whole documents only), [sentences-google.md](references/sentences-google.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [rhythm.md](references/rhythm.md), [unslop.md](references/unslop.md) | Pipeline |
| `how-to` | Instructions, procedures, runbooks, reproduction steps | [sentences-google.md](references/sentences-google.md), [steps-ste.md](references/steps-ste.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [unslop.md](references/unslop.md) | Pipeline |
| `github` | PR title and body, commit message body, review finding or reply | [github-text.md](references/github-text.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [unslop.md](references/unslop.md) | Pipeline; caller format wins |
| `report` | Review, blast-radius, investigation, or status report | [ambiguity-global-english.md](references/ambiguity-global-english.md), [rhythm.md](references/rhythm.md), [unslop.md](references/unslop.md) | Pipeline; keep findings, proof status, and risk judgments |
| `message` | Chat, Slack, Teams, email, Jira or issue comment | [messages.md](references/messages.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [unslop.md](references/unslop.md) | Pipeline |
| `unslop` | Any text; remove AI tells only | [unslop.md](references/unslop.md) | Pipeline |
| `sharpen` | Task prompt to deepen | [sharpen.md](references/sharpen.md) | The four answers, then the rewritten prompt |
| `rephrase` | Task prompt to restate in your own words | [rephrase.md](references/rephrase.md) | The restated goals and problem |

## Auto-selection

Pick the first rule that matches:

1. **Explicit route.** The user or caller names a valid route (`/write sharpen`) → use it. Unknown route → report it and list the routes.
2. **Active route.** A reply to an active `sharpen` or `rephrase` output → continue that route.
3. **Prompt work.** Ask to deepen, sharpen, or rewrite a prompt → `sharpen`. Ask to restate, rephrase, or say in your own words → `rephrase`. Both → `rephrase`, then `sharpen`.
4. **Unslop only.** Ask to unslop or remove AI tells with no other ask → `unslop`.
5. **Redirect.** Text kind in Redirects → invoke that skill. If that skill is the caller, refine its prose with `guide`, or `how-to` for steps, and preserve its template.
6. **Text kind.** Match the text kind from the input and the caller's task to the Routing table.
7. **Unclear kind** → `unslop`. State the assumed kind in the hand-back.

## Redirects

| Text kind | Action |
|---|---|
| Story, task, or bug requirements | *Load and follow the `write-work` skill to write or normalize the user story, implementation task, or bug report; select the applicable route.* Use operation `normalize` for existing text. |
| Spec, HLD, TOI, or untyped requirements | *Load and follow the `write-document` skill to write or normalize the specification, high-level design, or TOI document; select the applicable route.* Use operation `normalize` for an untyped fragment. |
| Bottom line or research report | *Load and follow the `write-document` skill to write the research report or bottom line; select the applicable route.* Use `bottom-line` for a standalone conclusion or `research` for a full report. |
| Structure a standalone documentation page or choose its template/sections | *Load and follow the `write-document` skill to structure the Markdown documentation page, using route `documentation`.* Preserve the supplied purpose, audience and facts. |
| ADR, Concept, or glossary term | *Load and follow the `architecture-records` skill to record the architecture decision, Concept, or term; select the applicable route.* |
| `SKILL.md`, agent, or instructions file | *Load and follow the `skill-author` skill to apply authoring rules to the agent-facing document, using route `guidance`.* |
| Product UI strings | Report that the product's copy guidelines own them. |

This skill owns prose refinement only. Preserve the owner's structure, evidence, and confidence.

Direct prose requests still use `guide` or `how-to`, including writing new prose. Delegate requests for document structure, templates or sections to `write-document documentation`. When `write-document` calls back for prose, honor its selected writing route and refine only; never redirect back. `guide` handles page prose and whole-document mode rules; `how-to` handles procedural blocks, including troubleshooting actions.

## Pipeline

1. **Write or edit.** No text supplied → write it with the route's references. Text supplied → edit it with the same references. *Done when* every listed reference has been applied.
2. **Unslop last.** Apply `unslop.md` last. Preserve meaning, tone, confidence, and protected text. *Done when* a read against the input shows no change to facts, scope, or confidence.
3. **Hand back.** Return the text. For an edit, list each fix with the heading of the reference rule it applies. Nothing to fix → return "No changes."
