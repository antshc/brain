# Repository Adapter Skill

## Purpose

A skill installed at plugin or user level offers one workflow to every repository it runs in, but a single
repository often needs that workflow pre-bound to its own data — required fields, keys, paths — before it is
usable without repeating that data on every call. Hardcoding one repository's binding into the shared skill
couples it to that repository; copying the workflow into a repository-local skill drifts the moment the shared
skill changes. This Concept fixes how a repository-scoped skill is generated to close that gap without either
failure.

## Rules

- A generated repository-level skill MUST resolve only this repository's bound data (fields, keys, paths) and
  invoke the owning user-level skill's documented action with it.
- A generated repository-level skill MUST NOT reimplement, inline, or fork the owning skill's procedure.
- A generated repository-level skill MUST live under the repository's own skill folder (e.g. `.github/skills/`),
  never inside the plugin or skill that generated it.
- A setup skill that scaffolds a repository-level adapter MUST discover the repository-bound data live, from the
  target system or repository, rather than hardcoding it into the generated file.
- A setup skill MUST ask before overwriting an existing generated adapter skill.

## Design Guidance

Three participants: a **setup skill** that scaffolds the adapter (e.g. `init-atl`), the **generated adapter
skill** it writes into the repository (e.g. `pub-<issue-type>`), and the **owning user-level skill** that performs
the actual action (e.g. `publish-work`). The extension point is the setup skill's discovery step: it enumerates
the repository- or target-specific variants live (e.g. Jira issue types configured for this project) and offers
to generate one adapter per variant, rather than shipping a fixed set.

Trigger → interactions → outcome: the user asks the generated adapter to act; the adapter gathers only the values
its pre-filled fields still need, then invokes the owning skill's documented action with the resolved arguments;
the owning skill performs the workflow exactly as it would for any other caller. The adapter carries no fallback
path that runs the action itself.

Apply this pattern whenever the same shared workflow is called from many repositories with different bound
parameters, and generating a thin per-repository skill is cheaper than asking the user to restate the same
parameters on every invocation. Skip it when the bound data never repeats across calls, or when a single config
file read by the shared skill already carries it — see
[Per-Repo Config Resolution](ops-per-repo-config-resolution.md) for that case.

## Violation signals

- A generated repository-level skill containing the owning skill's full procedure instead of a call to it.
- A generated skill hardcoding values that could have been discovered live from the target system.
- A generated skill placed inside the generating plugin's or skill's own folder instead of the repository's.
- A setup skill silently overwriting a previously generated adapter.

## Examples

- `init-atl`'s generated `pub-<issue-type>` skills (e.g. `pub-bug`, `pub-story`), each pre-filled with this
  repository's required Jira fields and invoking `/publish-work` to perform the actual creation.

## Consequences

- The shared workflow changes once, in the owning skill; every repository's adapter calls current behavior
  without being regenerated.
- Each repository accumulates a small number of thin, low-maintenance skills instead of duplicated logic, at the
  cost of one extra file per bound variant.
