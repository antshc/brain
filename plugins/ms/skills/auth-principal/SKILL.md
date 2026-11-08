---
name: auth-principal
description: >-
  Authorize Azure CLI with a service principal on Windows or Linux. Use when az authentication is missing or expired, 'az login fails', or for /ms:auth-principal.
---

**Step 0 — Detect OS**
Run `uname -s 2>/dev/null`. If it fails or returns a Windows-like environment, use the Windows steps. Otherwise use the Linux steps.

**Step 1 — Check credentials in the current environment**

Linux:
```bash
for variable in AZURE_CLIENT_ID AZURE_CLIENT_SECRET AZURE_TENANT_ID AZURE_SUBSCRIPTION_ID; do
  if [[ -z "${!variable}" ]]; then
    echo "$variable is not set. Set it locally or follow Brain's plugins/ms/install/install.md in Copilot CLI."
    exit 1
  fi
done
```

Windows (PowerShell):
```powershell
$requiredVariables = 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID', 'AZURE_SUBSCRIPTION_ID'
foreach ($variable in $requiredVariables) {
    if ([string]::IsNullOrWhiteSpace((Get-Item "Env:$variable" -ErrorAction SilentlyContinue).Value)) {
        throw "$variable is not set. Set it locally or follow Brain's plugins/ms/install/install.md in Copilot CLI."
    }
}
```

**Step 2 — Log in and configure defaults**

Linux:
```bash
if ! az login --service-principal \
  --username "$AZURE_CLIENT_ID" \
  --password "$AZURE_CLIENT_SECRET" \
  --tenant "$AZURE_TENANT_ID" \
  --output none 2>/dev/null; then
  echo 'az login failed.'
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

Windows (PowerShell):
```powershell
az login --service-principal --username $env:AZURE_CLIENT_ID --password $env:AZURE_CLIENT_SECRET --tenant $env:AZURE_TENANT_ID --output none 2>$null
if ($LASTEXITCODE -ne 0) { throw 'az login failed.' }
az config set defaults.subscription=$env:AZURE_SUBSCRIPTION_ID
if ($LASTEXITCODE -ne 0) { throw 'az config set subscription failed.' }
az config set defaults.location=westeurope
if ($LASTEXITCODE -ne 0) { throw 'az config set location failed.' }
```

**Step 3 — Verify**
```bash
az account show
```