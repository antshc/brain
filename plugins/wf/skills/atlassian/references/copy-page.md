# Copy page

Clone one page body and required attachments into another existing page:

```bash
<atl> copy-page <source-page> --to-page <target-page> [--title "<target-title>"] [--work-dir <dir>]
```

Source and target accept numeric IDs or standard Confluence `/pages/<id>` URLs on the configured site. The target must be a different page.

Clone policy:

- source inline-comment text stays, but `adf:comment` IDs are removed; footer comments are not copied;
- table layout and compatible widths come from the source, not the destination; ambiguous row-specific widths warn and use defaults;
- missing or failed required attachment/media retrieval blocks the copy;
- the target's current title stays unless `--title` is supplied;
- source ADF-to-Markdown conversion warnings or unresolved `adf:error` nodes block publication;
- existing target comment anchors removed by the replacement may be reported by the publish comment guard.

After publish, semantic ADF/title verification runs automatically. Work files stay in `--work-dir` or `tmp/atl-copy-<source>-to-<target>` for diagnosis; report the final URL only after verification passes.
