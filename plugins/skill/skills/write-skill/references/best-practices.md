# Skill best practices

Structure and content rules for agent-facing documents: `SKILL.md`, bundled references and templates, `*.agent.md`, instructions files. Wording rules live in [wording.md](wording.md). Repository-local rules (e.g. `.github/instructions/*.instructions.md`) override this file on conflict.

**Root virtue: predictability.** The agent takes the same _process_ every run, not the same output. Every rule below serves it.

**Guiding principle:** constrain what must remain true, prescribe how only when necessary, explain why when non-obvious, define what happens when execution cannot proceed.

## Frontmatter and description

| Key | Required | Rule |
|---|---|---|
| `name` | yes | Lowercase, hyphenated, matches folder name. Name by existing verb-prefix family; start a new family only when needed. |
| `description` | yes | Third person; target 100–300 chars; state **when → responsibility → result**; include 3–6 distinctive trigger keywords. |
| `disable-model-invocation` | no | `true` = human-only; omit when model or other skills must discover it. |

**Description characters:** plain text, max 1024 chars. Separate clauses with `.`, `;`, or `,`. **MUST NOT** use:

| Character | Why |
|---|---|
| `—` `–` (em/en dash), ` - ` / `--` as punctuation | Breaks naive parsers; hyphens inside identifiers (`publish-page`) allowed |
| `<` `>` | Rejected by skill validators (XML/HTML injection guard) |
| `: ` (colon + space) | YAML reads it as a nested mapping key |
| ` #` (space + hash) | YAML starts a comment; rest of description dropped |
| Leading `-` `?` `:` `[` `]` `{` `}` `,` `&` `*` `!` `\|` `>` `'` `"` `%` `@` `` ` `` | YAML indicator; plain scalar cannot start with it |
| Tabs, line breaks in a plain scalar, leading/trailing whitespace | Multiline/indent parse errors |

**YAML safety:** frontmatter MUST parse as YAML; a plain scalar containing `: ` or ` #` breaks parsing and the skill silently disappears. Write `description` (and any value with `: `, quotes, backticks, `#`, or a leading `[`, `{`, `*`, `&`, `!`, `%`, `@`) as a folded block scalar: `description: >-` then the text indented two spaces on the next line. Never use `: ` inside a plain scalar.

**Description as context pointer.** A description is a **context pointer**: always-loaded text naming out-of-context material plus the condition for reaching it. Its _wording_, not its target, decides when and how reliably the agent reaches the skill. It does two jobs: state what the skill is, list the **branches** that trigger it. Every word costs on every turn, so prune it harder than the body:

- Front-load the skill's **leading word**.
- One trigger per branch. Synonyms renaming one branch are duplication; collapse them.
- Cut identity the body already carries. Keep triggers plus any "when another skill needs…" reach clause.
- Use the words users actually type, and the same words used in prompts, docs, and code.

## Invocation choice

Two loads, each spent by every document and pointer:

- **Context load** — always-loaded material (descriptions, `AGENTS.md` lines) spending tokens and attention every turn.
- **Cognitive load** — the human as index, remembering which skills exist. Spend it where human judgement matters.

Pick one mode:

- **Model-invoked** (omit `disable-model-invocation`): agent and other skills can reach it; costs context load. Choose when the agent must reach it unprompted or another skill must invoke it.
- **User-invoked** (`disable-model-invocation: true`): only a human typing its name reaches it; no other skill can. Zero context load; description becomes a human-facing one-line summary, trigger lists stripped.
- When user-invoked skills multiply past memory, add one **router skill** naming the others and when to reach each.

## Skill invocation syntax

Reference the exact plain `skill-name` without leading `/`, immediately followed by the word `skill` (e.g. `` `fetch-page` skill ``). Verb may vary (run, follow, use, load).

Every skill invocation **MUST** include 3–6 distinctive keywords from the invoked skill's description. Do not copy the full description.

Wrap the whole invocation phrase in *italics*. Example: *Run `fetch-page` skill to fetch the Confluence page as Markdown.*

## Information hierarchy

Two content types mix freely: **steps** (ordered actions) and **reference** (definitions, rules, facts consulted on demand). A skill may be all steps, all reference, or both. Place each piece on the ladder by how immediately the agent needs it:

1. **In-file step** — primary tier: what the agent does, in order.
2. **In-file reference** — consulted on demand. A flat peer-set (every rule of a review on one rung) is fine.
3. **Disclosed reference** — separate file reached by a context pointer, loaded only when the pointer fires.

Order content by need: **steps → inline reference → disclosed reference**. Push too little down and the top bloats; push too much and you hide material the agent needs.

- **Progressive disclosure** — move material down the ladder behind a pointer so the top stays legible. Branching test: inline what every branch needs; disclose what only some branches reach. Undisclosed reference buries steps and makes attending to them a coin-flip.
- **Pointer wording decides reach.** A must-have target behind a weak pointer is a variance bug: sharpen wording first; inline only if sharpening fails. Name the condition: "Read `references/aws.md` when targeting AWS", not "Read documentation".
- Load references conditionally; never load every reference unconditionally.
- **Co-location** — keep a concept's definition, rules, and caveats under one heading. The document should read like documentation written for the agent.
- **Sprawl** — too long even when every line is live. Cure: disclose reference, split by branch or sequence.
- Keep `SKILL.md` body under 300 lines; 100–250 is a useful stricter target. Include only sections that materially help execution.

## Steps and completion criteria

Every step ends on a **completion criterion**: the condition that tells the agent the work is done. Use numbered steps only when order matters; otherwise state decision criteria.

- **Clarity** — can the agent tell done from not-done? A vague bound ("understanding reached") invites **premature completion**: ending a step early because attention slips to _being done_, pulled by visible **post-completion steps**.
- **Demand** — how much it requires. "Every modified model accounted for" forces **legwork** where "produce a change list" does not. Demand also binds flat reference ("every rule applied").
- Strongest criteria are both checkable and exhaustive.
- Defend premature completion in order: sharpen the bound first; only if irreducibly fuzzy _and_ the rush is observed, split the sequence. Hiding later steps works only across a real context boundary (hand-off or subagent); an inline call clears nothing.

**`## Completion criteria` section** — add when the result is not self-evident. List observable, checkable conditions on the produced result (files, output, state), not effort. Without them the agent stops at "steps ran" and claims success on a wrong or empty result.

- Name it **Completion criteria**; not `Verification`, `Validation`, `Testing`, or `Acceptance criteria`.
- State the result to observe, not how to run tests. A skill's own test suite is repository tooling: **MUST NOT** appear in a skill (no test commands, test paths, test-only dependencies).
- Omit when step completion conditions already prove the result. Do not repeat the same checks in workflow, output, and completion sections.

**Completeness sweep** — checks whether required scope was omitted (completion criteria check the result meets its contract).

- Add for multi-part work with independently missable obligations: features, cross-file refactors, migrations, broad research.
- When used, it **MUST** run last. Re-read the request, reconstruct explicit and implied obligations, map each to evidence across code, tests, docs, configuration, failure/compatibility paths.
- Resolve uncovered obligations by implementing, asking, or reporting explicit deferral. **MUST NOT** declare completion with an unaccounted obligation.
- Omit for small bounded work already proven by checks. **MUST NOT** duplicate checks across sweep and completion criteria.

## Output contract

Define what the agent must produce: artifacts, format, ordering, location. Include explicit outcomes for the edge cases:

- **No result** — e.g. return "No findings." after a complete pass; do not pad with suggestions.
- **Incomplete** — e.g. report "Review incomplete" plus missing evidence; never guess.
- **Unverified** — mark assumptions and unverified candidates separately from verified results.

## When to split

Give each skill one purpose nameable in one phrase. Each cut spends a load, so split only when it earns it:

- **By invocation** — split off a model-invoked skill when a distinct leading word should trigger it alone, or another skill must reach it.
- **By sequence** — split a run of steps when post-completion steps tempt the agent to rush the current one. Merging sequences has the reverse effect.
- **Compose by invoking the owner.** Behaviour needed by one skill stays inline; behaviour needed by several gets one owning skill that others invoke. Never restate another skill's procedure.

## Instruction precision

Make behavior predictable without restricting valid implementation choices.

**Constraint → mechanism → rationale → failure behavior** — use for critical requirements:

- **Constraint:** what MUST or MUST NOT happen.
- **Mechanism:** how the agent executes it.
- **Rationale:** why it matters (only when non-obvious).
- **Failure behavior:** what happens when blocked.

> MUST delegate codebase exploration to a subagent. The subagent returns relevant file paths and evidence. MUST NOT substitute direct exploration, even if faster. Rationale: preserve parent context. If delegation is unavailable, report the blocker rather than silently substituting another mechanism.

A rationale helps interpretation but does not guarantee compliance; verify critical constraints through observable actions or external checks. Prohibit plausible substitutions explicitly when an agent might silently swap mechanisms.

**Degrees of freedom** — match prescription to task risk:

| Task | Agent freedom | Instruction style |
|---|---|---|
| Exploration | High | Define objective and evidence |
| Design | High–Medium | Define constraints and decision criteria |
| Implementation | Medium | Preserve contracts and conventions |
| Testing | Medium–Low | Define required checks and results |
| Migration | Low | Specify ordering, mechanism, recovery |
| Destructive operations | Very low | Require authorization and explicit safeguards |

Constrain what must remain true; prescribe how only when necessary. Example: "MUST preserve public API behavior. Choose internal implementation details independently."

**Failure policies** — pick one per critical step:

- **Fail closed** — mechanism mandatory: stop, report blocker, MUST NOT replace it (e.g. no direct SQL when the migration tool is unavailable).
- **Controlled fallback** — alternatives permitted: name them ("Search with `rg`. If unavailable, use `grep -R`.").
- **Graceful degradation** — partial work valuable: complete independent parts, report what did not run, MUST NOT claim full success.

## Gotchas

When a skill depends on an external tool, API, or platform quirk, add `## Gotchas`. State the constraint first; add why only when it changes handling. Record only knowledge the agent cannot find by looking.

## Subagents

Run subagents through prose instructions describing task, scope, inputs, constraints, and expected output. Do not instruct agents to call `runSubagent` directly. Pass context pointers (paths, IDs) rather than duplicated content; pass absolute paths to bundled files.

## Resources

| Folder | Holds |
|---|---|
| `scripts/` | executable automation |
| `references/` | decision/reference material |
| `assets/` | files used unchanged |
| `templates/` | scaffolds to fill or modify |

- Keep up to two category files at skill root; otherwise use the matching resource folder. Name linked files for what they hold.
- **Bundled paths** resolve from the skill base directory, never caller CWD. Example: **Run `./scripts/run.py` from this skill's base directory**.
- **Skill-local resources:** each skill **MUST** bundle required resource files inside its own folder; **MUST NOT** read, link, or execute resource files from another skill's folder. Copy required resources in. Invoking another skill remains allowed.
- Use scripts for repetitive or fragile operations. Prefer Python over shell-specific scripts; use the repository-supported Python command.
- New plugin → register it in the repository's plugin marketplace/manifest in the same change.

## Template ownership

- **Template owns rendering; skill owns orchestration.** Template: structure, format, conditions, local constraints. `SKILL.md`: selection, workflow, inputs/outputs, shared rules.
- `{{value|hint}}` — preferred field-local guidance.
- `<!-- @: instruction -->` — hidden structural/rendering directive; **MUST** be one terse line.
- Templates MAY define local **Rules** and **Gotchas**. Move only shared guidance to `SKILL.md` or `references/`.

## Syntax legend

| Syntax | Meaning | Example |
|---|---|---|
| **bold** | Required rule, label, warning | **Required:** Run tests. |
| *italic* | Skill invocation phrase | *Run `fetch-page` skill to fetch the Confluence page as Markdown.* |
| `@camelCase` | Agent-resolved conceptual value | Use `@currentBranch` as target. |
| `set @camelCase to instruction` | Runtime assignment | `set @currentBranch to current Git branch` |
| `{{camelCase}}` | Replaced placeholder | `reports/{{camelCase}}.md` |
| `{{camelCase\|hint}}` | Preferred field-local guidance | `{{priority\|MVP or Should have}}` |
| `<!-- @: instruction -->` | Hidden structural/rendering directive; one terse line | `<!-- @: repeat per component -->` |
| `[optional]` | Optional input | `[target-path]` |
| `value1 \| value2` | Allowed values | `completed \| failed` |
| ``literal`` | Fixed command/path/value | `dotnet test` |
| `$snake_case` | Local Bash variable (shell only) | `$repo_root` |
| `$UPPER_SNAKE_CASE` | Bash environment variable (shell only) | `$REPOSITORY_ROOT` |
| `${UPPER_SNAKE_CASE}` | Braced Bash variable expansion (shell only) | `${REPOSITORY_ROOT}/src` |

## Pruning

- **Single source of truth** — one meaning, one place within a skill; a behaviour change is a one-place edit. **Duplication** costs maintenance and tokens and inflates a meaning's prominence. Duplicate across skills only to keep resources skill-local.
- **Environment is a source of truth** — `package.json` scripts, config, directory layout, `--help` output. Restating it is a **cache**; cache only what the agent cannot find by looking (unwritten conventions, reasons, gotchas).
- **Relevance** — every line bears on what the skill does. Lines lose relevance by never bearing on the task or by going stale. Without pruning the default fate is **sediment**.
- **No-ops** — apply the No-op test in [wording.md](wording.md).

## Evaluation

Treat authoring as iterative: run representative tasks without the skill, identify the failing behavior, write the smallest instruction that fixes it, rerun, compare. Judge actual traces and artifacts, not wording alone. Dimensions: trigger accuracy (positive, negative, near-miss prompts), execution correctness, constraint compliance (include prompts tempting a bypass), recovery, regression, efficiency.

## Before finishing

- Valid frontmatter; trigger-rich description free of forbidden description characters.
- `SKILL.md` body under 300 lines.
- No duplicate procedures within a skill; bundled resource paths stay inside the skill folder and resolve.
- No test commands or test-only dependencies; result checks live under `## Completion criteria`.
- Every critical step has a failure policy; every step has a checkable completion condition.
- No credentials, tokens, or secrets.

Sources: repository `agent-skills.instructions.md`; [mattpocock/skills](https://github.com/mattpocock/skills) `writing-for-agents` and `writing-great-skills` (v1.1.0) GLOSSARY; Agent Skills best practices KB and AI diff review agent KB (October 2026), drawing on the [Agent Skills specification](https://agentskills.io/specification), [Anthropic skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), and OpenAI/Anthropic skill-creator guidance.
