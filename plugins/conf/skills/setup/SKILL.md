---
name: setup
description: 'Set up acli for Confluence on Windows or Linux. Installs acli, configures ACLI_API_TOKEN, ACLI_EMAIL, and ACLI_SITE, and authorizes with Confluence. Use when acli is not installed, needs to be configured, or when mention "setup conf".'
---

**Step 0 — Detect OS**
Run the following to detect the operating system:
```bash
uname -s 2>/dev/null
```
If the command fails or returns a Windows-like environment, treat it as **Windows** (PowerShell). Otherwise treat it as **Linux**.

**Step 1 — Check if acli is already installed**

Linux:
```bash
command -v acli
```
Windows (PowerShell):
```powershell
Get-Command acli.exe -ErrorAction SilentlyContinue
```
If acli is already installed, skip to **Step 3**.

**Step 2 — Install acli**

**Linux (x86-64):**
```bash
mkdir -p "$HOME/.local/bin"
curl -LO "https://acli.atlassian.com/linux/latest/acli_linux_amd64/acli"
chmod +x ./acli
mv ./acli "$HOME/.local/bin/acli"
# Add ~/.local/bin to PATH if not already present
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  export PATH="$HOME/.local/bin:$PATH"
fi
acli --version
```

**Windows (x86-64, PowerShell):**
```powershell
$binDir = "$env:USERPROFILE\bin"
if (-not (Test-Path $binDir)) { New-Item -ItemType Directory -Force -Path $binDir | Out-Null }
Invoke-WebRequest -Uri "https://acli.atlassian.com/windows/latest/acli_windows_amd64/acli.exe" -OutFile "$binDir\acli.exe"

# Add to user PATH for future sessions
$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
if ($currentPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable('PATH', "$currentPath;$binDir", 'User')
}
# Also add to the current session
$env:PATH += ";$binDir"

& "$binDir\acli.exe" --version
```

**Step 3 — Collect credentials**
Ask the user:
1. "Enter your Atlassian email address (e.g. user@example.com):" → store as `<email>`
2. "Enter your Atlassian site (e.g. <organization>.atlassian.net):" → store as `<site>`
3. "Enter your ACLI API token (from https://id.atlassian.com/manage-profile/security/api-tokens):" → store as `<token>`

**Step 4 — Persist environment variables**

**Linux** — prepend the four export lines (including PATH) to `~/.profile` (at the top, before existing content):
```bash
{ printf 'export PATH="$HOME/.local/bin:$PATH"\nexport ACLI_API_TOKEN="%s"\nexport ACLI_EMAIL="%s"\nexport ACLI_SITE="%s"\n\n' "<token>" "<email>" "<site>"; cat ~/.profile; } > /tmp/.profile.tmp && mv /tmp/.profile.tmp ~/.profile
source ~/.profile
```

**Windows (PowerShell)** — persist as user-scoped environment variables:
```powershell
[Environment]::SetEnvironmentVariable('ACLI_API_TOKEN', '<token>', 'User')
[Environment]::SetEnvironmentVariable('ACLI_EMAIL',     '<email>', 'User')
[Environment]::SetEnvironmentVariable('ACLI_SITE',      '<site>',  'User')
# Also set for the current session
$env:ACLI_API_TOKEN = '<token>'
$env:ACLI_EMAIL     = '<email>'
$env:ACLI_SITE      = '<site>'
```

**Step 5 — Authorize Confluence**
```bash
if ! err=$(echo "$ACLI_API_TOKEN" | acli confluence auth login --token --email "$ACLI_EMAIL" --site "$ACLI_SITE" 2>&1); then
  echo "acli confluence auth login failed: $err"
fi
```

**Step 6 — Verify**
```bash
acli confluence page list --space-key TEAM --limit 1
```
If this succeeds, setup is complete. If it fails, check that `ACLI_API_TOKEN`, `ACLI_EMAIL`, and `ACLI_SITE` are set and re-run Step 5.
