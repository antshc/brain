# Python implementation

Implement the work described by the user, specification, or tickets.

- Clarify the expected behavior and agree test seams before changing code.
- Use test-driven development where practical: add or update focused tests before the implementation.
- Run the relevant type checks and the focused test file regularly while working.
- Run the complete test suite after the change.
- Review the final diff for correctness, scope, regressions, and maintainability.
- Commit the completed, verified change to the current branch.

Use `python3` for Python commands. Prefer the repository's documented commands; otherwise use:

```sh
python3 -m pytest <focused-test-file> -v
python3 -m pytest tools/
```
