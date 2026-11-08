# Commits

Use `type(scope): imperative summary` for ordinary commits. Scope is optional. Use lowercase type and scope. Choose the type from the actual change, such as `feat`, `fix`, `docs`, `refactor`, `test`, or `chore`. Keep meaningful rationale or evidence in the body. For breaking changes, preserve the `BREAKING CHANGE:` footer.

For an authorized WF ticket commit, use `ccode(<INITIATIVE_ID> <owner/repo#number>): <summary>`. Record changed paths, decisions, verification, and risks in the body. Codey, Chore, and the fallback worker match subjects with `^ccode\([^)]*\):` and read their caller-supplied history range oldest first.

For a squash commit, use the conventional subject from the PR title after removing the leading initiative marker. Retain breaking-change footers when applicable.
