# Source playbooks

The `why/why.md` procedure spawns one investigator per available evidence category, each reading a single source-specific playbook below. The playbooks cover common MCPs and the installed Atlassian skills. Adapt the examples for other providers in the same category.

| Category | Playbook | Provider it documents |
|---|---|---|
| Source control history | `why/sources/code-archaeology.md` | git, `gh` |
| Issue / ticket tracker | `why/sources/atlassian.md` (Jira procedure) | `preflight-atlassian` + `twg` skills; Rovo, then JQL |
| Issue / ticket tracker | `why/sources/linear.md` | Linear (adapt for Jira, GitHub Issues, Plane, Shortcut) |
| Long-form documents | `why/sources/atlassian.md` (Confluence procedure) | `preflight-atlassian` + `twg` skills; Rovo, then CQL |
| Long-form documents | `why/sources/notion.md` | Notion (adapt for Confluence, Google Docs, Coda) |
| Real-time team chat | `why/sources/slack.md` | Slack (adapt for Discord, Microsoft Teams, Mattermost) |
| Infrastructure observability | `why/sources/datadog.md` | Datadog (adapt for New Relic, Honeycomb, Grafana, Splunk) |
| Error / exception tracking | `why/sources/sentry.md` | Sentry (adapt for Rollbar, Bugsnag, Airbrake) |
| Product analytics warehouse | `why/sources/databricks.md` | Databricks SQL (adapt for Snowflake, BigQuery, ClickHouse, dbt) |

Cross-cutting:

- `why/sources/incident-postmortem.md`. Add this if the target code looks defensive (null checks, retry, timeout, rate limit, feature flag, egress guard, OOM handler).
