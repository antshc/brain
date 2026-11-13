# Branch naming

- A workflow may supply an explicit valid prefix; use it with the same slug and availability rules. Otherwise use the defaults below.
- Planned changes, including docs, maintenance, and refactoring: `feat/<slug>`. Defects: `fix/<slug>`.
- Derive a short slug from the work summary. Use lowercase ASCII letters, digits, and single hyphens. Remove initiative and ticket IDs, even when they prefix the summary. Ask for a usable summary if no slug remains.
- Parallel workers append a caller-assigned stable run-local ordinal, e.g. `-worker-02`; the caller records the mapping before launch.
- Check local and remote availability. On collision, require caller authorization for suffix or verified resume.
- Existing PRs and resumes retain recorded names, including legacy forms.
