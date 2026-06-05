---
name: create-conf
description: 'Create a Confluence page from a local Markdown file. Use when user wants to publish a markdown file to Confluence, create a Confluence page from md, or mentions "conf-cpage".'
argument-hint: '<md_file_path> <parent_page_url> (e.g., "./docs/page.md https://<org>.atlassian.net/wiki/spaces/~.../pages/1234567/Title")'
---

**Step 1 — Parse input**
Parse the user input: `{{input}}`

Extract:
- `<md_file_path>`: the local path to the Markdown file
- `<parent_page_url>`: the full Confluence page URL in the format `https://<org>.atlassian.net/wiki/spaces/{space_key}/pages/{parent_page_id}/{title}`
  - Extract `<parent_page_id>` (numeric) from the URL
  - Extract `<space_key>` from the URL

**Step 2 — Ensure Confluence auth**
Invoke `conf-auth` to ensure credentials are loaded and valid.

**Step 3 — Create the Confluence page from the Markdown file**
Run:
```bash
source ~/.profile
python3 <skill-directory>/scripts/md_to_confluence.py \
  --file "<md_file_path>" \
  --parent-id "<parent_page_id>" \
  --space "<space_key>"
```
On success the script prints the URL of the newly created page.

---

**Troubleshooting — Authorization error**
If Step 3 fails with an authorization or authentication error, invoke `conf-auth` and then retry Step 3.
