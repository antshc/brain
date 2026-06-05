---
name: setup-atl
description: 'Set up all Atlassian (atl plugin) tooling on Windows or Linux. Installs acli, installs required Python packages, configures ACLI_API_TOKEN, ACLI_EMAIL, and ACLI_SITE, and authorizes with both Confluence and Jira. Use when acli is not installed, needs to be configured, or when mention "setup atl" or "setup acli".'
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
If acli is already installed, skip to **Step 2.5**.

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

**Step 2.5 — Install required Python packages (idempotent)**

Install packages from `requirements.txt`. pip skips already-satisfied packages automatically.

**Linux:**
```bash
pip3 install -r "$HOME/.copilot/installed-plugins/brain/atl/skills/setup-atl/requirements.txt"
```

**Windows (PowerShell):**
```powershell
pip install -r "$env:USERPROFILE\.copilot\installed-plugins\brain\atl\skills\setup-atl\requirements.txt"
```

**Step 3 — Collect credentials**

Skip this step if all three variables are already set:

Linux:
```bash
source ~/.profile 2>/dev/null || true
```

If any of `ACLI_API_TOKEN`, `ACLI_EMAIL`, or `ACLI_SITE` is empty, ask the user:
1. "Enter your Atlassian email address (e.g. user@example.com):" → store as `<email>`
2. "Enter your Atlassian site (e.g. <organization>.atlassian.net):" → store as `<site>`
3. "Enter your ACLI API token (from https://id.atlassian.com/manage-profile/security/api-tokens):" → store as `<token>`

If all three are already set, skip to **Step 5**.

**Step 4 — Persist environment variables (idempotent)**

**Linux** — only prepend if the export line is not already present in `~/.profile`:
```bash
if ! grep -q 'ACLI_API_TOKEN' ~/.profile 2>/dev/null; then
  { printf 'export PATH="$HOME/.local/bin:$PATH"\nexport ACLI_API_TOKEN="%s"\nexport ACLI_EMAIL="%s"\nexport ACLI_SITE="%s"\n\n' "<token>" "<email>" "<site>"; cat ~/.profile; } > /tmp/.profile.tmp && mv /tmp/.profile.tmp ~/.profile
fi
source ~/.profile
```

**Windows (PowerShell)** — only set if not already configured:
```powershell
if (-not [Environment]::GetEnvironmentVariable('ACLI_API_TOKEN', 'User')) {
    [Environment]::SetEnvironmentVariable('ACLI_API_TOKEN', '<token>', 'User')
    [Environment]::SetEnvironmentVariable('ACLI_EMAIL',     '<email>', 'User')
    [Environment]::SetEnvironmentVariable('ACLI_SITE',      '<site>',  'User')
}
# Also set for the current session
$env:ACLI_API_TOKEN = if ($env:ACLI_API_TOKEN) { $env:ACLI_API_TOKEN } else { '<token>' }
$env:ACLI_EMAIL     = if ($env:ACLI_EMAIL)     { $env:ACLI_EMAIL }     else { '<email>' }
$env:ACLI_SITE      = if ($env:ACLI_SITE)      { $env:ACLI_SITE }      else { '<site>' }
```

**Step 5 — Authorize Confluence and Jira (idempotent)**

Check if already authorized before running auth. If the check succeeds, skip the login:
```bash
# Confluence — only re-authorize if not already working
if ! acli confluence page list --limit 1 >/dev/null 2>&1; then
  if ! err=$(echo "$ACLI_API_TOKEN" | acli confluence auth login --token --email "$ACLI_EMAIL" --site "$ACLI_SITE" 2>&1); then
    echo "acli confluence auth login failed: $err"
  fi
fi

# Jira — only re-authorize if not already working
if ! acli jira workitem list --limit 1 >/dev/null 2>&1; then
  if ! err=$(echo "$ACLI_API_TOKEN" | acli jira auth login --token --email "$ACLI_EMAIL" --site "$ACLI_SITE" 2>&1); then
    echo "acli jira auth login failed: $err"
  fi
fi
```

**Step 6 — Verify**
```bash
acli confluence page list --space-key TEAM --limit 1
acli jira workitem list --limit 1
```
If both succeed, setup is complete. If either fails, check that `ACLI_API_TOKEN`, `ACLI_EMAIL`, and `ACLI_SITE` are set and re-run Step 5.
