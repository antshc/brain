---
name: wi-fetch
description: 'Fetch Jira work item content. Use when mention "Fetch <jira_wi_url>".'
argument-hint: '<jira_wi_url> (e.g., "https://<organization>.atlassian.net/browse/<wi_key>")'
---

**Step 1 — Parse JIRA Work Item URL**
Parse the user input: `{{input}}`
Extract: <wi_key> from <jira_wi_url> in the format `https://<organization>.atlassian.net/browse/<wi_key>`

**Step 2 — Fetch JIRA Work Item content**
Run the following command to fetch the work item content in markdown format:
```
wi_json=$(acli jira workitem view <wi_key> -f summary,description --json)
python3 <skill-directory>/scripts/wi_json_to_markdown.py "$wi_json"
```

---

**Troubleshooting — Authorization error**
If the acli command fails with an authorization or authentication error, invoke `/atl:jira-auth` and then retry.