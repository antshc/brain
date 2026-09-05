# Requirements-coverage Review Guidance

Evaluate the change against the spec identified in Step 4. Ground every conclusion in the spec text and specific code evidence (not the patch alone). If no spec was found, report "no spec available" and stop.

## What to report

- **Missing or partial** — requirements from the spec that the diff does not fully implement.
- **Scope creep** — behavior in the diff that no requirement asked for.
- **Implemented but wrong** — requirements that appear implemented but do not match the spec's intent.

Quote the spec line for each review comment.

## LSP workflow for this axis

**Baseline** Enumerate all changed symbols from the diff. Include changed types, methods, properties, fields, interfaces, records, and constructors. Keep this shallow; use this map as the spine for the reachability checks below.

**Trace each requirement:**

- **Implemented & reachable** — for each requirement, "jump to the symbol's definition" + "search for all references to the symbol" to confirm the required behavior exists and is referenced, not dead or unreferenced code.
- **Scope creep** — invert the map: flag any changed symbol that **no requirement maps to** as candidate scope creep.
- **End-to-end path** — where a requirement spans multiple symbols, follow "trace the outgoing calls from the symbol"/"trace the incoming calls into the symbol" to confirm the full behavior path exists from entry point to effect.

**Depth rule.** Trace only far enough to confirm each requirement is implemented, reachable, and wired; stop once reachability is established. Prefer representative call paths over exhaustive expansion of the call graph.

For each review comment, conclude one of: **confirmed issue**, **plausible risk**, or **no issue found**.

## Review rules

These rules govern how review comments are grounded, scoped, and deduplicated:

- Review the changes as a whole, including cross-symbol behavior and the likely design intent.
- Do not report speculative issues. Report only review comments supported by specific code evidence.
- Treat existing review comments as already-covered review context for deduplication. Do not restate or rephrase them.
- Do not re-open the same review comment unless the current diff introduces materially new evidence, a different root cause, or a broader impact that was not previously reported.
- Report only net-new, actionable review comments that are not already covered by existing review comments.

## Evidence anchor

Internal grounding only — used to confirm the review comment, never emitted or placed in `REVIEW_COMMENT`. For this axis, the evidence anchor is: **the quoted spec line the review comment maps to**.

## Output

Emit each review comment as a JSON array of objects.
- Each object MUST represent one issue.
- The array MUST contain at most five objects.
- Output MUST contain JSON only, with no Markdown fences, prose, or unresolved placeholders.
- Results SHOULD order `suggest` before `nit`, then by file and line.
- Emit `[]` when no actionable, net-new issue is found.

```json
[{
  "AXIS": "requirements-coverage",
  "FILE_PATH": "<from the diff; repo-relative header path>",
  "LINE_NUMBER": "<from the diff (new-file line on the right side; last line of a multi-line range). These anchor the review comment to the pull-request change; the LSP trace grounds the conclusion but is never the anchor.>",
  "LABEL": "<missing, implemented-but-wrong, plausible risk, or scope creep → `suggest`>",
  "REVIEW_COMMENT": "<the LABEL value>: <a self-contained review comment that quotes the spec requirement and states the gap and fix — formatted via `/to-review-comment`>"
}]
```
