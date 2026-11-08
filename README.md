# Brain

My agent skills and plugins for GitHub Copilot — workflow automation, autonomous coding crews, PR review, and documentation lookups.

```sh
copilot plugin marketplace add antshc/brain
```

## Installation

Pick the plugin bundles you need. Each block uninstalls any stale version first, then installs the current one.

### Workflow plugins (wf, crew, ralph, review)

```sh
(copilot plugin uninstall wf@brain >/dev/null 2>&1 || true) && \
copilot plugin install wf@brain && \
(copilot plugin uninstall crew@brain >/dev/null 2>&1 || true) && \
copilot plugin install crew@brain && \
(copilot plugin uninstall review@brain >/dev/null 2>&1 || true) && \
copilot plugin install review@brain && \
(copilot plugin uninstall skill@brain >/dev/null 2>&1 || true) && \
copilot plugin install skill@brain && \
(copilot plugin uninstall ralph@brain >/dev/null 2>&1 || true) && \
copilot plugin install ralph@brain
```

<details>
<summary>Uninstall deprecated plugins</summary>

```sh
(copilot plugin uninstall droid@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall solution@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall learn-aws@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall aws-platform@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall azure-platform@brain >/dev/null 2>&1 || true)
```

</details>

### Atlassian plugin (atl)

```sh
(copilot plugin uninstall atl@brain >/dev/null 2>&1 || true) && \
copilot plugin install atl@brain
```

### Microsoft platform plugin (ms)

```sh
(copilot plugin uninstall ms@brain >/dev/null 2>&1 || true) && \
copilot plugin install ms@brain
```

### AWS plugin (aws)

```sh
(copilot plugin uninstall aws-platform@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall aws@brain >/dev/null 2>&1 || true) && \
copilot plugin install aws@brain
```

### Verify plugin (verify)

```sh
(copilot plugin uninstall verify@brain >/dev/null 2>&1 || true) && \
copilot plugin install verify@brain
```

### Skill authoring plugin (skill)

```sh
(copilot plugin uninstall skill@brain >/dev/null 2>&1 || true) && \
copilot plugin install skill@brain
```


### Brain engineering skills

```sh
gh skill install antshc/brain engineering/be-terse --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/suggest --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/testing-integrations --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/render-mermaid-png --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/suggest-graphify-improvements --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/remove-zone-identifiers --agent github-copilot --scope user -f
```

Repo-level (run from the target repo; `init-wf` offers it), then edit the copy to match the repo's conventions:

```sh
gh skill install antshc/brain engineering/factory-mode --agent github-copilot --scope project
```

### dotnet skill (external)

```sh
copilot plugin list
copilot plugin marketplace add dotnet/skills
copilot plugin install dotnet@dotnet-agent-skills
```

### JetBrains skills (external)

Installs the `slides` skill (PPTX deck authoring) into the user space (`~/.copilot/skills/`) for GitHub Copilot.

```sh
gh skill install JetBrains/skills slides --agent github-copilot --scope user -f
```

### mattpocock skills (external)

**Productivity**

```sh
gh skill install mattpocock/skills skills/productivity/writing-great-skills --agent github-copilot --scope user -f && \
gh skill install mattpocock/skills skills/productivity/handoff --agent github-copilot --scope user -f && \
gh skill install mattpocock/skills skills/productivity/teach --agent github-copilot --scope user -f

gh skill install github/awesome-copilot skills/mini-context-graph --agent universal --scope user -f
```

**Engineering**

```sh
gh skill install mattpocock/skills skills/engineering/codebase-design --agent github-copilot --scope user -f

```

```sh
gh skill search writing-great-skills --owner mattpocock
```

## Reference

Plugins bundle related skills (and, for `crew`, agents). Follow a link to read a skill's full `SKILL.md`.

### wf

Agent: [Codey](plugins/wf/agents/codey.agent.md) implements requested coding tasks. `implement-spec` delegates tickets to `wf:codey`, with a `general-purpose` fallback.

- [diagnosing-bugs](plugins/wf/skills/diagnosing-bugs/SKILL.md): diagnose hard bugs or performance regressions, and fix them when explicitly requested.

Common everyday workflow automation skills. Expected to be useful to all developers.

- [grill-design](plugins/wf/skills/grill-design/SKILL.md): relentless interview with situational tactics that sharpens a plan or design while surfacing terms, decisions, and assumptions as they crystallise.
- [wayfinder](plugins/wf/skills/wayfinder/SKILL.md): plan work larger than one session as a shared map of decision tickets, resolved one at a time.
- [to-spec](plugins/wf/skills/to-spec/SKILL.md): turn the current conversation into a GitHub spec issue, with explicit offline Markdown publishing when needed.
- [to-stories](plugins/wf/skills/to-stories/SKILL.md): turn requirements, `/to-spec` output, or `/to-zdesign` output into an ordered story list, owning numbered headings, dependencies, Jira metadata, and one `/draft-story` run per story.
- [draft-story](plugins/wf/skills/draft-story/SKILL.md): draft one standalone story body with its formatted title, requirements, acceptance criteria, and optional technical notes.
- [code-sketch](plugins/wf/skills/code-sketch/SKILL.md): draft one single-pass code sketch with usage first, types and signatures with `not implemented` bodies, a module map for larger work, and a rationale.
- [to-tickets](plugins/wf/skills/to-tickets/SKILL.md): break a plan or spec into tracer-bullet tickets.
- [git-conventions](plugins/wf/skills/git-conventions/SKILL.md): branch, commit, PR, and review comment formats.
- [worktrees](plugins/wf/skills/worktrees/SKILL.md): inspect, create, reuse, or remove local Git worktrees with ownership checks. Install `wf` for Code Review and Address worktree operations.
- [implement-spec](plugins/wf/skills/implement-spec/SKILL.md): integrate the ticket graph sequentially or through parallel worktrees into a draft PR; hand off app verification and code review to factory mode.
- [to-zdesign](plugins/wf/skills/to-zdesign/SKILL.md): synthesize or extend an authoritative feature design from specs and decisions.
- [doc-architecture-diagram](plugins/wf/skills/doc-architecture-diagram/SKILL.md), [doc-behavior-diagram](plugins/wf/skills/doc-behavior-diagram/SKILL.md), [doc-code-diagram](plugins/wf/skills/doc-code-diagram/SKILL.md): document architecture, behavior, or code structure as Mermaid diagrams and deltas.
- [doc-contracts](plugins/wf/skills/doc-contracts/SKILL.md): document contract deltas.
- [writing-style](plugins/wf/skills/writing-style/SKILL.md): write, review, or unslop prose; normalize requirement or story text by stripping implementation artifacts.
- [explore-codebase](plugins/wf/skills/explore-codebase/SKILL.md): read-only codebase lookup run inside a caller-spawned subagent; callers fall back to the explore agent when the skill is unavailable.
- [experiment](plugins/wf/skills/experiment/SKILL.md): run a throwaway experiment to answer a design question.
- [research](plugins/wf/skills/research/SKILL.md): investigate a question against primary sources and capture findings in the repo; inspects a system as-built along the behavior, flow, or data axis, cited to `file:line`, with diagrams; inspects AWS and Azure implementation constraints (APIs, SDK, IAM/RBAC, networking, quotas, retries, failures) from provider docs and read-only CLI into one shared template. Includes How for current behavior and Why for historical rationale.
- [subagents](plugins/wf/skills/subagents/SKILL.md): dispatch independent workers, select model roles, compare Arena candidates, and run Swarm partitions or races.
- [define-concept](plugins/wf/skills/define-concept/SKILL.md): suggest which Concept to add or extend (or check a described one against recorded Concepts), question it against cited codebase evidence, and record the result.
- [inspect-nuget-source](plugins/wf/skills/inspect-nuget-source/SKILL.md): verify facts about a NuGet package's real API or behavior.
- [record-architecture](plugins/wf/skills/record-architecture/SKILL.md): record settled ADRs, Concepts, Deployables, deployment topology, or glossary terms; render concept bodies and compact decision bullets without saving. Select a mode explicitly or describe the artifact.
- [bootstrap-docs](plugins/wf/skills/bootstrap-docs/SKILL.md) / [index-docs](plugins/wf/skills/index-docs/SKILL.md): create and keep `ARCHITECTURE.md`/`GLOSSARY.md` and their indexes in sync.
- [init-wf](plugins/wf/skills/init-wf/SKILL.md): one-time repo setup for GitHub issue labels and doc layout, and offers repo-level `factory-mode` install; labels-only mode repairs missing labels. Backlog skills bundle their own GitHub guidance; research/bootstrap-docs remain local, and other skills retain their Jira workflows.

### crew

Technology-agnostic autonomous coding crew (Codey, Chorey) and conventions.

Agents: [codey-py](plugins/crew/agents/codey-py.agent.md), [codey-dotnet](plugins/crew/agents/codey-dotnet.agent.md), [chorey](plugins/crew/agents/chorey.agent.md). Crew agents return gotchas in their reports.

- [to-crew](plugins/crew/skills/to-crew/SKILL.md): run the Codey subagent for an implementation task.
- [crew-commit](plugins/crew/skills/crew-commit/SKILL.md): commit staged/unstaged changes using the agent's status report.
- [chorey-diff](plugins/crew/skills/chorey-diff/SKILL.md) owns Chorey's commit/uncommitted review bundle, aggregate stack detection, and exact restoration mechanics; Chorey passes the manifest stacks to `/crew-chore` and owns behavior-preserving cleanup, scoped checks, the revert decision, and its status report.
- [init-crew](plugins/crew/skills/init-crew/SKILL.md): copy stack-specific Copilot instructions and install per-stack Chorey rules.

### ralph

AFK PR review and autonomous development loop.

- [dev](plugins/ralph/skills/dev/SKILL.md): pick the next open issue, implement it, and commit the result.
- [fix](plugins/ralph/skills/fix/SKILL.md): apply suggested changes from review comments.
- [create-worktree](plugins/ralph/skills/create-worktree/SKILL.md) / [delete-worktree](plugins/ralph/skills/delete-worktree/SKILL.md): create/reuse or remove an isolated git worktree per feature branch.
- [ralph-build](plugins/ralph/skills/ralph-build/SKILL.md): build the project in a worktree before implementation.
- [init-harness](plugins/ralph/skills/init-harness/SKILL.md): copy the `harness` skill from template into `.github/skills/harness/`, ensure its settings file exists, and install its pull command.

### review

Code and technical solution review skills with modular standards and guidance.

- Code Review, Address, and HITL load formatting from [Git Conventions](plugins/wf/skills/git-conventions/SKILL.md). Install WF with `copilot plugin install wf@brain` before using these Review skills.
- [blast-radius](plugins/review/skills/blast-radius/SKILL.md): trace downstream breakage, run the decisive proof, and report verified risks.
- [address](plugins/review/skills/address/SKILL.md): group PR review comments into issues, investigate, fix, and reply to every thread.
- [hitl](plugins/review/skills/hitl/SKILL.md): interactive, human-approved PR review — draft, approve, queue, then post inline comments.
- [architecture](plugins/review/skills/architecture/SKILL.md): audit drift between `ARCHITECTURE.md` and the actual codebase.
- [code-review](plugins/review/skills/code-review/SKILL.md): independent bug, quality, code-smell and initiative reviewers; routes models by PR size/risk and posts evidence-backed findings. Initiative ID comes from the PR description’s leading `[initiative-id]` marker or a supported legacy body ID; accepts a user PR URL or a factory-mode call and fetches the diff into a fresh detached review worktree without cloning.
- [solution](plugins/review/skills/solution/SKILL.md): review a technical design for gaps, contradictions, risks, and readiness. Invoke as `review:solution`.
- [test-gaps](plugins/review/skills/test-gaps/SKILL.md): map a change's risks to existing tests, judge assertion strength, and return prioritized missing test cases. Invoke as `review:test-gaps`.

### atl

Atlassian workflow skills.

- [init-atl](plugins/atl/skills/init-atl/SKILL.md): first-run setup for a repo's Atlassian config, optionally generating `pub-<issue-type>` skills.
- [preflight-atlassian](plugins/atl/skills/init-atl/preflight-atlassian.SKILL.template.md): `init-atl` template generated per-repo into `.github/skills/preflight-atlassian/`; resolves Atlassian connection facts before any Jira/Confluence operation, and owns locating/parsing the repo's Atlassian config file.
- [fetch-work](plugins/atl/skills/fetch-work/SKILL.md) / [publish-work](plugins/atl/skills/publish-work/SKILL.md): fetch or create/update a Jira work item.
- [fetch-page](plugins/atl/skills/fetch-page/SKILL.md) / [publish-page](plugins/atl/skills/publish-page/SKILL.md): fetch or create/update a Confluence page.
- [address-page-comments](plugins/atl/skills/address-page-comments/SKILL.md): address open Confluence page review comments; edit the page in place with twg targeted edits, reply per thread, and answer comments whose anchor text was removed in a page comment.
- [map-markdown-adf](plugins/atl/skills/map-markdown-adf/SKILL.md): convert Markdown to/from Atlassian Document Format, and detect the constructs only ADF can express.

### ms

Microsoft documentation, SDK reference, Azure CLI setup, authentication, and resource operation skills.

- [init-cli](plugins/ms/skills/init-cli/SKILL.md) / [auth-principal](plugins/ms/skills/auth-principal/SKILL.md): install/configure Azure CLI and authorize with a service principal.
- [query-azure](plugins/ms/skills/query-azure/SKILL.md): discover, inspect, create, update, and delete Azure resources with `az`.
- [search-ms-docs](plugins/ms/skills/search-ms-docs/SKILL.md): query official Microsoft documentation.
- [search-ms-code-samples](plugins/ms/skills/search-ms-code-samples/SKILL.md): find working code samples and verify Microsoft SDK API signatures.

### aws

AWS documentation and SDK reference skills.

- [search-aws-docs](plugins/aws/skills/search-aws-docs/SKILL.md): understand AWS services and find API references from official docs.
- [search-aws-sdk-nuget](plugins/aws/skills/search-aws-sdk-nuget/SKILL.md): AWS SDK for .NET NuGet package contract coverage — versions, APIs, signatures, upgrade guidance.

### verify

Agent-driven proof of app behavior for TypeScript (pnpm) or Python repos: a `mole` CLI that drives the app in a real Chrome, receipts with a revision-bound verdict, web and API surface adapters, and feature maps.

- [init-verify](plugins/verify/skills/init-verify/SKILL.md): install the TypeScript or Python kit into a repo, research the codebase, ask which surfaces to prove (web, api, both), and generate starter cases plus repository-local `verify-<app>` and `maintain-verify-<app>` skills (the latter keeps maps, adapters and proofs honest as the app changes and re-proves on a fresh build).
- [playwright-cli](plugins/verify/skills/playwright-cli/SKILL.md): browser driving helper for ad-hoc exploration and Playwright tests.

### skill

Skill authoring from bundled best practices (repo rules, mattpocock writing-for-agents, Agent Skills KBs).

- [grill-skill](plugins/skill/skills/grill-skill/SKILL.md): interview one question at a time to define purpose, triggers, contract, body blocks, and constraints; outputs a confirmed skill brief for you to pass to `/write-skill`. Manual-only.
- [write-skill](plugins/skill/skills/write-skill/SKILL.md): write mode drafts the skill (template with composable Workflow, Loop, Tactics, and Reference blocks) then shrinks it, each in a fresh subagent; shrink mode only tightens existing skill, agent, or instructions files while preserving behavior. Manual-only.

### engineering

General-purpose skills not tied to a specific platform.

- [be-terse](skills/engineering/be-terse/SKILL.md): rephrase or tighten a selection into terse, agent-optimized text.
- [suggest](skills/engineering/suggest/SKILL.md): analyze provided information and propose improvements with reasoning.
- [testing-integrations](skills/engineering/testing-integrations/SKILL.md): select and run focused integration, functional-slice, and regression tests with evidence.
- [render-mermaid-png](skills/engineering/render-mermaid-png/SKILL.md): render Mermaid diagrams as high-resolution PNGs.
- [suggest-graphify-improvements](skills/engineering/suggest-graphify-improvements/SKILL.md): audit a Graphify knowledge graph and suggest evidence-backed improvements.
- [ask-dev](skills/engineering/ask-dev/SKILL.md): answer a manual tester's question about a codebase in black-box terms.
- [sync-skill](skills/engineering/sync-skill/SKILL.md): merge upstream skill improvements into a customized local copy.
- [remove-zone-identifiers](skills/engineering/remove-zone-identifiers/SKILL.md): delete Windows Zone.Identifier markers from the repo on any OS.
- [factory-mode](skills/engineering/factory-mode/SKILL.md): repo-level engineering instructions; restate the goal, route to a playbook, delegate, and verify on the real artifact. Installed per repo by `init-wf` and customized by its users.
