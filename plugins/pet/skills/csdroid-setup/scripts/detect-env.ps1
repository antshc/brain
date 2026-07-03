#!/usr/bin/env pwsh
# Detect CSDROID_HARNESS_ROOT and CSDROID_WORKSPACE_ROOT and persist them to
# "$CsdroidHarnessRoot/.csdroid.env" as export lines.
# Works from the harness root, the workspace source repo, or any of their worktrees.
# Idempotent: if the env file already exists, load it and skip detection.
$ErrorActionPreference = "Stop"

# Main working tree of the current repo (resolves through linked worktrees).
$CurrentMain = (Resolve-Path (Join-Path (git rev-parse --git-common-dir) "..")).Path

# Harness root: climb from the current repo to the outermost enclosing repo.
$CsdroidHarnessRoot = $CurrentMain
while ($parent = (git -C (Join-Path $CsdroidHarnessRoot "..") rev-parse --show-toplevel 2>$null)) { $CsdroidHarnessRoot = $parent }

$EnvFile = Join-Path $CsdroidHarnessRoot ".csdroid.env"

if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^export (\w+)="?(.*?)"?$') { Set-Item "Env:$($Matches[1])" $Matches[2] }
  }
  Write-Output "CSDROID_HARNESS_ROOT=$Env:CSDROID_HARNESS_ROOT"
  Write-Output "CSDROID_WORKSPACE_ROOT=$Env:CSDROID_WORKSPACE_ROOT"
  Write-Output "(existing .csdroid.env - skipped detection)"
  exit 0
}

# Workspace root:
# - If we started inside a nested repo (current repo != harness), that repo IS the workspace source.
# - Otherwise, look for a source repo under workspace/ (matching the worktree skill's resolution).
# - Else, fall back to the harness root (harness-only layout).
if ($CurrentMain -ne $CsdroidHarnessRoot) {
  $CsdroidWorkspaceRoot = $CurrentMain
} else {
  $srcGit = Get-ChildItem -Path (Join-Path $CsdroidHarnessRoot "workspace") -Filter ".git" -Directory -Recurse -Depth 1 -Force -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($srcGit) {
    $CsdroidWorkspaceRoot = $srcGit.Parent.FullName
  } else {
    $CsdroidWorkspaceRoot = $CsdroidHarnessRoot
  }
}

@(
  "export CSDROID_HARNESS_ROOT=`"$CsdroidHarnessRoot`""
  "export CSDROID_WORKSPACE_ROOT=`"$CsdroidWorkspaceRoot`""
) | Set-Content -Path $EnvFile

Write-Output "CSDROID_HARNESS_ROOT=$CsdroidHarnessRoot"
Write-Output "CSDROID_WORKSPACE_ROOT=$CsdroidWorkspaceRoot"
