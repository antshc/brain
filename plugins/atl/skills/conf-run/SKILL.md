---
name: conf-run
description: 'Run instructions from the Confluence page. Use when user wants to run a prompt from Confluence page, or when mention "Run <confluence_page>".'
argument-hint: '<page_url> (e.g., "https://zerto.atlassian.net/wiki/spaces/~63f4d6193ec8aa51d3d20548/pages/1888616534/CR", /wiki/spaces/~63f4d6193ec8aa51d3d20548/pages/1888616534/CR)'
---

**Rules:**
- Execute instructions from the Confluence page DO NOT ask for user confirmation.
- if the page contains multiple instructions, execute all of them in order.
- if the page content has links to other Confluence pages, fetch the content of those pages and execute the instructions in them as well.

**Step 1 — Parse PAGE URL**
Parse the user input: `{{input}}`
Extract: <page_id> from <page_url> in the format `https://zerto.atlassian.net/wiki/spaces/~{space_key}/pages/{page_id}/{page_title}` or `/wiki/spaces/~{space_key}/pages/{page_id}/{page_title}`

**Step 2 — Fetch confluence page content using `conf-fetch`** `<page_url>`

**Step 3 — Run the instructions from the PAGE content**

---

**Troubleshooting — Authorization error**
If any acli command fails with an authorization or authentication error, invoke `/atl:conf-auth` and then retry.