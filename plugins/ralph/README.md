# ralph plugin

## Initialization

Install the `ralph-init` skill before using it in a repository:

```bash
gh skill install antshc/brain plugins/ralph/skills/ralph-init --agent github-copilot --dir .github/skills
```

Then open the repository in VS Code and run `/ralph-init` from its Git root.

Run `/ralph-init` from a Git repository root with `gh` available. It confirms a technology-specific persona, independently offers Build and Feedback, installs selected skills in `.github/skills`, and creates Codey and Chorey in `.github/agents`.

Core installation contains `ralph-init`, `ralph-implement`, `ralph-gotchas`, and `ralph-chore`; Build adds `ralph-build` and Feedback adds `ralph-feedback`. Initialization never overwrites an existing local Ralph skill, agent, or guidance file.


## Agents

### `codey`

Autonomous implementation agent. It works only in its invocation directory, uses the persona confirmed by `/ralph-init`, and reports `STATUS`, `SUMMARY`, `FILES`, `GOTCHAS UPDATED`, and `NOTES`.

### `chorey`

Maintainability reviewer. It uses the persona confirmed by `/ralph-init`, verifies current uncommitted work before review, applies behavior-preserving refactors only when justified, and re-verifies only after edits.

## Skills

| Skill | Description |
|---|---|
| `/to-codey <task>` | Run Codey directly for one task |
| `/to-chorey` | Review current uncommitted work with Chorey |
| `/ralph-init` | Install and configure selected Ralph skills, agents, and skill-owned guidance in a repository |
| `/ralph-build` | Run initialized `BUILD.md` guidance when the Codey BUILD gate is enabled |
| `/ralph-feedback` | Run initialized changed-file checks from `FEEDBACK.md` |
| `/ralph-gotchas` | Initialize `GOTCHAS.md` on first use and maintain grounded reusable directives |
| `/ralph-chore` | Review changes using initialized `CHORE.md` rules |
| `/ralph-dev` | AFK loop that invokes Codey then Chorey |
| `/ralph-fix` | Apply PR review comments |
| `/ralph-worktree` | Prepare a deterministic worktree and use Codey for merge conflicts |

## `/ralph-dev` workflow

`/ralph-dev <milestone-title>` creates an isolated feature worktree, processes one eligible issue per iteration, and opens a draft pull request after every eligible issue is handled. Issues labeled `spec` or `hitl` are never implemented.

```mermaid
flowchart TD
	%% resolve: extracts Feature ID and Target Branch from the milestone description
	start[Milestone] --> resolve[Resolve branch name]
	resolve --> worktree[Create worktree]
	worktree --> state[Read state and select issue]
	state --> codey[Codey agent]
	codey --> complete[Codey complete]
	codey --> incomplete[Codey partial or blocked]
	complete --> chorey["Chorey agent (optional)"]
	incomplete --> outcome[Use Codey outcome]
	chorey --> outcome
	outcome --> publish[Commit and push changes]
	publish --> issue[Update spec and handle issue]
	issue --> remaining[Eligible issues remain]
	issue --> done[No eligible issues remain]
	remaining --> state
	done --> pr[Create draft PR]
```

### Codey agent

```mermaid
flowchart TD
	input[Confirm invocation directory] --> gotchas[Read gotchas]
	gotchas --> build["Build and LSP check (optional)"]
	build --> implement[Implement task]
	implement --> feedback["Run feedback checks (optional)"]
	feedback --> update[Update gotchas]
	update --> report[Five-field outcome]
```

### Chorey agent

```mermaid
flowchart TD
	input[Confirm invocation directory] --> gotchas[Read gotchas]
	gotchas --> verify[Verify current changes]
	verify --> review[Review and refactor]
	review --> changed[Edits made]
	review --> unchanged[No edits made]
	changed --> reverify[Reverify edits]
	unchanged --> report[Five-field outcome]
	reverify --> report
```
