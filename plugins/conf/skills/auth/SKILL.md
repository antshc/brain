---
name: auth
description: 'Authorize acli with Confluence. Use when acli Confluence auth is missing or expired, or when mention "conf-auth".'
---

**Step 1 — Load credentials**
```bash
source ~/.profile
if [[ -z "$ACLI_API_TOKEN" ]]; then
  echo "ACLI_API_TOKEN is not set. Run /conf:setup first."
  exit 1
fi
```

**Step 2 — Authorize Confluence**
```bash
if ! err=$(echo "$ACLI_API_TOKEN" | acli confluence auth login --token --email "$ACLI_EMAIL" --site "$ACLI_SITE" 2>&1); then
  echo "acli confluence auth login failed: $err"
fi
```
