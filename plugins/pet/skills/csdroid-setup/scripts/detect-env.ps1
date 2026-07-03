#!/usr/bin/env pwsh
# Detect CSDROID_HARNESS_ROOT and CSDROID_WORKSPACE_ROOT and persist them to
# "$(git rev-parse --show-toplevel)/.csdroid.env" as export lines.
# Idempotent: if the env file already exists, load it and skip detection.
$ErrorActionPreference = "Stop"

$EnvFile = Join-Path (git rev-parse --show-toplevel) ".csdroid.env"

if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^export (\w+)="?(.*?)"?$') { Set-Item "Env:$($Matches[1])" $Matches[2] }
  }
  Write-Output "CSDROID_HARNESS_ROOT=$Env:CSDROID_HARNESS_ROOT"
  Write-Output "CSDROID_WORKSPACE_ROOT=$Env:CSDROID_WORKSPACE_ROOT"
  Write-Output "(existing .csdroid.env - skipped detection)"
  exit 0
}

# Harness root: main working tree of the current repo, then climb to the outermost repo.
$CsdroidHarnessRoot = (Resolve-Path (Join-Path (git rev-parse --git-common-dir) "..")).Path
while ($parent = (git -C (Join-Path $CsdroidHarnessRoot "..") rev-parse --show-toplevel 2>$null)) { $CsdroidHarnessRoot = $parent }

# Workspace root: the workspace/ source repo if present, else the harness root.
$workspace = Join-Path $CsdroidHarnessRoot "workspace"
if ((Test-Path $workspace) -and (git -C $workspace rev-parse --show-toplevel 2>$null)) {
  $CsdroidWorkspaceRoot = (git -C $workspace rev-parse --show-toplevel)
} else {
  $CsdroidWorkspaceRoot = $CsdroidHarnessRoot
}

@(
  "export CSDROID_HARNESS_ROOT=`"$CsdroidHarnessRoot`""
  "export CSDROID_WORKSPACE_ROOT=`"$CsdroidWorkspaceRoot`""
) | Set-Content -Path $EnvFile

Write-Output "CSDROID_HARNESS_ROOT=$CsdroidHarnessRoot"
Write-Output "CSDROID_WORKSPACE_ROOT=$CsdroidWorkspaceRoot"
