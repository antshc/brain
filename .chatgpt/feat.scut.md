If the user prefixes a request with `feat!`, use the feature-branch workflow:

1. Run the `github` **Name branch** tactic. Verify and create the resulting `feat/` or `fix/` branch.
2. Implement using `dev!`. Use the `github` **Draft commit** tactic for the implementation commit, then push.
3. Run the `github` **Draft PR** tactic with the verified head, base `main`, and initiative ID. Resolve a missing ID before opening the pull request.
4. Validate the pull request 'Python tests' gate github action pass.
5. Fix the problems.
