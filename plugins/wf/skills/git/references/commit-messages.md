# Commit messages

- Ordinary: `type(scope): imperative summary`, scope optional. Type and scope are lowercase. Use `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, or another meaningful type.
- Keep rationale and evidence in the body. Preserve `BREAKING CHANGE:` footers.
- Authorized WF ticket commit: `ccode(<INITIATIVE_ID> <owner/repo#number>): <summary>`. Record paths, decisions, verification and risks in body. Workers recognize subjects with `^ccode\([^)]*\):`.
- Squash: conventional PR title without leading `[INITIATIVE_ID]` marker. Preserve breaking-change footer.
- *Apply `writing-style` skill to write PR descriptions and commit messages* using **Write a PR description or commit message** to prose without changing required subject.
