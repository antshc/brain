# Cross-Scope Skill Family

## Purpose

An orchestrator skill that scans only its own plugin's folder for `skillname-*` extension members cannot be
extended by a skill someone adds locally in their repository or user scope — the new member stays invisible until
it is registered inside the plugin that ships the orchestrator. This Concept fixes where a `skillname-*` family's
members may live and how an orchestrator finds them, so extension never requires editing the orchestrator itself.

## Rules

- An orchestrator skill's `skillname-*` discovery MUST scan the complete available skill roster — plugin-installed,
  user-level, and repository-level (e.g. `.github/skills/`) — not only its own plugin's skills folder.
- An orchestrator skill MUST select a family member by its declared description and compatibility, never by a
  hardcoded list of names.
- A repository- or user-scoped skill joining a family MUST use the exact `skillname-*` naming convention and MUST
  declare any tool or server compatibility it depends on.
- An orchestrator MUST report when the best-matching member declares a compatibility requirement (tool or server)
  unavailable in the current session, rather than silently skipping it.

## Design Guidance

Three participants: the **orchestrator (main) skill** that owns the family name and the routing/continuation
logic; the **family members**, each named `skillname-*` and self-contained with its own procedure and contract;
and the **available skill roster**, which spans every scope Copilot loads skills from — plugin-installed,
user-level, and repository-level. The extension point is the naming convention alone: adding a new member is
adding a skill file matching the pattern, in any scope, with no edit to the orchestrator.

Trigger → interactions → outcome: the orchestrator receives a task; it scans the roster for names matching its
declared family prefix; it judges each candidate's `description` (and `compatibility` line, where present)
against the task; one match runs via its documented action, several matches each run over the part they own, and
no match falls through to the orchestrator's own generic handling where one exists.

Apply this pattern whenever a shared orchestrator's behavior should grow through independently added skills rather
than through edits to the orchestrator — including additions made outside the plugin that ships it. This is the
cross-scope reading of the same naming convention that [Skill Composition](structure-skill-composition.md)
establishes for same-scope specialist families; that Concept owns division and call style in general, this one
owns where a family's members are allowed to live and how discovery reaches across scope boundaries.

## Violation signals

- An orchestrator's routing logic lists specific skill names instead of a naming pattern plus a roster scan.
- A repository-added skill matching the family's naming pattern is never selected because discovery is scoped to
  one folder or plugin.
- Two skills across scopes silently duplicate the same specialization instead of one being chosen or one
  superseding the other.
- A missing tool/server dependency for the best-matching member is skipped without being reported.

## Examples

- `/research`'s discovery of `research-*` and `inspect-*` specialists from the roster, regardless of which plugin
  or repository defines them.

## Consequences

- A user can extend a shared orchestrator's behavior locally, inside their own repository, without touching the
  plugin that ships the orchestrator.
- Two same-named families defined in different scopes could collide; naming discipline (a unique family prefix)
  is the only guard against that collision.
