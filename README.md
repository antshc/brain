# Brain

My agent skills and plugins for GitHub Copilot — workflow automation, autonomous coding crews, PR review, and documentation lookups.

```sh
copilot plugin marketplace add antshc/brain
```

## Installation

Pick the plugin bundles you need. Each block uninstalls any stale version first, then installs the current one.

### Workflow plugins (wf, crew, ralph, review, harness)

```sh
(copilot plugin uninstall wf@brain >/dev/null 2>&1 || true) && \
copilot plugin install wf@brain && \
(copilot plugin uninstall crew@brain >/dev/null 2>&1 || true) && \
copilot plugin install crew@brain && \
(copilot plugin uninstall ralph@brain >/dev/null 2>&1 || true) && \
copilot plugin install ralph@brain && \
(copilot plugin uninstall review@brain >/dev/null 2>&1 || true) && \
copilot plugin install review@brain

(copilot plugin uninstall harness@brain >/dev/null 2>&1 || true) && \
copilot plugin install harness@brain
```

<details>
<summary>Uninstall workflow plugins</summary>

```sh
(copilot plugin uninstall wf@brain >/dev/null 2>&1 || true) && \
copilot plugin uninstall droid@brain >/dev/null 2>&1 || true) && \
copilot plugin uninstall crew@brain >/dev/null 2>&1 || true) && \
copilot plugin uninstall ralph@brain >/dev/null 2>&1 || true) && \
copilot plugin uninstall review@brain >/dev/null 2>&1 || true)
```

</details>

### Atlassian plugin (atl)

```sh
(copilot plugin uninstall atl@brain >/dev/null 2>&1 || true) && \
copilot plugin install atl@brain
```

### Azure platform plugin (azure-platform)

```sh
(copilot plugin uninstall az@brain >/dev/null 2>&1 || true) && \
copilot plugin uninstall learn-ms@brain >/dev/null 2>&1 || true) && \
copilot plugin uninstall azure-platform@brain >/dev/null 2>&1 || true) && \
copilot plugin install azure-platform@brain
```

### AWS skills (learn-aws)

```sh
gh skill install antshc/brain plugins/learn-aws/skills/search-aws-docs --agent github-copilot --scope project -f
```

### Brain engineering skills

```sh
gh skill install antshc/brain engineering/be-terse --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/suggest --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/render-mermaid-png --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/suggest-graphify-improvements --agent github-copilot --scope user -f
```

### dotnet skill (external)

```sh
copilot plugin list
copilot plugin marketplace add dotnet/skills
copilot plugin install dotnet@dotnet-agent-skills
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
gh skill install mattpocock/skills skills/engineering/codebase-design --agent github-copilot --scope user -f && \
gh skill install mattpocock/skills skills/engineering/diagnosing-bugs --agent github-copilot --scope user -f

```

```sh
gh skill search writing-great-skills --owner mattpocock
```

## Reference

Plugins bundle related skills (and, for `crew`, agents). Follow a link to read a skill's full `SKILL.md`.

### wf

Common everyday workflow automation skills. Expected to be useful to all developers.

- [grill-design](plugins/wf/skills/grill-design/SKILL.md): relentless interview and domain-modeling probe set that sharpens a plan or design while surfacing terms, decisions, and assumptions as they crystallise.
- [wayfinder](plugins/wf/skills/wayfinder/SKILL.md): plan work larger than one session as a shared map of decision tickets, resolved one at a time.
- [to-spec](plugins/wf/skills/to-spec/SKILL.md): turn the current conversation into a spec and publish it to the ticket tracker.
- [to-capabilities](plugins/wf/skills/to-capabilities/SKILL.md): break an idea or grilled requirement into solution-agnostic capabilities.
- [to-stories](plugins/wf/skills/to-stories/SKILL.md): package requirements into atomic, testable, FE/BE-split user stories with acceptance criteria.
- [to-tickets](plugins/wf/skills/to-tickets/SKILL.md): break a plan or spec into tracer-bullet tickets.
- [to-zdesign](plugins/wf/skills/to-zdesign/SKILL.md): synthesize or extend an authoritative feature design from specs and decisions.
- [architecture-diagram](plugins/wf/skills/architecture-diagram/SKILL.md), [behavior-diagram](plugins/wf/skills/behavior-diagram/SKILL.md), [code-diagram](plugins/wf/skills/code-diagram/SKILL.md): document architecture, behavior, or code structure as Mermaid diagrams and deltas.
- [to-contract-delta](plugins/wf/skills/to-contract-delta/SKILL.md): document contract deltas.
- [solution-agnostic](plugins/wf/skills/solution-agnostic/SKILL.md): strip implementation artifacts out of requirement or story text.
- [explore-codebase](plugins/wf/skills/explore-codebase/SKILL.md): delegate read-only codebase questions to a subagent.
- [prototype](plugins/wf/skills/prototype/SKILL.md): build a throwaway prototype to answer a design question.
- [research](plugins/wf/skills/research/SKILL.md): investigate a question against primary sources and capture findings in the repo.
- [record-adr](plugins/wf/skills/record-adr/SKILL.md), [record-concept](plugins/wf/skills/record-concept/SKILL.md), [record-term](plugins/wf/skills/record-term/SKILL.md), [record-service](plugins/wf/skills/record-service/SKILL.md), [record-deployment-view](plugins/wf/skills/record-deployment-view/SKILL.md): capture ADRs, Concepts, glossary terms, services, and deployment topology into the docs the moment they crystallise.
- [bootstrap-docs](plugins/wf/skills/bootstrap-docs/SKILL.md) / [index-docs](plugins/wf/skills/index-docs/SKILL.md): create and keep `ARCHITECTURE.md`/`CONTEXT.md` and their indexes in sync.
- [manage-backlog](plugins/wf/skills/manage-backlog/SKILL.md) / [init-wf](plugins/wf/skills/init-wf/SKILL.md): one-time repo setup for ticket tracker, labels, and doc layout.
- [track-ledger](plugins/wf/skills/track-ledger/SKILL.md): session ledger for decisions and assumptions staged during a grilling session.

### crew

Technology-agnostic autonomous coding crew (Codey, Chorey) and conventions.

Agents: [codey](agents/crew/codey.agent.md), [codey-py](agents/crew/codey-py.agent.md), [codey-dotnet](agents/crew/codey-dotnet.agent.md), [codey-ai](agents/crew/codey-ai.agent.md), [chorey](agents/crew/chorey.agent.md).

- [to-codey](plugins/crew/skills/to-codey/SKILL.md) / [to-chorey](plugins/crew/skills/to-chorey/SKILL.md): run the Codey or Chorey subagent for an implementation or review task.
- [to-commit](plugins/crew/skills/to-commit/SKILL.md): commit staged/unstaged changes using the agent's status report.
- [crew-select](plugins/crew/skills/crew-select/SKILL.md): resolve which Stack(s) apply to a piece of work and name the primary agent.
- [crew-codey-flow](plugins/crew/skills/crew-codey-flow/SKILL.md) / [crew-chorey-flow](plugins/crew/skills/crew-chorey-flow/SKILL.md): shared implementation/review workflow (input, gotchas, feedback loops, status-report contract).
- [crew-implement](plugins/crew/skills/crew-implement/SKILL.md): implementation rules — style, layers, design, and tests.
- [crew-review](plugins/crew/skills/crew-review/SKILL.md): behavior-preserving cleanup review of a commit or uncommitted work.
- [crew-feedback](plugins/crew/skills/crew-feedback/SKILL.md): run LSP, build, and test against changed files.
- [crew-gotchas](plugins/crew/skills/crew-gotchas/SKILL.md): read/write per-agent `GOTCHAS.md` friction notes.
- [init-crew](plugins/crew/skills/init-crew/SKILL.md): scaffold per-Stack convention files and `GOTCHAS.md`.

### ralph

AFK PR review and autonomous development loop.

- [dev](plugins/ralph/skills/dev/SKILL.md): pick the next open issue, implement it, and commit the result.
- [address](plugins/ralph/skills/address/SKILL.md): group PR review comments into issues, investigate, fix, and reply to every thread.
- [fix](plugins/ralph/skills/fix/SKILL.md): apply suggested changes from review comments.
- [create-worktree](plugins/ralph/skills/create-worktree/SKILL.md) / [delete-worktree](plugins/ralph/skills/delete-worktree/SKILL.md): create/reuse or remove an isolated git worktree per feature branch.
- [ralph-build](plugins/ralph/skills/ralph-build/SKILL.md): build the project in a worktree before implementation.

### review

PR code review skills with modular standards and guidance.

- [hitl](plugins/review/skills/hitl/SKILL.md): interactive, human-approved PR review — draft, approve, queue, then post inline comments.
- [architecture](plugins/review/skills/architecture/SKILL.md): audit drift between `ARCHITECTURE.md` and the actual codebase.
- [quality](plugins/review/skills/quality/SKILL.md): PR review for correctness, reliability, compatibility, performance, testability.
- [smells](plugins/review/skills/smells/SKILL.md): PR review against a fixed set of Fowler design smells.
- [reqs](plugins/review/skills/reqs/SKILL.md): PR requirements-coverage review.
- [fetch-diff](plugins/review/skills/fetch-diff/SKILL.md): check out a PR branch and fetch its diff per file for review skills.
- [posting](plugins/review/skills/posting/SKILL.md): post a review comment as an inline PR comment via the `gh` API.
- [to-review-comment](plugins/review/skills/to-review-comment/SKILL.md): format a raw review comment into the review tone of voice.

### harness

Harness configuration setup and resolution skills.

- [init-harness](plugins/harness/skills/init-harness/SKILL.md): create or update the Harness configuration file, resolving repo paths.
- [resolve-harness](plugins/harness/skills/resolve-harness/SKILL.md): resolve Harness settings from the nearest ancestor `.harness.env` file.

### atl

Atlassian workflow skills.

- [init-atl](plugins/atl/skills/init-atl/SKILL.md): first-run setup for a repo's Atlassian config, optionally generating `pub-<issue-type>` skills.
- [preflight-atl](plugins/atl/skills/preflight-atl/SKILL.md): resolve Atlassian connection facts before any Jira/Confluence operation.
- [fetch-work](plugins/atl/skills/fetch-work/SKILL.md) / [publish-work](plugins/atl/skills/publish-work/SKILL.md): fetch or create/update a Jira work item.
- [fetch-page](plugins/atl/skills/fetch-page/SKILL.md) / [publish-page](plugins/atl/skills/publish-page/SKILL.md): fetch or create/update a Confluence page.
- [map-markdown-adf](plugins/atl/skills/map-markdown-adf/SKILL.md): convert Markdown to/from Atlassian Document Format.

### azure-platform

Microsoft documentation, SDK reference, Azure CLI setup, authentication, and resource operation skills.

- [init-cli](plugins/azure-platform/skills/init-cli/SKILL.md) / [auth-principal](plugins/azure-platform/skills/auth-principal/SKILL.md): install/configure Azure CLI and authorize with a service principal.
- [query-azure](plugins/azure-platform/skills/query-azure/SKILL.md): discover, inspect, create, update, and delete Azure resources with `az`.
- [search-ms-docs](plugins/azure-platform/skills/search-ms-docs/SKILL.md): query official Microsoft documentation.
- [search-ms-code-samples](plugins/azure-platform/skills/search-ms-code-samples/SKILL.md): find working code samples and verify Microsoft SDK API signatures.

### learn-aws

AWS documentation skills for querying official AWS docs, API references, and regional availability.

- [search-aws-docs](plugins/learn-aws/skills/search-aws-docs/SKILL.md): understand AWS services and find API references from official docs.
- [search-aws-sdk-nuget](plugins/learn-aws/skills/search-aws-sdk-nuget/SKILL.md): AWS SDK for .NET NuGet package contract coverage — versions, APIs, signatures, upgrade guidance.

### engineering

General-purpose skills not tied to a specific platform.

- [be-terse](skills/engineering/be-terse/SKILL.md): rephrase or tighten a selection into terse, agent-optimized text.
- [suggest](skills/engineering/suggest/SKILL.md): analyze provided information and propose improvements with reasoning.
- [render-mermaid-png](skills/engineering/render-mermaid-png/SKILL.md): render Mermaid diagrams as high-resolution PNGs.
- [suggest-graphify-improvements](skills/engineering/suggest-graphify-improvements/SKILL.md): audit a Graphify knowledge graph and suggest evidence-backed improvements.
- [find-root-cause](skills/engineering/find-root-cause/SKILL.md): drive a bug or regression down to its root cause on cited evidence alone.
- [ask-dev](skills/engineering/ask-dev/SKILL.md): answer a manual tester's question about a codebase in black-box terms.
- [inspect-nuget-source](skills/engineering/inspect-nuget-source/SKILL.md): verify facts about a NuGet package's real API or behavior.
- [sync-skill](skills/engineering/sync-skill/SKILL.md): merge upstream skill improvements into a customized local copy.
