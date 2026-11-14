# Why

Rationale procedure of the Research skill. Paths resolve from the skill base directory.

Investigate the motivation and intent behind code. How explains current behavior. `why` answers what forces led to its shape.

At each dispatch, *load and follow the `subagents` skill to dispatch independent workers using role-based models and isolated outputs* using **Dispatch**. Use `general-purpose` with read-only instructions for MCP access and citation spot-checks. Use the role fallback on rejection, then the closest valid model of the same family.

## Operating Posture

Operate as a **careful, cautious, and precise investigator**. Be honest about what you know vs what you're inferring. Apply the loaded Epistemics confidence framework and phrasing guide. The synthesizer must follow it.

## Step 1. Understand the Target and the Question

The **target** is usually a chunk of code, a pattern, a feature, or a named design decision. The **question** is usually a design rationale, a tradeoff, a motivating edge case, an external constraint, dead code, or a broad history sweep.

If the target is vague ("why do we do it this way?" with no clear referent), make your best guess from conversation context (open files, recent edits, cursor location, what was just discussed). State your interpretation briefly so the user can redirect if you're off, then proceed.

## Step 2. Establish the Code Anchor

Dispatch one read-only worker with the `why investigators` role to build the seed context: file paths and line ranges, key symbols (functions, classes, constants), the last few commits touching the target, PR numbers from merge commits (pattern `(#1234)` in the subject line), and any linked ticket IDs. Run `git blame -L <start>,<end> <file>` for last-touch commits, `git log --follow -p -- <file>` for full history with patches through renames, `git log --oneline -20 -- <file>` for recent commits with PR numbers visible, and `git log -1 --format=%B <commit>` to extract PR numbers. Then pull the PR bodies and discussion for any substantive commit: *Load and follow the `github` skill to read pull requests in read-only mode and review threads* using Pull requests with the qualified PR, retaining body and discussion. Start with any PR or commit explicitly supplied by the caller. Return the cited anchor and any access gaps. For the Why code anchor action, stop here. For full Why, pass the anchor to every investigator and the synthesizer.

## Step 3. Spawn Parallel Investigators

**Default to the full parallel investigation.** The goal is a complete coverage map, not a minimal one. Document the null, don't skip the search.

### Discovery

Before spawning investigators, list the MCP servers and installed skills available in this session (the `github-mcp-server-*`, other MCP tools, and skill names your tool list shows). Read names and descriptions, not credential or config files.

Map available evidence providers to these categories:

1. Source control history
2. Issue / ticket tracker
3. Long-form documents
4. Real-time team chat
5. Infrastructure observability
6. Error / exception tracking
7. Product analytics warehouse

Use local Git for source history; *Load and follow the `github` skill to inspect repositories in read-only mode and pull requests* for remote source and PR evidence. For the other six, classify using MCP names, server instructions, tool names, skill descriptions, and resource descriptors. If a provider fits more than one category, choose its primary evidence, except for the Atlassian pair below. Record ambiguous cases in the coverage map.

When both `preflight-atlassian` and `atlassian` skills are installed, *Load and follow the `preflight-atlassian` skill to resolve the credentialed TWG launcher and site* using **Resolve** once. Use its credentialed `twg` launcher and site in two independent investigators: **Jira** for issue / ticket tracker, **Confluence** for long-form documents. Both use `why/sources/atlassian.md` with their own category's procedure. If `tokenAvailable` is false or the site/launcher is unavailable, mark both categories inaccessible with the exact prerequisite; never read credentials, start login, or silently switch identity. Do not spawn a second provider for either category. If the skills are absent, retain ordinary MCP discovery for those categories.

Spawn one investigator per category with an available provider, all in a single message so they run concurrently, each owning one category and one provider. Atlassian's credentialed launcher may be shared by its Jira and Confluence investigators, but each must search and report only its assigned product. Don't ask one investigator to cover multiple categories or MCPs. `model`: the `why investigators` role.

Each investigator's prompt is `why/investigator-prompt.md` filled in, plus:
- the category playbook `why/sources/<source>.md` for the selected provider, adapted from the examples in `why/source-playbook.md`
- `why/sources/incident-postmortem.md` **if the target code looks defensive** (null checks, retry logic, timeout handling, rate limiting, feature flags, egress guards, OOM handlers)
- the code anchor and the user's original question

After the initial results, dispatch targeted Jira-to-Confluence and Confluence-to-Jira follow-ups with the earlier findings and relevant links, scoped to the receiving product. Keep each finding under its owning category; do not duplicate evidence.

### Investigator roster, one per available evidence category

Each category below is uniquely positioned to surface one shape of "why", shown after "Best at". Use it to know what to expect back, to name a gap when a category returns empty, and, only in the rare provably-irrelevant case, to justify a skip.

1. **Source control** (git history, `gh` for PRs, code comments, tests). Always spawn, the only guaranteed source. Best at *implementation-time rationale captured during review*.
2. **Issue / ticket tracker** (e.g. Atlassian `twg`/Jira, Linear, GitHub Issues, Plane, Shortcut MCP). Best at *the product or business forcing function*. Strongest when the why is external to engineering.
3. **Long-form documents** (e.g. Atlassian `twg`/Confluence, Notion, Google Docs, Coda MCP). Best at *long-form design rationale*, written out before it becomes code.
4. **Real-time team chat** (e.g. Slack, Discord, Microsoft Teams, Mattermost MCP). Best at *real-time deliberation that never reached a doc*. Especially important when the source control, ticket, and doc paper trail is thin.
5. **Infrastructure observability** (e.g. Datadog, New Relic, Honeycomb, Grafana, Splunk MCP). Best at *infrastructure and runtime reality that motivated the code*. Strongest when the target reacts to an infra signal (timeouts, retries, rate limits, circuit breakers).
6. **Error / exception tracking** (e.g. Sentry, Rollbar, Bugsnag, Airbrake MCP). Best at *the specific exceptions and error trajectories that motivated defensive or corrective code*. Strongest for catch blocks, null guards, type checks, retries, and other defenses.
7. **Product analytics warehouse** (e.g. Databricks, Snowflake, BigQuery, ClickHouse, dbt, Redshift MCP). Best at *product and data reality that shaped the code*. Strongest for flag-gated code, experiment-driven ships, data migrations, and "where did this number come from" questions.

### When to skip an investigator

Only with an **explicit, written justification** that goes in the final Sources Consulted. Two valid reasons:

- **No matching provider is available for that category**, or its required credentials are unavailable. Flag it as a gap, not a choice: "Real-time team chat skipped. No matching MCP available, so the conversational record was not searchable."
- **The source is provably irrelevant**, not just "probably irrelevant." A high bar: "Error / exception tracking skipped. Target is a build-time script with no runtime code path."

If your scope assessment suggests a single-commit trivial target where the PR description already contains the complete answer, you may answer inline **only after** confirming all seven available category searches would be redundant. Say so explicitly. This should be rare.

## Step 4. Synthesize

Spawn one synthesizer. `model`: the `why synthesizer` role. It gets:
1. The investigator findings, including any null results and any categories skipped with justification
2. The code anchor
3. The user's original question
4. The epistemics framework from `why/epistemics.md`
5. The synthesizer prompt template from `why/synthesizer-prompt.md`

## Step 5. Present

Return the synthesizer's output inline to Research for coordinator delivery under Caller-owned destinations. You may lightly edit for clarity or add context from the conversation, but **do not rewrite the confidence language**.

## Output Format

The structure is the one in `why/synthesizer-prompt.md`: The Question, The Code in Question, What We Found, What We Can Reasonably Infer, Competing Hypotheses, What We Don't Know, Sources Consulted, Confidence Summary. Adapt as needed, but keep the confidence separation intact, and keep Sources Consulted as one line per investigator, including the ones that returned nothing or were skipped, with the reason.

After Sources Consulted, if the user's `why` question is a precursor to changing this code, convert the lineage findings into a Preserve / Change / Avoid / Risk constraint set for planning the change.

## Common Failure Modes to Avoid

- **Recency bias**. Assuming the most recent commit is authoritative. The current shape is often the accretion of many earlier decisions. Trace back.
