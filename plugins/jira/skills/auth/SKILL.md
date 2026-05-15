---
name: auth
description: 'Authorize acli with Jira. Use when acli Jira auth is missing or expired, or when mention "jira-auth".'
---

**Step 1 — Load credentials**
```bash
source ~/.profile
if [[ -z "$ACLI_API_TOKEN" ]]; then
  echo "ACLI_API_TOKEN is not set. Run /jira:setup first."
  exit 1
fi
```

**Step 2 — Authorize Jira**
```bash
if ! err=$(echo "$ACLI_API_TOKEN" | acli jira auth login --token --email "$ACLI_EMAIL" --site "$ACLI_SITE" 2>&1); then
  echo "acli jira auth login failed: $err"
fi
```
