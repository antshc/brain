# Skill best practices

Structure and content rules for agent-facing documents: `SKILL.md`, bundled references and templates, `*.agent.md`, instructions and `.crew/` convention files. Wording rules live in wording.md. Repository-local overrides win on conflict; a repository stub invoking this skill adds no separate rules. In this repository, design-time composition guidance lives in `ARCHITECTURE.md`.

**Predictability:** repeat the process, not the output.

Constrain invariants; prescribe mechanisms only when needed; explain non-obvious reasons; define blocked behavior.

## Contents

- Frontmatter and description
- Invocation choice
- Skill invocation syntax
- Information hierarchy
- Route composition
- Steps and completion criteria
- Output contract
- When to split
- Instruction precision
- Gotchas
- Subagents
- Resources
- Template ownership
- Syntax legend
- Pruning
- Evaluation
- Before finishing

## Frontmatter and description

| Key | Required | Rule |
|---|---|---|
| `name` | yes | Lowercase, hyphenated, matches folder name. Name by existing verb-prefix family; start a new family only when needed. |
| `description` | yes | See Description shape. |
| `disable-model-invocation` | no | `true` = human-only; omit when model or other skills must discover it. |

**Description shape:** **what → when → [redirect]**, 60–300 chars.

1. **What:** one sentence, imperative verb first, naming the concrete result (`Publish …`, `Return one report`).
2. **When:** `Use when …` or `Use for /name, 'phrase', …` with 2–5 triggers in words users type; quoted phrases beat abstract keywords.
3. **Redirect** (optional): point to the nearest sibling (``Use `why` for motivation.``) or `Skip when …`.

Omit process detail (`using bundled best practices`, `from a brief`) unless it sets the skill apart. User-invoked skills: the What sentence only.

**Overlap rules:**

- Put the strongest trigger phrases first; listings may truncate long descriptions.
- Every quoted trigger phrase is unique across all skills; near-duplicates (`'how does this work'` vs `'how does this code work'`) count as duplicates.
- Where skills overlap, end with ``Not for X → `skill`.``, one `→ skill` redirect per neighbor, each naming an existing skill other than itself.
- Assign one role per skill; name the owner of each neighboring role in `Not for`.

Repository CI uses `.github/scripts/lint_skill_descriptions.py` over `plugins/wf/` to check length, duplicate/near-duplicate quoted triggers, and unresolved `Not for` targets.

| Invocation | Example |
|---|---|
| Model-invoked | `Investigate a question against primary sources and save cited findings as Markdown. Use for /research, 'research X', 'gather docs on Y', or delegating reading legwork. Use why for design rationale.` |
| User-invoked | `Write, rewrite, or shrink an agent skill and its bundled references.` |

**Description characters:** plain text, max 1024 chars. Separate clauses with `.`, `;`, or `,`. **MUST NOT** use:

| Character | Why |
|---|---|
| `—` `–` (em/en dash), ` - ` / `--` as punctuation | Breaks naive parsers; hyphens inside identifiers (`address-page-comments`) allowed |
| `<` `>` | Rejected by skill validators (XML/HTML injection guard) |
| `:` (colon + space) | YAML reads it as a nested mapping key |
| `#` (space + hash) | YAML starts a comment; rest of description dropped |
| Leading `-` `?` `:` `[` `]` `{` `}` `,` `&` `*` `!` `\|` `>` `'` `"` `%` `@` `` ` `` | YAML indicator; plain scalar cannot start with it |
| Tabs, line breaks in a plain scalar, leading/trailing whitespace | Multiline/indent parse errors |

**YAML safety:** frontmatter MUST parse. Use a folded block scalar (`description: >-`, text indented two spaces) for `description` and values containing `:`, quotes, backticks, `#`, or leading `[`, `{`, `*`, `&`, `!`, `%`, `@`. Never use `:` inside a plain scalar.

**Description as context pointer:** name the skill and its triggering branches. Pointer wording controls discovery; prune always-loaded descriptions harder than bodies:

- Front-load the skill's **leading word**.
- One trigger per branch. Synonyms renaming one branch are duplication; collapse them.
- Cut identity the body already carries. Keep triggers plus any "when another skill needs…" reach clause.
- Use the words users actually type, and the same words used in prompts, docs, and code.

## Invocation choice

Balance **context load** (always-loaded descriptions and `AGENTS.md`) against **cognitive load** (humans remembering skills). Spend human attention where judgement matters.

Pick one mode:

- **Model-invoked** (omit `disable-model-invocation`): agent and other skills can reach it; costs context load. Choose when the agent must reach it unprompted or another skill must invoke it.
- **User-invoked** (`disable-model-invocation: true`): only a human typing its name reaches it; no other skill can. Zero context load; description becomes a human-facing one-line summary, trigger lists stripped.
- When user-invoked skills multiply past memory, add one **router skill** naming the others and when to reach each.

## Skill invocation syntax

**Identity and task:** Use the exact discovered skill identifier, without a leading `/`, immediately followed by `skill`; retain a namespace when the installed runtime requires it. State the concrete task and expected result in wording consistent with its current description; keyword counts and copied descriptions are unnecessary. Preserve conditions, route/action, inputs, outputs and constraints in the call or adjacent prose. Dynamic callers resolve the exact name and description before rendering; never emit placeholders literally.

**Standalone calls:** Italicize the invocation phrase. Use these forms; replace illustrative placeholders before rendering:

| Case | Form |
|---|---|
| Simple skill | *Load and follow the `skill-name` skill to \<task and expected result\>.* |
| Explicit route | *Load and follow the `skill-name` skill to \<task and expected result\>, using route `route-name`.* |
| Inferred route | *Load and follow the `skill-name` skill to \<task and expected result\>; select the applicable route.* |

**Repeated dependencies:** Add an optional **Load and follow skills** section to the caller's `SKILL.md`, naming only its actual dependency skills. Example declaration:

> For every call to the `research`, `prove`, or `review` skill, load and follow its skill content in full and the selected route procedure. Read required resources before acting. Reuse complete content already loaded for the same revision.

The declaration governs calls when their conditions apply; listing a dependency does not load it immediately. Under this contract, use compact italicized calls: *Invoke the `skill-name` skill, route `route-name`, to \<task and expected result\>*; omit the route clause for simple skills or let the target router select it. Repeat skill identity, route when known, and task at separate decision points; keep the loading procedure shared. For alternatives at one decision point, a sentence naming the target skill may govern a condition/route/task table.

**Context:** The named-dependency contract must be available to the executing agent, including when it follows the caller's selected playbook. Independent prompts and workers receive a standalone call or their own contract naming the dependencies; expand compact calls when that context would be absent.

**Route selection:** Honor an explicit valid route. Otherwise continue an active route per the target's continuation policy, then infer from clear intent. Apply the target's ambiguity and combined-request policies. Unknown explicit route → report it and available routes; do not silently substitute. Use exact route identifiers from the target router; these call forms and routes are repository conventions, not Agent Skills specification fields.

**Optional rationale:** Append ordinary prose outside the italicized call: `(rationale: ...)`. Use one short clause only when it explains a non-obvious skill/route choice, unusual constraint, or required evidence. Put observable conditions before calls and mandatory behavior in the call or adjacent constraints; rationale explains rather than carries requirements. Omit generic benefits and repeated tasks. Applies to standalone, compact, simple and routed calls.

**Load before execution:** Load and follow the invoked skill content in full, then select and read its entire applicable route procedure, when separate, before acting. Read required references, tactics and text templates fully before their dependent steps; load conditional resources when their conditions apply. Resolve paths from the invoked skill's base directory. Continue truncated reads to EOF; partial content counts as not loaded. Apply this contract to delegated calls. Missing required content blocks dependent work; report the gap and continue independent work.

**Discovery is not loading:** Use the runtime's supported loading mechanism. Names, descriptions, excerpts, remembered summaries and invocation announcements do not satisfy loading. The phrase “load and follow” and italics do not add discovery capabilities. Reuse complete content already available for the same revision; reload after context loss or changes.

**Disclosure:** `SKILL.md` directly links every route and required resource with loading conditions. Routes name applicable resources from that index. Preserve one-level links and skill-local ownership; callers invoke the owner instead of opening its internals. A skill without routes executes its body procedure. Load only selected or triggered resources.

**Scope:** These rules govern executable instructions and generated calls. Human slash examples, descriptions, command parsing, prohibitions and citations keep their natural form. Execute scripts and consume binary assets as instructed; reading their bytes as prose is unnecessary. External or generated targets resolve through the installed roster; verify their current description before rendering, and report missing dependencies rather than inventing names or instructions.

## Information hierarchy

Order by need: **steps** (ordered actions) → **inline reference** (rules, definitions, facts) → **disclosed reference** (separate files loaded by condition). Use any combination, including reference-only skills and flat rule sets.

- **Progressive disclosure:** inline shared material; disclose branch-only material behind conditional pointers.
- **Pointers:** name the loading condition: "Read `references/aws.md` when targeting AWS". Sharpen weak pointers before inlining their targets.
- Load references conditionally; never load every reference unconditionally.
- **Co-location:** keep a concept's definition, rules, and caveats under one heading.
- **Sprawl:** split lengthy live content by branch or sequence, or disclose reference.
- Keep `SKILL.md` body under 300 lines; 100–250 is a useful stricter target. Include only sections that materially help execution.

## Route composition

Use these repository conventions; they are not Agent Skills specification fields.

| Term | Responsibility |
|---|---|
| Router | Select outcomes or execution variants inside an activated `SKILL.md`. |
| Route | One selectable path with a trigger and output contract; represented in the router, not a folder. |
| Playbook | Own one route's end-to-end procedure: inputs, decisions, steps, failures, output, completion. |
| Tactic | Solve a conditional subproblem: observable trigger, technique, result/evidence; reusable across routes. |
| Reference | Supply knowledge, schemas, examples, or conventions without owning a task. |

| Need | Structure |
|---|---|
| One short procedure | Inline Workflow; no router needed |
| Related outcomes with distinct substantial procedures | Routing in `SKILL.md`; `playbooks/<route>.md` |
| One or two short methods | Inline Tactics |
| Bulky, conditional, or multi-playbook technique | `tactics/<name>.md` |
| Supporting knowledge | `references/` |
| Fillable output | `templates/` |
| Repeated or error-prone deterministic work | `scripts/` |
| Independent discovery or authority boundary | Separate skill |

Generate only justified files and directories. Keep shared invariants and selection in `SKILL.md`; the selected playbook owns execution. For each route define an unambiguous trigger, playbook, and output contract; specify ambiguity handling, continuation, and combined-request order. Read only the selected playbook, then select again only per the continuation policy.

Link every conditional playbook, tactic, and reference directly from `SKILL.md` with its loading condition; read selected playbooks fully before acting and required or triggered resources fully before dependent steps. A playbook may name a registered tactic or reference and its trigger in prose, but must not introduce a loading chain or second router. Resolve bundled paths from the target skill base directory. Keep one authoritative tactic definition for all consuming routes.

**Kind folders:** A skill with several same-kind playbooks MAY group them in a plural lowercase kind folder (`kinds/`, `strategies/`, `modes/`) instead of `references/`. Link every file directly from the `SKILL.md` routing table; bundled-path, skill-local and one-level-deep rules apply. Name sibling playbooks in prose (`component` kind), never link between them.

## Steps and completion criteria

End every step with a checkable completion condition, exhaustive where omissions matter ("every modified model accounted for", not "produce a change list"). Apply the same demand to reference rules. Number steps only when order matters; otherwise state decision criteria.

**Body blocks** — compose; default to Workflow, add others only when needed:

- **Routing** — select related task outcomes; use Route composition to separate selection from playbook execution.
- **Workflow** — ordered steps. When cases need different steps, make step 1 a branch: "**New file?** → Creation steps; **Existing file?** → Editing steps".
- **Loop** — repeat-until work (interview, review, validate → fix → repeat). State the exit condition and the steps every pass runs; a step that always runs belongs in the loop, not in Tactics.
- **Tactics** — unordered techniques, each with an observable trigger, an action, and a result; state when triggers are re-checked. Use bold-lead lines, not tables, so a tactic can carry bullets and pointers.
- **Examples** — input → output pairs when output style or quality matters; examples outperform descriptions of style.
- Defend premature completion in order: sharpen the bound first; only if irreducibly fuzzy *and* the rush is observed, split the sequence. Hiding later steps works only across a real context boundary (hand-off or subagent); an inline call clears nothing.

**`## Completion criteria` section:** when results are not self-evident, define observable conditions on files, output, or state, not effort.

- Name it **Completion criteria**; not `Verification`, `Validation`, `Testing`, or `Acceptance criteria`.
- State the result to observe, not how to run tests. A skill's own test suite is repository tooling: **MUST NOT** appear in a skill (no test commands, test paths, test-only dependencies).
- Omit when step completion conditions already prove the result. Do not repeat the same checks in workflow, output, and completion sections.

**Completeness sweep** — checks whether required scope was omitted (completion criteria check the result meets its contract).

- Add for multi-part work with independently missable obligations: features, cross-file refactors, migrations, broad research.
- When used, it **MUST** run last, after every other pass. Re-read the request and acceptance criteria; reconstruct explicit and implied obligations from existing architecture/conventions, affected paths, tests, docs, configuration/migrations, and error/security/observability/compatibility concerns. Map every obligation through `Requirement → Implementation → Test → Documentation`; state when a link is not applicable.
- Resolve uncovered obligations by implementing, asking, or reporting explicit deferral. **MUST NOT** declare completion with an unaccounted obligation.
- Omit for small bounded work already proven by checks. **MUST NOT** duplicate checks across sweep and completion criteria.

Repository concept: `docs/concepts/ops-completeness-sweep.md`.

## Output contract

Define what the agent must produce: artifacts, format, ordering, location. Include explicit outcomes for the edge cases:

- **No result** — e.g. return "No findings." after a complete pass; do not pad with suggestions.
- **Incomplete** — e.g. report "Review incomplete" plus missing evidence; never guess.
- **Unverified** — mark assumptions and unverified candidates separately from verified results.

**Structured response** (JSON/YAML an agent returns): open with a `| Field | Content |` table giving each field's meaning, allowed values, and empty case; then one compact example showing every field once (one array item each), not an exhaustive instance; then the failure shape. The table plus example must suffice to reconstruct any valid response.

## When to split

Give each skill one phrase of purpose. Split only when justified:

- **By invocation** — split off a model-invoked skill when a distinct leading word should trigger it alone, or another skill must reach it.
- **By sequence** — split a run of steps when post-completion steps tempt the agent to rush the current one. Merging sequences has the reverse effect.
- **Compose by invoking the owner.** Behaviour needed by one skill stays inline; behaviour needed by several gets one owning skill that others invoke. Never restate another skill's procedure.

## Instruction precision

**Constraint → mechanism → rationale → failure behavior** — use for critical requirements:

- **Constraint:** what MUST or MUST NOT happen.
- **Mechanism:** how the agent executes it.
- **Rationale:** why it matters (only when non-obvious).
- **Failure behavior:** what happens when blocked.

> MUST delegate codebase exploration to a subagent. The subagent returns relevant file paths and evidence. MUST NOT substitute direct exploration, even if faster. Rationale: preserve parent context. If delegation is unavailable, report the blocker rather than silently substituting another mechanism.

Verify critical constraints through observable actions or external checks; rationale alone cannot enforce them. Explicitly prohibit plausible substitutions.

**Degrees of freedom** — match prescription to task risk:

| Task | Agent freedom | Instruction style |
|---|---|---|
| Exploration | High | Define objective and evidence |
| Design | High–Medium | Define constraints and decision criteria |
| Implementation | Medium | Preserve contracts and conventions |
| Testing | Medium–Low | Define required checks and results |
| Migration | Low | Specify ordering, mechanism, recovery |
| Destructive operations | Very low | Require authorization and explicit safeguards |

**Failure policies** — pick one per critical step:

- **Fail closed** — mechanism mandatory: stop, report blocker, MUST NOT replace it (e.g. no direct SQL when the migration tool is unavailable).
- **Controlled fallback** — alternatives permitted: name them ("Search with `rg`. If unavailable, use `grep -R`.").
- **Graceful degradation** — partial work valuable: complete independent parts, report what did not run, MUST NOT claim full success.

## Gotchas

When a skill depends on an external tool, API, or platform quirk, add `## Gotchas`. State the constraint first; add why only when it changes handling. Record only knowledge the agent cannot find by looking.

## Subagents

Run subagents through prose instructions describing task, scope, inputs, constraints, and expected output. Do not instruct agents to call `runSubagent` directly. Pass context pointers (paths, IDs) rather than duplicated content; pass absolute paths to bundled files.

A brief requiring a skill **MUST** name a skill-capable agent type, `general-purpose`; forbid edits for read-only work. Codebase lookups use the `research` skill's Explore route in the caller's session. Never wrap a skill that spawns workers (`research`, `prove`, `challenge-this`) inside another subagent. Batch many claims into one `prove` call. Plain grep or LSP checks may use the built-in `explore` agent.

## Resources

| Folder | Holds |
|---|---|
| `playbooks/` | substantial route procedures; create only when needed |
| `tactics/` | substantial conditional techniques shared or used by routes; create only when needed |
| `scripts/` | executable automation |
| `references/` | decision/reference material |
| `assets/` | files used unchanged |
| `templates/` | scaffolds to fill or modify |

- Keep up to two category files at skill root; otherwise use the matching resource folder. Name linked files for what they hold.
- **Bundled paths**, including kind folders, resolve from the skill base directory, never caller CWD; write them relative to the skill root (`references/x.md`). Example: **Run `./scripts/run.py` from this skill's base directory**.
- **Skill-local resources:** each skill **MUST** bundle required resource files inside its own folder; **MUST NOT** read, link, or execute resource files from another skill's folder. Copy required resources in. Invoking another skill remains allowed.
- **Keep references one level deep:** `SKILL.md` links every reference directly; references **MUST NOT** load another file. Cite exact headings in already-loaded files instead. Loading chains risk partial reads. See sources below.
- **Hand-back by action:** a reference returns control by naming the action and the target section's exact heading, never the file name or a step number. Example: "Return control to the orchestrator for *Frontier check*."
- **Long references:** over 100 lines, start with `## Contents` listing every section by exact heading so previews expose the full scope.
- **Read references fully:** read every required or conditionally triggered reference in full before dependent work; **MUST NOT** preview (`head`, partial ranges). A truncated read continues by range to end of file; a partially read reference counts as not loaded.
- Use scripts for repetitive or fragile operations. Prefer Python over shell-specific scripts; use the repository-supported Python command.
- New plugin → register it in the repository's plugin marketplace/manifest in the same change; this repository uses `.github/plugin/marketplace.json`.

## Template ownership

- **Template owns rendering; skill owns orchestration.** Template: structure, format, conditions, local constraints. `SKILL.md`: selection, workflow, inputs/outputs, shared rules.
- `{{value|hint}}` — preferred field-local guidance.
- `<!-- @: instruction -->` — hidden structural/rendering directive; **MUST** be one terse line.
- Templates MAY define local **Rules** and **Gotchas**. Keep template-specific guidance in the template; move only shared/cross-template guidance to `SKILL.md` or `references/`.

## Syntax legend

| Syntax | Meaning | Example |
|---|---|---|
| **bold** | Required rule, label, warning | **Required:** Run tests. |
| *italic* | Skill invocation phrase | *Load and follow the `atlassian` skill to fetch the Confluence page as Markdown.* |
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

- **Single source of truth:** one meaning, one place within a skill. Duplicate across skills only to preserve skill-local resources.
- **Environment:** use `package.json`, config, layout, `--help`; record only undiscoverable conventions, reasons, gotchas.
- **Relevance:** delete unrelated or stale lines.
- **No-ops** — apply No-op test in the already-loaded wording.md; delete stale rules and no-ops.

## Evaluation

Treat authoring as iterative: run representative tasks without the skill, identify the failing behavior, write the smallest instruction that fixes it, rerun, compare. Judge actual traces and artifacts, not wording alone. Dimensions: trigger accuracy (positive, negative, near-miss prompts), execution correctness, constraint compliance (include prompts tempting a bypass), recovery, regression, efficiency.

## Before finishing

- Executable calls use a standalone form or a compact form covered by a named-dependency contract; full body, selected route and required-resource loading conditions are explicit, and workers receive their own loading context.
- Valid frontmatter; trigger-rich description free of forbidden description characters.
- `SKILL.md` body under 300 lines.
- No duplicate procedures within a skill; bundled resource paths stay inside the skill folder and resolve.
- No test commands or test-only dependencies; result checks live under `## Completion criteria`.
- Every critical step has a failure policy; every step has a checkable completion condition.
- No credentials, tokens, or secrets.

Sources: migrated repository agent-facing authoring instructions; [mattpocock/skills](https://github.com/mattpocock/skills) `writing-for-agents` and `writing-great-skills` (v1.1.0) GLOSSARY; Agent Skills best practices KB and AI diff review agent KB (October 2026), drawing on the [Agent Skills specification](https://agentskills.io/specification), [Anthropic skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), and OpenAI/Anthropic skill-creator guidance.
