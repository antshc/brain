# Review Comment Template

Use this template for every review comment. Keep it actionable and grounded in code evidence.

## Accepted Labels

- **bug:** definite correctness or compatibility issue
- **suggest:** improvement or likely risk worth fixing
- **nit:** minor note or polish

## Comment-Writing Rules

- `COMMENT_BODY` write concise, terse comment text following the tone guidelines in `Tone of Voice in Code Reviews` from `<skill-directory>/references/tone.md`.
- `FILE_PATH` must be the repo-relative file path exactly as it appears in the diff header.
- `LINE_NUMBER` must be the new-file line number of the most relevant changed line on the right side of the diff.
- For multi-line ranges, use the last line of the relevant changed range.
- Omit the snippet for `nit` comments.

## Template

```
FILE_PATH: <repo-relative file path>
LINE_NUMBER: <new-file line number>
COMMENT_BODY: <label>: <clear statement of the issue>. <why it matters>. <minimal change requested>.
```

Optional minimal snippet:

````language
<tiny inline snippet or diff showing the smallest safe fix>
````


