---
name: conf-fetch
description: 'Fetch confluence page content. Use when mention "Fetch <confluence_page_url>".'
argument-hint: '<page_url> (e.g., "https://zerto.atlassian.net/wiki/spaces/~63f4d6193ec8aa51d3d20548/pages/1888616534/CR", /wiki/spaces/~63f4d6193ec8aa51d3d20548/pages/1888616534/CR)'
---

**Step 1 — Parse PAGE URL**
Parse the user input: `{{input}}`
Extract: <page_id> from <page_url> in the format `https://zerto.atlassian.net/wiki/spaces/~{space_key}/pages/{page_id}/{page_title}` or `/wiki/spaces/~{space_key}/pages/{page_id}/{page_title}`

**Step 2 — Fetch PAGE content**
Run the following command to fetch the page content in markdown format:
```
page_json=$(acli confluence page view --id <page_id> --body-format view --json)
python3 <skill-directory>/scripts/page_view_json_to_markdown.py "$page_json"
```