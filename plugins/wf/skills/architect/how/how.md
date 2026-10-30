# How

Grounding procedure of the `architect` skill. Paths resolve from the skill base directory.

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Every spawn is a read-only subagent (`agent_type: explore`, or `general-purpose` with a brief that forbids edits when the explorer needs MCP). Explorers use the `how explorer` role and every explainer uses the `how explainer` role. Set `model` to the role's value in `models.md`, or to its fallback if the value is missing. Leave `model` unset when the value is `auto` or `inherit-parent`. If the subagent tool rejects a model, use the fallback and say so. If it rejects the fallback, use the closest valid model of the same family from its error message. Pick each subagent's reasoning effort per `references/subagents.md`.

**Spawn as `explore-codebase` request.** Read `explore-codebase` skill's **Request**; form per spawn: `@work` = the filled prompt template as prompt instruction (verbatim); `@depth` = `thorough` for explorers, `medium` for the simple-path explainer, `quick` for the synthesizing explainer; `[@target]` = repositories or services the question names; `@outputShape` = the template's Output section. Spawn each subagent with its request verbatim, instructing it to *run `explore-codebase` skill for the read-only lookup — resolve target, locate symbols, callers, flow, config evidence*. Skill unavailable → spawn with the filled prompt template alone, as below.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. Spawn one explainer that explores and explains in one pass, built from `how/explainer-prompt.md` without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Spawn all explorers in a single message, each with `how/explorer-prompt.md` and its angle filled in.

## 3. Synthesize (complex only)

Once all explorers have returned, spawn one explainer with `how/explainer-prompt.md` and every explorer's findings filled in.

## 4. Present

Present the explainer's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output format

The explanation uses the sections defined in `how/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
