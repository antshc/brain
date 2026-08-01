---
name: ralph-init
description: Use when explicitly asked to install and configure Ralph skills and agents in a repository.
disable-model-invocation: true
---

# Initialize Ralph

Run only when a person explicitly invokes this skill. Never run it as part of Codey or Chorey.

## Resolve target and source

Set `repositoryRoot` to the invocation directory and require it to be a Git repository root. Require `gh`; when it is unavailable, report it and stop without writing files.

Use `antshc/brain` as `sourceRepository`. Install skills in `$repositoryRoot/.github/skills` and agents in `$repositoryRoot/.github/agents`.

## Confirm configuration

Inspect `repositoryRoot` manifests, configuration, and documented commands to rank technologies. Propose `Senior <technology> developer` for the highest-ranked evidence; ask the user to choose when evidence ties, to provide a role when no technology is inferred, and to confirm the selected role. When declined, stop without writing files.

Present build-system evidence and ask whether to enable the early Build & LSP Check gate. Ask independently whether to enable Feedback. Do not infer either answer from evidence.

## Install selected resources

Always select `ralph-init`, `ralph-implement`, `ralph-gotchas`, and `ralph-chore`. Select `ralph-build` only when Build is enabled and `ralph-feedback` only when Feedback is enabled. Do not select `ralph-dev`, `ralph-fix`, `ralph-worktree`, `to-codey`, or `to-chorey`.

Create `$repositoryRoot/.github/skills` and `$repositoryRoot/.github/agents` when absent.

For each selected skill absent from `$repositoryRoot/.github/skills/<skillName>`, run:

```bash
gh skill install antshc/brain plugins/ralph/skills/<skillName> --agent github-copilot --dir "$repositoryRoot/.github/skills"
```

Never use `--force`. When a selected local skill already exists, preserve it and report it as unchanged.

For each absent agent, copy the initiating Ralph `codey.agent.md` and `chorey.agent.md` into `$repositoryRoot/.github/agents`. Preserve an existing local agent unchanged and report that it could not be configured.

## Configure new agents

Apply the following generated block to each newly created local agent after its title and before Workflow:

```md
<!-- ralph-init:persona:start -->
## Persona

**Expertise:** <role>

**Working style:** Be specific about expertise. Define the working style: concise, practical, and clear about assumptions, evidence, and verification.
<!-- ralph-init:persona:end -->
```

When Build is enabled, retain Codey's `ralph-init:build-*` blocks; otherwise remove both blocks and their markers. When Feedback is enabled, retain each agent's `ralph-init:feedback-*` blocks; otherwise remove those blocks and their markers. After each removal, renumber the local agent checklist consecutively.

## Configure selected skills

For every newly installed selected skill, follow its Initialize guidance. Inspect `repositoryRoot` before populating `CODE.md`, `FEEDBACK.md`, `CHORE.md`, or `BUILD.md`; use only repository-supported conventions and commands. Do not create `BUILD.md` unless Build is enabled. Do not infer Gotchas; `/ralph-gotchas` creates `GOTCHAS.md` on first use.

## Report

Emit: "Persona: [confirmed role]. Build: [enabled | declined]. Feedback: [enabled | declined]. Skills: [installed | preserved]. Agents: [created | preserved]. Guidance: [populated | defaults | preserved]. Omitted: [list]."

## Hard Rules

- Manual invocation only.
- Never overwrite or reconfigure an existing local Ralph skill, agent, or guidance file.
- Keep repository-specific detail in skill-owned guidance files, not in core Ralph skills or agents.