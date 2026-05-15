---
name: auth-principal
description: 'Authorize az with Azure using a Service Principal. Use when Azure CLI auth is missing or expired, or when mention "/az:auth-principal".'
---

**Step 1 — Load credentials**
```bash
source ~/.profile
if [[ -z "$AZURE_CLIENT_ID" ]]; then
  echo "AZURE_CLIENT_ID is not set. Run /az:setup-cli first."
  exit 1
fi
if [[ -z "$AZURE_CLIENT_SECRET" ]]; then
  echo "AZURE_CLIENT_SECRET is not set. Run /az:setup-cli first."
  exit 1
fi
if [[ -z "$AZURE_TENANT_ID" ]]; then
  echo "AZURE_TENANT_ID is not set. Run /az:setup-cli first."
  exit 1
fi
if [[ -z "$AZURE_SUBSCRIPTION_ID" ]]; then
  echo "AZURE_SUBSCRIPTION_ID is not set. Run /az:setup-cli first."
  exit 1
fi
```

**Step 2 — Login with Service Principal**
```bash
if ! err=$(az login --service-principal \
  -u "$AZURE_CLIENT_ID" \
  -p "$AZURE_CLIENT_SECRET" \
  -t "$AZURE_TENANT_ID" \
  --output none 2>&1); then
  echo "az login failed: $err"
  exit 1
fi
if ! err=$(az config set defaults.subscription="$AZURE_SUBSCRIPTION_ID" 2>&1); then
  echo "az config set subscription failed: $err"
  exit 1
fi
if ! err=$(az config set defaults.location=westeurope 2>&1); then
  echo "az config set location failed: $err"
  exit 1
fi
```

**Step 3 — Verify**
```bash
az account show
```
