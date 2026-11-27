# Why

Route procedure for historical rationale: why code, a constraint, or a workaround exists; what led to a change. Answer from the record, not the code: the commits and PR discussions that introduced the target and each later change, then linked Jira and Confluence when that trail is thin. Cite what the authors wrote, mark inferences as inferences, and say what the record does not answer. Spawns `whyy` (anchor, then one per source). Paths resolve from the skill base directory.

## Conditional resources

| Trigger | Resource |
|---|---|
| Source control investigator, including the anchor | `why/sources/code-archaeology.md` |
| Jira or Confluence investigator | `why/sources/atlassian.md` (that product's procedure) |

## Workflow

1. **Target.** Name the target (code, pattern, feature, decision) and the question. Vague → best guess from conversation context; state it so the requester can redirect. *Done when* target and question are explicit.
2. **Anchor.** Spawn one `whyy` with Investigator brief, source = source control, task = build the anchor: files and line ranges, key symbols, recent commits touching the target, PR numbers from merge subjects, linked work item IDs, and the substantive PR bodies and discussion via *Load and follow the `github` skill to read pull requests in read-only mode and review threads*. Start from any PR or commit the caller supplied. At anchor depth, deliver the anchor and stop. *Done when* the anchor is cited or its gaps are named.
3. **Investigate.** Spawn in one parallel batch, each with Investigator brief, the anchor, and its source resource:
   - **Source control** — deeper history per `code-archaeology.md`. Always.
   - **Jira** and **Confluence** — when the `preflight-atlassian` and `atlassian` skills are installed: *Load and follow the `preflight-atlassian` skill to resolve the credentialed atl launcher and site* using **Resolve** once; pass launcher and site to both. `tokenAvailable` false or launcher/site missing → mark both inaccessible with the exact prerequisite; never read credentials, start login, or switch identity.

   Then dispatch Jira → Confluence and Confluence → Jira follow-ups with the other's Additional Leads, scoped to the receiving product. *Done when* every investigator returned findings, a null result, or a blocker.
4. **Present.** Merge investigator outputs per Report, with light edits only: keep each claim's tier label and confidence wording; merge duplicate citations; keep contradictions with both sources. Synthesize only evidence the investigators supplied; every inference traces to cited evidence. A deciding citation in doubt or a material gap → one bounded `whyy` follow-up in the owning source, never direct source reading. Apply Delivery. *Done when* the report pointer is returned.

## Investigator brief

Fill the placeholders; send this section, the anchor, and the source resource path as the worker prompt. One source per worker.

> {QUESTION}

- Anchor — files and lines {FILES_WITH_LINE_RANGES}; symbols {SYMBOLS}; commits {COMMIT_LIST}; PRs {PR_NUMBERS}; work items {WORK_ITEM_IDS}; unknown → `to be built`.
- Source — {SOURCE_NAME}; read {SOURCE_RESOURCE} in full.
- Task — {TASK}

**Investigate** as a careful, precise investigator; boring and exact beats plausible.

1. Cast a wide net, then narrow.
2. Read each PR, work item, doc, or thread in full; key evidence hides in comments and follow-ups.
3. Follow links within your source only; record other-source links under Additional Leads.
4. Quote verbatim with exact location (PR #, work item key, URL, commit, `file:line`), author, and date.
5. Record every query, including empty ones; an empty search is a finding.
6. Record disagreeing items side by side; a contradiction is often the key finding.

Mechanics are not motivation: a diff shows what changed, not why. Claim intent only where an author stated it; never cite code as evidence of its own intent. Treat a hypothesis in the question as a candidate. Never round a partial finding up.

**Tier every claim**; the tier sets phrasing:

- **Direct** — an author explicitly wrote why. Confident, cited.
- **Supported** — several indirect items converge. Cite each item.
- **Inferred** — reasoning from evidence, no statement. Hedge (`likely`, `suggests`) and show the chain.
- **Speculative** — plausible, weakly backed. Mark as speculation.
- **Unknown** — searched, not found. Name what was searched.

**Return** inline: Source · What I searched · Findings by tier (quote, location, author/date, relevance; alternative readings for Inferred) · Contradictions · Gaps · Additional Leads.

## Report

Question · Code in question (paths, lines, symbols) · What we found (Direct, Supported) · What we can reasonably infer (Inferred, hedged, with chain) · Competing hypotheses (when evidence fits several) · What we don't know · Sources consulted (one line per source, including empty, inaccessible, and not searched: Slack, observability, error tracking, analytics) · Confidence summary. Question precedes a change → add Preserve / Change / Avoid / Risk constraints.

## Gotchas

- **Recency bias.** The latest commit is rarely the origin; trace back to the change that introduced the shape.
