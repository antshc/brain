# Repository

For checkout identity and remote verification, *use `git` skill for verified Git mechanics* using Repository. Resolve source and tracker independently. Stop on mismatch or ambiguity.

Use `repo read --repo OWNER/REPO [--ref SHA] [--path PATH]` for metadata, commits, and commit-pinned files. Use `repo search --repo OWNER/REPO QUERY` for candidate files, then confirm against a pinned commit. Preserve source URLs and lines. Require caller approval before an external-source edit.
