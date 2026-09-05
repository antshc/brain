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
(copilot plugin uninstall droid@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall crew@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall ralph@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall review@brain >/dev/null 2>&1 || true)
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
(copilot plugin uninstall learn-ms@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall azure-platform@brain >/dev/null 2>&1 || true) && \
copilot plugin install azure-platform@brain
```

### AWS skills (learn-aws)

```sh
gh skill install antshc/brain skills/learn-aws/search-aws-docs --agent github-copilot --scope project -f
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
gh skill install mattpocock/skills skills/engineering/research --agent github-copilot --scope user -f
```

```sh
gh skill search writing-great-skills --owner mattpocock
```

## Reference

Plugins bundle related skills (and, for `crew`, agents). Follow a link to read a skill's full `SKILL.md`.

### wf

Common everyday workflow automation skills. Expected to be useful to all developers.

- [grill-design](skills/wf/grill-design/SKILL.md): relentless interview and domain-modeling probe set that sharpens a plan or design while surfacing terms, decisions, and assumptions as they crystallise.
- [wayfinder](skills/wf/wayfinder/SKILL.md): plan work larger than one session as a shared map of decision tickets, resolved one at a time.
- [to-spec](skills/wf/to-spec/SKILL.md): turn the current conversation into a spec and publish it to the ticket tracker.
- [to-capabilities](skills/wf/to-capabilities/SKILL.md): break an idea or grilled requirement into solution-agnostic capabilities.
- [to-stories](skills/wf/to-stories/SKILL.md): package requirements into atomic, testable, FE/BE-split user stories with acceptance criteria.
- [to-tickets](skills/wf/to-tickets/SKILL.md): break a plan or spec into tracer-bullet tickets.
- [to-zdesign](skills/wf/to-zdesign/SKILL.md): synthesize or extend an authoritative feature design from specs and decisions.
- [to-diagram](skills/wf/to-diagram/SKILL.md) / [to-contract-delta](skills/wf/to-contract-delta/SKILL.md): document behavior as Mermaid diagrams or contract deltas.
- [solution-agnostic](skills/wf/solution-agnostic/SKILL.md): strip implementation artifacts out of requirement or story text.
- [explore-codebase](skills/wf/explore-codebase/SKILL.md): delegate read-only codebase questions to a subagent.
- [prototype](skills/wf/prototype/SKILL.md): build a throwaway prototype to answer a design question.
- [research](skills/wf/research/SKILL.md): investigate a question against primary sources and capture findings in the repo.
- [record-adr](skills/wf/record-adr/SKILL.md), [record-concept](skills/wf/record-concept/SKILL.md), [record-term](skills/wf/record-term/SKILL.md), [record-service](skills/wf/record-service/SKILL.md), [record-deployment-view](skills/wf/record-deployment-view/SKILL.md): capture ADRs, Concepts, glossary terms, services, and deployment topology into the docs the moment they crystallise.
- [bootstrap-docs](skills/wf/bootstrap-docs/SKILL.md) / [index-docs](skills/wf/index-docs/SKILL.md): create and keep `ARCHITECTURE.md`/`CONTEXT.md` and their indexes in sync.
- [manage-backlog](skills/wf/manage-backlog/SKILL.md) / [setup-wf](skills/wf/setup-wf/SKILL.md): one-time repo setup for ticket tracker, labels, and doc layout.
- [track-ledger](skills/wf/track-ledger/SKILL.md): session ledger for decisions and assumptions staged during a grilling session.

### crew

Technology-agnostic autonomous coding crew (Codey, Chorey) and conventions.

Agents: [codey](agents/crew/codey.agent.md), [codey-py](agents/crew/codey-py.agent.md), [codey-dotnet](agents/crew/codey-dotnet.agent.md), [codey-ai](agents/crew/codey-ai.agent.md), [chorey](agents/crew/chorey.agent.md).

- [to-codey](skills/crew/to-codey/SKILL.md) / [to-chorey](skills/crew/to-chorey/SKILL.md): run the Codey or Chorey subagent for an implementation or review task.
- [to-commit](skills/crew/to-commit/SKILL.md): commit staged/unstaged changes using the agent's status report.
- [crew-select](skills/crew/crew-select/SKILL.md): resolve which Stack(s) apply to a piece of work and name the primary agent.
- [crew-codey-flow](skills/crew/crew-codey-flow/SKILL.md) / [crew-chorey-flow](skills/crew/crew-chorey-flow/SKILL.md): shared implementation/review workflow (input, gotchas, feedback loops, status-report contract).
- [crew-implement](skills/crew/crew-implement/SKILL.md): implementation rules — style, layers, design, and tests.
- [crew-review](skills/crew/crew-review/SKILL.md): behavior-preserving cleanup review of a commit or uncommitted work.
- [crew-feedback](skills/crew/crew-feedback/SKILL.md): run LSP, build, and test against changed files.
- [crew-gotchas](skills/crew/crew-gotchas/SKILL.md): read/write per-agent `GOTCHAS.md` friction notes.
- [setup-crew](skills/crew/setup-crew/SKILL.md): scaffold per-Stack convention files and `GOTCHAS.md`.

### ralph

AFK PR review and autonomous development loop.

- [dev](skills/ralph/dev/SKILL.md): pick the next open issue, implement it, and commit the result.
- [address](skills/ralph/address/SKILL.md): group PR review comments into issues, investigate, fix, and reply to every thread.
- [fix](skills/ralph/fix/SKILL.md): apply suggested changes from review comments.
- [create-worktree](skills/ralph/create-worktree/SKILL.md) / [delete-worktree](skills/ralph/delete-worktree/SKILL.md): create/reuse or remove an isolated git worktree per feature branch.
- [ralph-build](skills/ralph/ralph-build/SKILL.md): build the project in a worktree before implementation.

### review

PR code review skills with modular standards and guidance.

- [hitl](skills/review/hitl/SKILL.md): interactive, human-approved PR review — draft, approve, queue, then post inline comments.
- [architecture](skills/review/architecture/SKILL.md): audit drift between `ARCHITECTURE.md` and the actual codebase.
- [quality](skills/review/quality/SKILL.md): PR review for correctness, reliability, compatibility, performance, testability.
- [smells](skills/review/smells/SKILL.md): PR review against a fixed set of Fowler design smells.
- [reqs](skills/review/reqs/SKILL.md): PR requirements-coverage review.
- [fetch-diff](skills/review/fetch-diff/SKILL.md): check out a PR branch and fetch its diff per file for review skills.
- [posting](skills/review/posting/SKILL.md): post a review comment as an inline PR comment via the `gh` API.
- [to-review-comment](skills/review/to-review-comment/SKILL.md): format a raw review comment into the review tone of voice.

### harness

Harness configuration setup and resolution skills.

- [setup-harness](skills/harness/setup-harness/SKILL.md): create or update the Harness configuration file, resolving repo paths.
- [resolve-harness](skills/harness/resolve-harness/SKILL.md): resolve Harness settings from the nearest ancestor `.harness.env` file.

### atl

Atlassian workflow skills.

- [init-atl](skills/atl/init-atl/SKILL.md): first-run setup for a repo's Atlassian config, optionally generating `pub-<issue-type>` skills.
- [preflight-atl](skills/atl/preflight-atl/SKILL.md): resolve Atlassian connection facts before any Jira/Confluence operation.
- [fetch-work](skills/atl/fetch-work/SKILL.md) / [publish-work](skills/atl/publish-work/SKILL.md): fetch or create/update a Jira work item.
- [fetch-page](skills/atl/fetch-page/SKILL.md) / [publish-page](skills/atl/publish-page/SKILL.md): fetch or create/update a Confluence page.
- [map-markdown-adf](skills/atl/map-markdown-adf/SKILL.md): convert Markdown to/from Atlassian Document Format.

### azure-platform

Microsoft documentation, SDK reference, Azure CLI setup, authentication, and resource operation skills.

- [setup-cli](skills/azure-platform/setup-cli/SKILL.md) / [auth-principal](skills/azure-platform/auth-principal/SKILL.md): install/configure Azure CLI and authorize with a service principal.
- [query-azure](skills/azure-platform/query-azure/SKILL.md): discover, inspect, create, update, and delete Azure resources with `az`.
- [search-ms-docs](skills/azure-platform/search-ms-docs/SKILL.md): query official Microsoft documentation.
- [search-ms-code-samples](skills/azure-platform/search-ms-code-samples/SKILL.md): find working code samples and verify Microsoft SDK API signatures.

### learn-aws

AWS documentation skills for querying official AWS docs, API references, and regional availability.

- [search-aws-docs](skills/learn-aws/search-aws-docs/SKILL.md): understand AWS services and find API references from official docs.
- [search-aws-sdk-nuget](skills/learn-aws/search-aws-sdk-nuget/SKILL.md): AWS SDK for .NET NuGet package contract coverage — versions, APIs, signatures, upgrade guidance.

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
