---
name: setup-cli
description: 'Set up Azure CLI on Windows or Linux. Installs az, configures AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, and AZURE_SUBSCRIPTION_ID, and authorizes with Azure. Use when az is not installed, needs to be configured, or when mention "setup az".'
---

**Step 0 — Detect OS**
Run the following to detect the operating system:
```bash
uname -s 2>/dev/null
```
If the command fails or returns a Windows-like environment, treat it as **Windows** (PowerShell). Otherwise treat it as **Linux**.

**Step 1 — Check if az is already installed**

Linux:
```bash
command -v az
```
Windows (PowerShell):
```powershell
Get-Command az -ErrorAction SilentlyContinue
```
If az is already installed, skip to **Step 3**.

**Step 2 — Install az**

**Linux:**
```bash
curl -fsSL 'https://azurecliprod.blob.core.windows.net/$root/deb_install.sh' | sudo bash
```

**Windows (PowerShell):**
```powershell
winget install --exact --id Microsoft.AzureCLI
```
> After installation on Windows, close and reopen any active terminal window before continuing.

**Step 3 — Verify installation**
```bash
az --version
```

**Step 4 — Collect credentials**
Ask the user:
1. "Enter your Azure Client ID (Service Principal App ID):" → store as `<client-id>`
2. "Enter your Azure Client Secret:" → store as `<client-secret>`
3. "Enter your Azure Tenant ID:" → store as `<tenant-id>`
4. "Enter your Azure Subscription ID:" → store as `<subscription-id>`

**Step 5 — Persist environment variables**

**Linux** — append the four export lines to `~/.profile`:
```bash
cat >> ~/.profile << 'EOF'

export AZURE_CLIENT_ID="<client-id>"
export AZURE_CLIENT_SECRET="<client-secret>"
export AZURE_TENANT_ID="<tenant-id>"
export AZURE_SUBSCRIPTION_ID="<subscription-id>"
EOF
```

**Windows (PowerShell)** — persist as user-scoped environment variables:
```powershell
[Environment]::SetEnvironmentVariable('AZURE_CLIENT_ID',       '<client-id>',       'User')
[Environment]::SetEnvironmentVariable('AZURE_CLIENT_SECRET',   '<client-secret>',   'User')
[Environment]::SetEnvironmentVariable('AZURE_TENANT_ID',       '<tenant-id>',       'User')
[Environment]::SetEnvironmentVariable('AZURE_SUBSCRIPTION_ID', '<subscription-id>', 'User')
# Also set for the current session
$env:AZURE_CLIENT_ID       = '<client-id>'
$env:AZURE_CLIENT_SECRET   = '<client-secret>'
$env:AZURE_TENANT_ID       = '<tenant-id>'
$env:AZURE_SUBSCRIPTION_ID = '<subscription-id>'
```

**Step 6 — Reload profile**

Linux:
```bash
source ~/.profile
```

**Step 7 — Authorize**
Run `/azure-platform:auth-principal` skill.