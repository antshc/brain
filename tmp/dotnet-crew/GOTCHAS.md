# MEMORY

<!-- Read-only guardrails, loaded by droid-memory during GUARDRAILS. Curated by a human from recurring entries in .droid/LOG.md — never written to by the agent itself. -->

## Guardrails

<!-- One directive per line, distilled from .droid/LOG.md. Example shape (replace with real, curated guardrails): -->
<!-- - <directive> -->

## Gotchas

- New `.cs` files created via the file-creation tool land as UTF-8 (no BOM) with LF line endings, but zerto-zic requires UTF-8-with-BOM + CRLF — after creating any new `.cs` file, convert it (`sed -i 's/\r$//' f; sed -i 's/$/\r/' f; printf '\xEF\xBB\xBF' | cat - f > f.tmp && mv f.tmp f`) and verify with `head -c3 f | od -An -tx1` (expect `ef bb bf`).
- `grep_search` scoped with an `includePattern` ending in `/**` has produced false-negative (empty) results on files that do contain the searched text (seen on a `.csproj`'s `InternalsVisibleTo` `AssemblyAttribute` item, and separately on a large CFN JSON file) — treat an empty scoped `grep_search` result as unproven; re-run unscoped or with a terminal `grep -rn` before concluding "not found".
- In this bash environment, `!` inside a double-quoted string (e.g. an xUnit `--filter "Category!~X"` expression) triggers bash history expansion ("event not found") even though the shell is non-interactive-looking — run `set +H` as its own prior command in the terminal session before any command containing `!` in a filter/query string.
