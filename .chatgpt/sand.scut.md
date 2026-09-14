If the user prefixes a request with `sand!`, use the disposable sandbox workflow.

1. Identify the single question the sandbox must answer and the GitHub issue that owns it. If either is unclear, ask before coding.
2. Select the repository-relative Python file to run. It must end in `.py` and not contain `..`.
3. Create the branch `sand/<relative-path-to-python-file>` and implement only the runnable experiment at that path.
4. Make the script print the question, the observed result, and a clear verdict. Keep it throwaway: no production abstractions or unrelated changes.
5. Commit and push the branch. Open a PR targeting `main`, linked to the owning issue.
6. Verify the `Sandbox` GitHub Actions gate passes. Fix and push until it passes.
7. Publish a comment on the GitHub issue with the verdict and the validated, implementation-relevant code from the sandbox. State how production implementation should use it.
8. Close the sandbox PR without merging and delete the remote `sand/<relative-path-to-python-file>` branch.
9. Close the issue only when the sandbox fully resolves it and no production implementation is required. Otherwise leave it open for implementation.

The sandbox workflow runs the Python file whose repository-relative path follows `sand/` in the PR head branch name.
