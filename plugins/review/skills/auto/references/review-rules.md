# Shared Review Rules

These rules apply to **every** review axis. They govern how findings are grounded, scoped, and deduplicated — independent of which quality attribute or
smell an axis is looking for.

- Review the changes as a whole, including cross-symbol behavior and the likely design intent.
- Do not report speculative issues. Report only findings supported by specific code evidence.
- Treat existing review comments as already-covered review context for deduplication. Do not restate or rephrase them.
- Do not re-open the same finding unless the current diff introduces materially new evidence, a different root cause, or a broader impact that was not previously reported.
- Report only net-new, actionable findings that are not already covered by existing review comments.
