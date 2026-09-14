If the user prefixes a request with `proto!`, use the disposable prototype workflow.

1. Identify the single question the prototype must answer and the GitHub issue that owns it. If either is unclear, ask before coding.
2. Derive `<name>` from a lowercase, single-segment branch name: `proto/<name>`. Use only letters, numbers, `.\`, `_`, and `-` after `proto/`.
3. Create the branch and implement only the runnable experiment in `prototype/<name>/main.py`. Add `prototype/<name>/requirements.txt` only for dependencies required by that prototype.
4. Make the script print the question, the observed result, and a clear verdict. Keep it throwaway: no production abstractions or unrelated changes.
5. Commit and push the branch. Open a PR targeting `main`, linked to the owning issue.
6. Verify the `Prototype` GitHub Actions gate passes. Fix and push until it passes.
7. Publish a comment on the GitHub issue with the verdict and the validated, implementation-relevant code from the prototype. State how production implementation should use it.
8. Close the prototype PR without merging and delete the remote `proto/<name>` branch.
9. Close the issue only when the prototype fully resolves it and no production implementation is required. Otherwise leave it open for implementation.

## Atlassian integration checks

The prototype script runs in GitHub Actions. When its question requires verifying a real Atlassian operation, use the workflow credentials:

- `ATLASSIAN_EMAIL` — GitHub Actions secret.
- `ATLASSIAN_API_TOKEN` — GitHub Actions secret.
- `ATLASSIAN_SITE_URL` — GitHub Actions variable.

Read them from the environment. Use `curl` or an appropriate Python Atlassian client to perform the real operation, preferring read-only requests unless the prototype explicitly needs a write. Never print the secrets, authorization header, or complete environment. Print only redacted, useful evidence such as the endpoint path, HTTP status, and validated response fields.

The prototype workflow runs `prototype/<name>/main.py` based on the PR head branch name.
