---
description: Use when explicitly asked to install and configure Ralph skills and agents in a repository.
disable-model-invocation: true
name: ralph-init
---
# Initialize Ralph

Run only when a person explicitly invokes this skill. Never run it as part of Codey or Chorey.

## Resolve target and source

Set `repositoryRoot` to the invocation directory and require it to be a Git repository root. Require `gh`; when it is unavailable, report it and stop without writing files.

Use `antshc/brain` as `sourceRepository`. Install skills in `$repositoryRoot/.github/skills` and agents in `$repositoryRoot/.github/agents`.

## Confirm configuration

Inspect `repositoryRoot` manifests, configuration, and documented commands to rank technologies. Propose `Senior <technology> developer` for the highest-ranked evidence; ask the user to choose when evidence ties, to provide a role when no technology is inferred, and to confirm the selected role. When declined, stop without writing files.

Present build-system evidence and ask whether to enable the early Build & LSP Check gate. Ask independently whether to enable Feedback. Do not infer either answer from evidence. These choices control agent and guidance configuration, not skill installation.

## Install selected resources

Always select every Ralph-plugin skill: `ralph-build`, `ralph-chore`, `ralph-dev`, `ralph-feedback`, `ralph-fix`, `ralph-gotchas`, `ralph-implement`, `ralph-init`, `ralph-worktree`, `to-chorey`, and `to-codey`.

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

For every newly installed selected skill, inspect its sibling `*.template.md` files after installation and follow its Initialize guidance. Select the template that matches the confirmed role and repository evidence; for example, select `CODE.skills.template.md` for skills, agents, and instruction work, or `CODE.<technology>.template.md` for a confirmed technology. When the canonical target guidance file named by the Initialize guidance is absent, copy the selected template to it; for example, both `CODE.skills.template.md` and `CODE.<technology>.template.md` produce `CODE.md`. Then add only repository-supported conventions and commands. Preserve a substantive existing guidance file unchanged. Do not create `BUILD.md` unless Build is enabled or `FEEDBACK.md` unless Feedback is enabled. Create `GOTCHAS.md` from its template without adding directives; `/ralph-gotchas` records grounded directives after use.

## Finalize configuration

After configuring a newly installed skill, delete its sibling `*.template.md` files only after its canonical guidance file has been created or preserved. Retain `ralph-build` or `ralph-feedback` templates when their respective gates are declined. Never delete templates from a preserved existing local skill.

## Report

Emit: "Persona: [confirmed role]. Build: [enabled | declined]. Feedback: [enabled | declined]. Skills: [installed | preserved]. Agents: [created | preserved]. Guidance: [populated | defaults | preserved]. Templates: [removed | retained]. Omitted: [list]."

## Hard Rules

- Manual invocation only.
- Never overwrite or reconfigure an existing local Ralph skill, agent, or guidance file.
- Keep repository-specific detail in skill-owned guidance files, not in core Ralph skills or agents.
