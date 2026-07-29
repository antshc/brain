# CODE

<!-- Read in full by droid-implement during IMPLEMENTATION. Describe this repo's own conventions — never invent or copy example values from another repo. -->

This repo's "code" is skills, agent instructions, and templates. The droid authors and edits them.

## Style

**Writing style:** be terse, concise, no fillers.

**Section references:** name a section by its title only — drop the `#` heading markers. Write `Building blocks`, not `## Building blocks`.

**Skill invocation:** every step that runs another skill reads ``Run `/{{skillName}}` `` — slash-prefixed, backticked, verb always *run*, never "call" or "invoke". Target a named section as ``Run `/index-docs`' **Sync index row** ``. Naming a skill as an owner rather than running it takes the plain backticked name.

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

## Layer placement

- Plugin skills: `plugins/<plugin>/skills/<skill>/SKILL.md`.
- Plugin agents: `plugins/<plugin>/agents/<name>.agent.md`.
- Standalone (non-plugin) skills: `skills/<skill>/SKILL.md`.
- Repo-wide agent instructions: `.github/copilot-instructions.md`.
- Shared writing/syntax conventions: this file, `.droid/CODE.md`.

## Design principles

- One skill/agent = one responsibility — don't merge concerns.
- Reference this file's syntax legend instead of duplicating it inside individual skills.
- Keep skill/instruction/template files terse — no filler prose.

## Tests

N/A — no automated tests for markdown files.