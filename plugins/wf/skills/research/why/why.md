# Why

Investigate historical motivation directly in this agent. How explains current behavior; Why answers what forces led to its shape. Apply Research's Read-only contract, Caller-owned destinations and loaded Epistemics. Mechanics are not motivation; preserve confidence language. Trace history beyond the last-touch commit when earlier decisions matter; recency alone does not establish rationale.

## Understand the Target and the Question

Identify files, symbols, decision/pattern and requested rationale. If vague, state a bounded interpretation from supplied context and proceed. Done when target and question are explicit.

## Establish the Code Anchor

Use Local search for locally available files and refs. Build seed context: paths/lines, symbols, recent commits, PR numbers and linked tickets. Run `git blame -L <start>,<end> <file>`, `git log --follow -p -- <file>`, `git log --oneline -20 -- <file>` and `git log -1 --format=%B <commit>` as relevant. Begin with supplied commits/PRs. *Load and follow the `github` skill to read pull requests in read-only mode and review threads* using Pull requests; retain substantive PR bodies and discussion. Remote PR/ticket discussion establishes historical context, never substitutes for missing local implementation evidence.

For `@whyDepth=anchor`, return the cited anchor and gaps; stop before category investigation. Full Why retains the anchor for all subsequent searches. Done when anchor is cited or missing prerequisites are named.

## Investigate evidence categories

Discover available MCP tools and installed skills by names/descriptions; never inspect credentials or config files. Map providers to seven categories below. Choose one primary provider per category; record ambiguous classifications. Use local Git for source history and authorized GitHub access for PR discussion. An unavailable source does not block other categories.

When both Atlassian skills are installed, *Load and follow the `preflight-atlassian` skill to resolve the credentialed TWG launcher and site* using Resolve once. Search Jira and Confluence as separate categories using the same credentialed launcher and the registered Atlassian procedures. Missing token/site/launcher → both inaccessible with exact prerequisite; never start login, read credentials or silently switch identity. Otherwise discover providers normally.

For each available category, apply the Source investigation checklist and selected source playbook registered in Research. Search directly; independent queries may run together, with separate category evidence notes. Defensive code → apply Incident postmortems checks inside each relevant source. Collect null results and exact queries. Follow cross-source leads in a subsequent pass under the receiving category, including Jira-to-Confluence and Confluence-to-Jira links. Deduplicate evidence.

### Coverage roster

1. **Source control** (git history, `gh` for PRs, code comments, tests). Always check local history; unavailable history is an explicit gap. Best at *implementation-time rationale captured during review*.
2. **Issue / ticket tracker** (e.g. Atlassian `twg`/Jira, Linear, GitHub Issues, Plane, Shortcut MCP). Best at *the product or business forcing function*. Strongest when the why is external to engineering.
3. **Long-form documents** (e.g. Atlassian `twg`/Confluence, Notion, Google Docs, Coda MCP). Best at *long-form design rationale*, written out before it becomes code.
4. **Real-time team chat** (e.g. Slack, Discord, Microsoft Teams, Mattermost MCP). Best at *real-time deliberation that never reached a doc*. Especially important when the source control, ticket, and doc paper trail is thin.
5. **Infrastructure observability** (e.g. Datadog, New Relic, Honeycomb, Grafana, Splunk MCP). Best at *infrastructure and runtime reality that motivated the code*. Strongest when the target reacts to an infra signal (timeouts, retries, rate limits, circuit breakers).
6. **Error / exception tracking** (e.g. Sentry, Rollbar, Bugsnag, Airbrake MCP). Best at *the specific exceptions and error trajectories that motivated defensive or corrective code*. Strongest for catch blocks, null guards, type checks, retries, and other defenses.
7. **Product analytics warehouse** (e.g. Databricks, Snowflake, BigQuery, ClickHouse, dbt, Redshift MCP). Best at *product and data reality that shaped the code*. Strongest for flag-gated code, experiment-driven ships, data migrations, and "where did this number come from" questions.

### Skips and gaps

Default to complete category coverage. Skip only with an explicit reason in Sources Consulted: no accessible matching provider/credentials, or provably irrelevant (e.g. runtime exceptions for a build-only script). Missing local checkout/history is a source gap; do not infer absence or clone/fetch. A trivial target may stop early only after establishing that all remaining category searches are redundant; state the reason for each.

Done when each of the seven categories has findings, a searched-empty result, or a justified gap/skip.

## Synthesize

Apply the registered Why report directly to category notes, anchor, original question and loaded Epistemics. Reconcile overlaps, spot-check citations, surface contradictions and competing hypotheses; never invent intent from code. Verify unclear citations directly before relying on them. Done when every rationale claim has an evidence tier and appropriate wording.

## Present

Apply Caller-owned destinations. Preserve The Question, The Code in Question, What We Found, What We Can Reasonably Infer, Competing Hypotheses, What We Don't Know, Sources Consulted and Confidence Summary as applicable. Sources Consulted has one row per category, including nulls/skips with reasons. A precursor to changing code additionally derives Preserve / Change / Avoid / Risk constraints. Done when rationale, confidence and coverage are explicit.

Last, sweep the original question against the anchor, all seven categories and report; resolve missing obligations or name their consequence and exact next check.
