## Deterministic Source Repository development — 2026-07-31
- **category**: other
- **severity**: note
- **problem**: MEMORY.md is absent from the harness droid configuration.
- **context**: .droid/MEMORY.md
- **workaround**: Continued with no guardrails recorded.

## Deterministic Source Repository development — 2026-07-31
- **category**: tool-access
- **severity**: note
- **problem**: The mandatory Explore subagent was unavailable in this invocation.
- **context**: droid-implement Explore delegation
- **workaround**: Performed the required local implementation and convention review directly.

## Repository-tailored Droid setup — 2026-07-31
- **category**: other
- **severity**: note
- **problem**: MEMORY.md is absent from the harness droid configuration.
- **context**: .droid/MEMORY.md
- **workaround**: Continued with no guardrails recorded.

## Repository-tailored Droid setup — 2026-07-31
- **category**: tool-access
- **severity**: note
- **problem**: GitHub GraphQL lookup for the dependency issue timed out during the TLS handshake.
- **context**: gh issue view 67 --repo antshc/brain
- **workaround**: Used the local Droid guidance history and task requirements to confirm the ownership model.

## Retire harness discovery — 2026-07-31
- **category**: directory-access
- **severity**: note
- **problem**: Terminal commands defaulted to the source checkout rather than the task worktree.
- **context**: /home/pet/_projects/afk/brain.worktrees/main_droid
- **workaround**: Prefixed every subsequent command with an explicit worktree `cd`.

## Retire harness discovery — 2026-07-31
- **category**: tool-access
- **severity**: note
- **problem**: Content-free apply_patch delete directives reported success but left harness files in place.
- **context**: plugins/harness
- **workaround**: Deleted the explicitly retired directory with `rm -rf` and verified its absence.