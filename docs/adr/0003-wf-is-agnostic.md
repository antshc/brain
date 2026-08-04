# wf plugin is operating-system-agnostic

`wf` skills must not embed OS-specific shell syntax (bash-only or PowerShell-only) in their commands or helper scripts. Wherever a skill needs logic beyond a bare cross-platform CLI invocation (e.g. `gh`, `git`), that logic is written in Python so the same instruction runs unmodified on Linux, macOS, and Windows, instead of asking the agent to pick and maintain a per-OS variant.

## Considered Options

- **Parallel bash and PowerShell variants per snippet** (status quo, e.g. `to-tickets`'s repo-parsing snippet) — rejected: doubles the surface to keep in sync and silently drifts when only one variant is updated.
- **Bash-only scripts** (status quo, e.g. `manage-backlog/scripts/create-labels.sh`) — rejected: fails on Windows without a POSIX shell, contradicting `wf`'s use across arbitrary caller environments.
- **Python** — accepted: a single script or inline snippet executes identically across OSes without requiring a POSIX shell or PowerShell host.
