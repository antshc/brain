# Branches

- Use `feat/<slug>` for planned changes, including docs, maintenance, and refactoring. Use `fix/<slug>` to correct a defect.
- Derive a short slug from the work summary. Use lowercase ASCII letters, digits, and single hyphens. Omit initiative and ticket IDs, including any prefixed to the summary. Ask for a usable summary if no slug remains.
- For a parallel worker, append `-worker-02` with the caller's stable run-local ordinal. The caller records the mapping before launch.
- Return a candidate. The caller validates it with Git and checks local and remote collisions before use. On collision, the caller can authorize a unique run suffix or verify ownership for resume.
- Existing PRs and resumed runs use the exact recorded refs, including legacy names.
