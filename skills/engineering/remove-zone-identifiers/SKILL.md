---
name: remove-zone-identifiers
description: Remove Windows Zone.Identifier files and streams from a repo. Use when asked to delete, clean, or purge Zone.Identifier, `:Zone.Identifier`, or "mark of the web" artifacts, on any OS.
disable-model-invocation: true
---
# Remove zone identifiers

Delete all Windows `Zone.Identifier` markers (files named `*:Zone.Identifier`, or NTFS alternate streams on Windows) from the repo working tree, using whatever tools suit the current OS.

- List matches first, then delete. Done when a re-check finds none.
- Skip `.git/`; delete only `Zone.Identifier` markers, nothing else.
- Do not commit unless asked.
- Report the count removed.
