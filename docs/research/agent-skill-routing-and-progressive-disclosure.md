# Skill routing, playbooks, tactics, and progressive disclosure

Research date: 2026-11-10.

## Question

What does the Agent Skills standard require, and when should a skill use a router, playbook, tactic, or supporting reference?

## What the industry standard actually defines

The [Agent Skills specification](https://agentskills.io/specification) defines a skill directory with a required `SKILL.md` containing `name` and `description` metadata and Markdown instructions. Optional bundled resources include `references/`, `scripts/`, and `assets/`. It does not standardize the terms *router*, *route*, *playbook*, or *tactic*, or prescribe folder names for them. Those are authoring conventions.

Progressive disclosure has three stages:

1. **Discovery:** the agent sees skill metadata (primarily name and description).
2. **Activation:** the full `SKILL.md` is read after the skill is selected.
3. **On demand:** only task-relevant supporting files are read or scripts executed.

The specification recommends a `SKILL.md` below 500 lines and roughly 5,000 tokens, with relative file paths and references linked directly from `SKILL.md` rather than through long reference chains. These are authoring recommendations, not mandatory schema fields. See [specification](https://agentskills.io/specification) and [Anthropic best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

A Markdown link does not execute a route or import its target automatically. The skill must tell the agent **when to read** a referenced file. A runtime may also provide explicit skill/resource-reading tools. Vendor-specific frontmatter, such as `disable-model-invocation`, is not part of the portable core specification; support varies by host. See [Cloudflare Agent Skills](https://developers.cloudflare.com/agents/concepts/agent-skills/).

### Patterns demonstrated by public repositories

| Source | Observed pattern | Why it matters |
| --- | --- | --- |
| [Microsoft B2B Outreach Suite](https://github.com/microsoft/cat-agent-skills/blob/main/submissions/b2b-outreach-suite/SKILL.md) | One `SKILL.md` maps six task intents directly to distinct playbooks in `references/`. | Concrete intent-to-playbook router, including ambiguous and combined requests. |
| [Cursor pstack poteto-mode](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md) | Selects task playbooks (investigation, bug fix, shipping, etc.) and invokes other skills conditionally. | Larger orchestration router with task-level procedures. |
| [Anthropic PDF](https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md) | Core operations inline; advanced guidance and form handling in separate files. | Conditional reference loading without a full route table. |
| [Vercel composition patterns](https://github.com/vercel-labs/agent-skills/blob/main/skills/composition-patterns/SKILL.md) | Categorizes rules and points to individual rule files. | Fine-grained technique/reference selection, analogous to tactics. |
| [Trail of Bits open-sourcing](https://github.com/trailofbits/skills/blob/main/plugins/open-sourcing/skills/open-sourcing/SKILL.md) | Selects language-specific guides and an organization policy overlay only when applicable. | Conditional domain/reference selection. |
| [obra superpowers using-superpowers](https://github.com/obra/superpowers/blob/main/skills/using-superpowers/SKILL.md) | Routes to independent process skills and platform-specific references. | Distinguishes internal routing from cross-skill selection. |

These are implementation examples, not additional requirements of the specification.

## When to use each pattern

| Pattern | Responsibility | Use when | Avoid when |
| --- | --- | --- | --- |
| **Inline instructions** | Define one compact procedure. | One small, coherent task; all instructions are almost always needed. | Most instructions concern uncommon variants. |
| **Router** | Select a route/reference from intent or observed conditions. | One capability has several related outcomes or variants. | The paths have unrelated triggers, permissions, or lifecycles. |
| **Playbook** | Define a complete task procedure, decisions, checks, and completion criteria. | A route has multiple dependent actions or meaningful gates. | A short instruction or single technique suffices. |
| **Tactic** | Apply a narrow, reusable method within a route or playbook. | Several workflows need the same conditional technique, e.g. runtime verification. | The file would own the complete task outcome. |
| **Reference** | Supply facts, schemas, conventions, examples, or templates. | Information is needed only for some tasks or steps. | Every run needs it to select the correct behavior. |
| **Script** | Perform deterministic, repetitive, or error-prone operations. | A reliable tool can replace repeatedly reconstructed commands. | Judgment or context-sensitive decisions cannot safely be encoded. |
| **Separate skill** | Expose an independently discoverable capability. | The intent deserves its own trigger or authority boundary. | It is just one optional route or technique of an existing capability. |

A **route** is the selected behavior. A **router** chooses it. A **playbook** explains how to complete it. A **tactic** solves a narrower problem during it. A **reference** supplies knowledge rather than necessarily prescribing actions. This taxonomy is a recommended convention, not an Agent Skills schema.

### Router versus router skill

- **Internal router:** a section of one activated `SKILL.md` dispatching to its own references/playbooks. It does not create additional discoverable skills.
- **Router skill:** an independently invocable skill that chooses other installed skills. Invocation and accessibility depend on the host; a mere link to another skill does not guarantee invocation.

### Recommended decision rules

1. Keep global invariants and the route table in `SKILL.md` so every route receives them.
2. State each route's trigger, primary file, and output contract; read the selected file fully.
3. Load conditional tactics at the point of need; never preload unrelated routes.
4. Link each required supporting file directly from `SKILL.md`, even if files are stored in subdirectories.
5. Keep one owner for each convention; avoid copying instructions into several playbooks.
6. Preserve short operations inline; extraction should remove meaningful unused context, not merely create more files.
7. Choose separate skills when trigger precision, independent ownership, or authorization boundaries outweigh a shared entry point.

## Application to Brain

Use a single discoverable entry skill for coherent capability families such as `design`, `review`, and `define`, with explicit route selection. Place route procedures in playbooks/references; keep recurring conditional methods as tactics. A flat `references/` directory is compatible with the standard. Filename prefixes such as `grill.md`, `verification.md`, and `issue-template.md` can communicate their roles without introducing more auto-discoverable skills.

For example, a `design` router can map *challenge a design* to `references/grill.md`, *produce a specification* to `references/spec.md`, and *decompose tickets* to `references/tickets.md`. Load `references/verification.md` only when conclusions require independent proof. Keep GitHub-specific operations in the corresponding operational skill rather than copying their implementation into every route.

**Tradeoff:** consolidation reduces discovery entries but increases dependence on a clear umbrella description and accurate internal routing. [OpenAI's skill guidance](https://learn.chatgpt.com/docs/build-skills) notes that large inventories may consume their discovery budget and have descriptions shortened or omitted; internal references do not add discovery entries.

## Verification

Test the two selection boundaries separately:

- **Activation:** intended prompts select the umbrella skill; unrelated prompts do not.
- **Routing:** each activation chooses the correct route, including ambiguous and combined intents.
- **Disclosure:** only required route files and conditionally relevant tactics are read.
- **Outcome:** each playbook's completion criteria are satisfied; shared conventions remain consistent.

Use positive, negative, and mixed-intent prompts. Measure observed choices rather than relying on the directory structure as proof.

## Primary sources

- [Agent Skills specification](https://agentskills.io/specification)
- [Anthropic skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [OpenAI skill creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)
- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Cloudflare: Agent Skills](https://developers.cloudflare.com/agents/concepts/agent-skills/)
- GitHub implementation links in the examples table above.
