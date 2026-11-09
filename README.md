# Brain

My agent skills and plugins for GitHub Copilot — workflow automation, autonomous coding crews, PR review, and documentation lookups.

```sh
copilot plugin marketplace add antshc/brain
```

## Installation

### Install a plugin and configure a repository

Open Copilot CLI from the target repository. Use a separate Brain checkout as the installer source.

```sh
copilot --add-dir="/path/to/brain/plugins" \
  -i 'Follow /path/to/brain/plugins/wf/install/install.md in this repository.'
```

Replace `wf` with `crew`, `ms`, `ralph`, or `verify`. For Jira or Confluence setup, run `/atlassian install` after installing `wf@brain`. In an open Copilot session, use `/add-dir /path/to/brain/plugins` and ask Copilot to follow the matching installer by absolute path. The MS installer sets up Azure CLI and can run outside a repository. Each installer checks the plugin version against the source checkout before setup.

### Install only the plugins

Pick the plugin bundles you need. Each block uninstalls any stale version first, then installs the current one.

### Workflow plugins (wf, crew, ralph)

```sh
(copilot plugin uninstall wf@brain >/dev/null 2>&1 || true) && \
copilot plugin install wf@brain && \
(copilot plugin uninstall crew@brain >/dev/null 2>&1 || true) && \
copilot plugin install crew@brain && \
(copilot plugin uninstall ralph@brain >/dev/null 2>&1 || true) && \
copilot plugin install ralph@brain
```

<details>
<summary>Uninstall deprecated plugins</summary>

```sh
(copilot plugin uninstall review@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall droid@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall solution@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall learn-aws@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall aws-platform@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall azure-platform@brain >/dev/null 2>&1 || true) && \
(copilot plugin uninstall skill@brain >/dev/null 2>&1 || true)
```

</details>

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

### Brain engineering skills

```sh
gh skill install antshc/brain engineering/be-terse --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/suggest --agent github-copilot --scope user -f
gh skill install antshc/brain plugins/wf/install/assets/testing-integrations/SKILL.md --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/render-mermaid-png --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/suggest-graphify-improvements --agent github-copilot --scope user -f
gh skill install antshc/brain engineering/remove-zone-identifiers --agent github-copilot --scope user -f
```

Repo-level (run from the target repo; the WF installer offers it), then edit the copy to match the repo's conventions:

```sh
gh skill install antshc/brain plugins/wf/install/assets/factory-mode/SKILL.md --agent github-copilot --scope project
```

### Brain productivity skills

```sh
gh skill install antshc/brain productivity/skill-author --agent github-copilot --scope user -f
gh skill install antshc/brain productivity/doc-flow --agent github-copilot --scope user -f
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

Agent: [Codey](plugins/wf/agents/codey.agent.md) implements requested coding tasks. `implement` delegates tickets to `wf:codey`, with a `general-purpose` fallback.

- [diagnosing-bugs](plugins/wf/skills/diagnosing-bugs/SKILL.md): diagnose hard bugs or performance regressions, and fix them when explicitly requested.

Common everyday workflow automation skills. Expected to be useful to all developers.

- [design](plugins/wf/skills/design/SKILL.md): `grill` for decision interviews, `sketch` for a single-pass usage-first code sketch, `spec` for GitHub or offline specs, and `tickets` for approved implementation breakdowns, `wayfinder` for decision maps, and `review` for technical design review.
- [factory-mode Stories playbook](plugins/wf/install/assets/factory-mode/playbooks/stories.md): turn requirements, `/design spec` output, or feature design into an approved ordered story list, with numbered headings, dependencies, Jira metadata, and one `draft-artifact` Story run per row. Requires repo-level `factory-mode` installation.
- [draft-artifact](plugins/wf/skills/draft-artifact/SKILL.md): draft a User story, bug report, feature handover (TOI), or feature design.
- [github](plugins/wf/skills/github/SKILL.md): route Git conventions, branches, commits, owned worktrees, specs, issues, PRs, review discussions, and checks through one skill and CLI. Install WF for Factory Mode's GitHub routes.
- [implement](plugins/wf/skills/implement/SKILL.md): integrate the ticket graph sequentially or through parallel worktrees into a draft PR; hand off app verification and code review to factory mode.
- [doc-diagram](plugins/wf/skills/doc-diagram/SKILL.md): document architecture, behavior, or code structure as Mermaid diagrams and deltas.
- [doc-contracts](plugins/wf/skills/doc-contracts/SKILL.md): document contract deltas.
- [writing-style](plugins/wf/skills/writing-style/SKILL.md): write, review, or unslop prose; normalize requirement or story text by stripping implementation artifacts.
- [experiment](plugins/wf/skills/experiment/SKILL.md): run a throwaway experiment to answer a design question.
- [research](plugins/wf/skills/research/SKILL.md): investigate a question against primary sources and capture findings in the repo; inspects a system as-built along the behavior, flow, or data axis, cited to `file:line`, with diagrams; inspects AWS and Azure implementation constraints (APIs, SDK, IAM/RBAC, networking, quotas, retries, failures) from provider docs and read-only CLI into one shared template. Includes How for current behavior, Why for historical rationale, and Explore for inline read-only codebase and restored NuGet package lookups run inside a caller-spawned subagent (callers fall back to the explore agent when Research is unavailable).
- [subagents](plugins/wf/skills/subagents/SKILL.md): dispatch independent workers, select model roles, compare Arena candidates, and run Swarm partitions or races.
- [define-concept](plugins/wf/skills/define-concept/SKILL.md): suggest which Concept to add or extend (or check a described one against recorded Concepts), question it against cited codebase evidence, and record the result.
- [record-architecture](plugins/wf/skills/record-architecture/SKILL.md): record settled ADRs, Concepts, Deployables, deployment topology, or glossary terms; render concept bodies and compact decision bullets without saving. Select a mode explicitly or describe the artifact.
- [index-docs](plugins/wf/skills/index-docs/SKILL.md): initialize missing `ARCHITECTURE.md` and `GLOSSARY.md`, and maintain architecture indexes.
- [review](plugins/wf/skills/review/SKILL.md): use `code` for PR findings, `comments` for existing threads, `blast-radius` for downstream risk, `tests-gap` for regression coverage, `architecture` for drift, or `hitl` for human-led PR review.
- [WF installer](plugins/wf/install/install.md): one-time repo setup for GitHub issue labels and doc layout, and offers repo-level `factory-mode` install; labels-only mode repairs missing labels. Backlog skills bundle their own GitHub guidance; research and docs initialization remain local, and other skills retain their Jira workflows.

#### Atlassian

- [ATL installer](plugins/wf/skills/atlassian/references/install.md) (`/atlassian install`): first-run setup for a repo's Atlassian config, optionally generating `pub-<issue-type>` skills.
- [preflight-atlassian](plugins/wf/skills/atlassian/assets/preflight-atlassian/preflight-atlassian.SKILL.template.md): template copied by the ATL installer into `.github/skills/preflight-atlassian/`; resolves Atlassian connection facts before any Jira/Confluence operation, and owns locating/parsing the repo's Atlassian config file.
- [atlassian](plugins/wf/skills/atlassian/SKILL.md): one entry point for Jira and Confluence: fetch or publish a work item or page, address page review comments (targeted in-place edits plus a reply per thread), convert Markdown to/from ADF, and search or operate through twg. `/atlassian help` lists every tactic and command. Its `scripts/atl.py` CLI (`fetch-work`, `publish-work`, `fetch-page`, `publish-page`, `map-markdown`) runs from any working directory.

**Migration:** install or update `wf@brain` and remove any standalone `atlassian` copy. If you still use the retired plugin, run `copilot plugin uninstall atl@brain`. `fetch-work`, `publish-work`, `fetch-page`, `publish-page`, `map-markdown-adf`, `address-page-comments`, and `twg` are now tactics of the `atlassian` skill; old slash commands become requests to `/atlassian` (e.g. `/atlassian fetch PROJ-123`). `fix-confluence-comments` is retired: ordinary page edits use the Publish page tactic, review-thread replies the Address page comments tactic. `brief-daily` moved to the engineering skill [daily-briefing](skills/engineering/daily-briefing/SKILL.md). Scripts that called `plugins/atl/skills/<old-skill>/scripts/*.py` call `python3 plugins/wf/skills/atlassian/scripts/atl.py <command>` instead. Re-run `/atlassian install` to refresh `preflight-atlassian` and migrate generated `pub-*` wrappers.

### crew

Technology-agnostic autonomous coding crew (Codey, Chorey) and conventions.

Agents: [codey-py](plugins/crew/agents/codey-py.agent.md), [codey-dotnet](plugins/crew/agents/codey-dotnet.agent.md), [chorey](plugins/crew/agents/chorey.agent.md). Crew agents return gotchas in their reports.

- [to-crew](plugins/crew/skills/to-crew/SKILL.md): run the Codey subagent for an implementation task.
- [crew-commit](plugins/crew/skills/crew-commit/SKILL.md): commit staged/unstaged changes using the agent's status report.
- [chorey-diff](plugins/crew/skills/chorey-diff/SKILL.md) owns Chorey's commit/uncommitted review bundle, aggregate stack detection, and exact restoration mechanics; Chorey passes the manifest stacks to `/crew-chore` and owns behavior-preserving cleanup, scoped checks, the revert decision, and its status report.
- [Crew installer](plugins/crew/install/install.md): copy stack-specific Copilot instructions and install per-stack Chorey rules.

### ralph

AFK PR review and autonomous development loop.

- [dev](plugins/ralph/skills/dev/SKILL.md): pick the next open issue, implement it, and commit the result.
- [fix](plugins/ralph/skills/fix/SKILL.md): apply suggested changes from review comments.
- [create-worktree](plugins/ralph/skills/create-worktree/SKILL.md) / [delete-worktree](plugins/ralph/skills/delete-worktree/SKILL.md): create/reuse or remove an isolated git worktree per feature branch.
- [ralph-build](plugins/ralph/skills/ralph-build/SKILL.md): build the project in a worktree before implementation.
- [Ralph installer](plugins/ralph/install/install.md): copy the `harness` skill from template into `.github/skills/harness/`, ensure its settings file exists, and install its pull command.


### ms

Microsoft documentation, SDK reference, Azure CLI setup, authentication, and resource operation skills.

- [MS installer](plugins/ms/install/install.md) / [auth-principal](plugins/ms/skills/auth-principal/SKILL.md): install/configure Azure CLI and authorize with a service principal.
- [query-azure](plugins/ms/skills/query-azure/SKILL.md): discover, inspect, create, update, and delete Azure resources with `az`.
- [search-ms-docs](plugins/ms/skills/search-ms-docs/SKILL.md): query official Microsoft documentation.
- [search-ms-code-samples](plugins/ms/skills/search-ms-code-samples/SKILL.md): find working code samples and verify Microsoft SDK API signatures.

### aws

AWS documentation and SDK reference skills.

- [search-aws-docs](plugins/aws/skills/search-aws-docs/SKILL.md): understand AWS services and find API references from official docs.
- [search-aws-sdk-nuget](plugins/aws/skills/search-aws-sdk-nuget/SKILL.md): AWS SDK for .NET NuGet package contract coverage — versions, APIs, signatures, upgrade guidance.

### verify

Agent-driven proof of app behavior for TypeScript (pnpm) or Python repos: a `mole` CLI that drives the app in a real Chrome, receipts with a revision-bound verdict, web and API surface adapters, and feature maps.

- [Verify installer](plugins/verify/install/install.md): install the TypeScript or Python kit into a repo, research the codebase, ask which surfaces to prove (web, api, both), and generate starter cases plus repository-local `verify-<app>` and `maintain-verify-<app>` skills (the latter keeps maps, adapters and proofs honest as the app changes and re-proves on a fresh build).
- [playwright-cli](plugins/verify/skills/playwright-cli/SKILL.md): browser driving helper for ad-hoc exploration and Playwright tests.

### productivity

- [skill-author](skills/productivity/skill-author/SKILL.md): routes each request to a mode playbook. Grill interviews one question at a time to define purpose, triggers, contract, body blocks, and constraints, then hands the confirmed skill brief to write mode. Write drafts the skill (template with composable Workflow, Loop, Tactics, and Reference blocks) then shrinks it, each in a fresh subagent. Shrink only tightens existing skill, agent, or instructions files while preserving behavior. Agent writes or rewrites a custom coding agent, including planner agents. Manual-only.
- [doc-flow](skills/productivity/doc-flow/SKILL.md): draft or revise a workflow as compact numbered pseudocode with named subflows.

### engineering

General-purpose skills not tied to a specific platform.

- [be-terse](skills/engineering/be-terse/SKILL.md): rephrase or tighten a selection into terse, agent-optimized text.
- [suggest](skills/engineering/suggest/SKILL.md): analyze provided information and propose improvements with reasoning.
- [testing-integrations](plugins/wf/install/assets/testing-integrations/SKILL.md): select and run focused integration, functional-slice, and regression tests with evidence.
- [render-mermaid-png](skills/engineering/render-mermaid-png/SKILL.md): render Mermaid diagrams as high-resolution PNGs.
- [suggest-graphify-improvements](skills/engineering/suggest-graphify-improvements/SKILL.md): audit a Graphify knowledge graph and suggest evidence-backed improvements.
- [ask-dev](skills/engineering/ask-dev/SKILL.md): answer a manual tester's question about a codebase in black-box terms.
- [sync-skill](skills/engineering/sync-skill/SKILL.md): merge upstream skill improvements into a customized local copy.
- [remove-zone-identifiers](skills/engineering/remove-zone-identifiers/SKILL.md): delete Windows Zone.Identifier markers from the repo on any OS.
- [daily-briefing](skills/engineering/daily-briefing/SKILL.md): report your blocked Jira items and unanswered or answered @mentions; read-only. Requires the `atlassian` skill and its installer-generated `preflight-atlassian` skill.
- [factory-mode](plugins/wf/install/assets/factory-mode/SKILL.md): repo-level engineering instructions; restate the goal, route to a playbook, delegate, and verify on the real artifact. Installed per repo by the WF installer and customized by its users.
