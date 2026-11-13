# Resource Access Skill

## Purpose

A feature skill that needs infrastructure — a ticket tracker, a docs backend, an external API — risks coupling
its callers directly to a specific vendor or tool. A Resource Access Skill encapsulates access to one category
of infrastructure, similar to the iDesign Resource Access layer, so the backend can be replaced without
affecting its callers.

## Rules

- These rules apply when a workflow uses a swappable Resource Access Skill. The explicitly GitHub-native wf backlog workflow follows the exception below.
- A Resource Access Skill MUST own all vendor-specific knowledge for its infrastructure category — commands,
  IDs, formats.
- Vendor-specific knowledge for that category MUST NOT appear in a caller.
- An action MUST document the values it reads and what it returns.
- An action's inputs MUST be read as `{{placeholder}}` variables already present in the caller's context, not
  declared as a formal call-site argument list.
- The skill's set of actions MUST stay stable when its backend is swapped.

## Design Guidance

Direct use of the underlying infrastructure tool is still allowed; what is barred is a caller inlining that
command *in place of* a skill reference it is otherwise making. The call style itself is owned by
[0010](0010-skill-composition.md).

Swapping a backend — GitHub → Jira, local files → a wiki — rewrites the skill's internals only. Callers and
their invocation style stay unchanged, which is the whole return on the encapsulation.

## Exceptions

- **GitHub-native WF backlog.** [GitHub](../../plugins/wf/skills/github/SKILL.md) owns the shared operation routes and CLI. Design retains separate publication policy for Spec, Tickets, and Wayfinder. The [WF installer](../../plugins/wf/install/install.md) supplies the baseline label manifest and uses the same CLI. Callers may direct users to labels-only setup for missing labels.
- `research` and the `record-architecture` **Initialize missing docs** action remain local-document workflows with no backlog operations. Explicit offline spec/ticket Markdown output is a publication fallback, not a local tracker backend; report it separately from successful GitHub publication. Other wf skills' Jira metadata/workflows and `atl` remain outside this exception.
- `trigger-indexer` writes directly to the file containing an index table (e.g. `ARCHITECTURE.md`), even when that file is otherwise owned by another Resource Access Skill (`manage-docs`). It is not itself an instance of this Concept — there is no swappable vendor backend involved, only index-table mechanics — so this carve-out does not weaken the Concept's ownership boundary for any other file content.
