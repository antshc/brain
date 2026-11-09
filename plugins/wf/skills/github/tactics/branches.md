# Branches

- Use `feat/<slug>` for planned changes, including docs, maintenance, and refactoring. Use `fix/<slug>` to correct a defect.
- Derive a short slug from the work summary. Use lowercase ASCII letters, digits, and single hyphens. Omit initiative and ticket IDs, including any prefixed to the summary. Ask for a usable summary if no slug remains.
- For a parallel worker, append `-worker-02` with the caller's stable run-local ordinal. The caller records the mapping before launch.
- Return a candidate. The caller validates it with Git and checks local and remote collisions before use. On collision, the caller can authorize a unique run suffix or verify ownership for resume.
- Existing PRs and resumed runs use the exact recorded refs, including legacy names.

## Execute

Use `branch inspect/create/fetch/push/delete --help` through `GH_TOOL`. Use an absolute checkout. For fetch and push, verify the named remote belongs to the qualified repository. Fetch a full commit SHA. Push a verified local branch head with its recorded previous remote SHA or `absent`. Reconcile a lost push response by rereading the remote. Delete a local branch only after the caller authorizes cleanup and its recorded tip is reachable from the supplied integration SHA.
