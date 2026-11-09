# How

Grounding procedure of the Research skill. Paths resolve from the skill base directory.

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

For each stage, *run `subagents` skill to dispatch independent workers with role-based models* using **Dispatch**. Explorers use `how explorer` and explainers use `how explainer`. Require read-only access: use `explore`, or `general-purpose` with edits forbidden if MCP is needed. Use the role fallback on rejection, then the closest valid model of the same family.

**Spawn as Explore request.** Read this skill's **Explore request**; form per spawn: `@work` = the filled prompt template as prompt instruction (verbatim); `@depth` = `thorough` for explorers, `medium` for the simple-path explainer, `quick` for the synthesizing explainer; `[@target]` = repositories or services the question names; `@outputShape` = the template's Output section. Spawn each subagent with its request verbatim, instructing it to *run `research` skill Explore route for the inline read-only lookup — where is, what calls, flow, config evidence*. Research unavailable → spawn with the filled prompt template alone, as below.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. Spawn one explainer that explores and explains in one pass, built from `how/explainer-prompt.md` without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Spawn all explorers in a single message, each with `how/explorer-prompt.md` and its angle filled in. Fill placeholders only; keep the Read-only paragraph verbatim. Target has `graphify-out/` → paste the research skill's Graphify line verbatim into each explorer prompt body.

## 3. Synthesize (complex only)

Once all explorers have returned, spawn one explainer with `how/explainer-prompt.md` and every explorer's findings filled in.

## 4. Present

Return the explainer's output to Research. Require `file:line` evidence for code claims, and mark gaps. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output format

The explanation uses the sections defined in `how/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
