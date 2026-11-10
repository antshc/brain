# Commits

Load [Commit messages](../references/commit-messages.md) for ordinary, ticket and squash conventions. Codey, Chore and the fallback worker read their caller-supplied history range oldest first.

## Execute

Drafting returns text. Read with `GIT_TOOL commit history --checkout ROOT [--base SHA --tip SHA] [--ccode]`. Commit only on explicit caller authorization with `GIT_TOOL commit create --checkout ROOT --expected SHA --message-file FILE -- PATHS...`. Supply exact repository-relative paths and require a clean staging area. Use returned head to verify publication.
