# Review Comment Template

Use this template for every review comment. Keep it actionable and grounded in code evidence.

## Template

```
FILE_PATH: <repo-relative file path>
LINE_NUMBER: <new-file line number>
COMMENT_BODY: <label> <clear statement of the issue>. <why it matters>. <minimal change requested>.
```

Optional minimal snippet:

````language
<tiny inline snippet or diff showing the smallest safe fix>
````

## Accepted Labels

- **bug:** definite correctness or compatibility issue
- **suggest:** improvement or likely risk worth fixing
- **nit:** minor note or polish

## Comment-Writing Rules

- Ground every comment in verified code evidence, not guesswork.
- Prefer one concrete finding per comment.
- State the impact in practical terms.
- Use the narrowest fix that solves the problem.
- `FILE_PATH` must be the repo-relative file path exactly as it appears in the diff header.
- `LINE_NUMBER` must be the new-file line number of the most relevant changed line on the right side of the diff.
- For multi-line ranges, use the last line of the relevant changed range.
- Omit the snippet for `nit` comments.
- Maintain a direct and professional tone — see `<skill-directory>/references/tone.md`.

## Review Guidance

Good review comments include:
- the exact problem
- the concrete impact
- the smallest reasonable fix
- optional test guidance only when coverage is materially missing

Avoid:
- speculative concerns without code evidence
- style-only feedback unless explicitly requested
- broad redesign advice when a local fix is enough
- combining multiple unrelated issues into one comment

If the evidence is weak or the right fix is unclear, ask follow-up questions before posting. If the concern still cannot be verified, do not draft or post a review comment.
