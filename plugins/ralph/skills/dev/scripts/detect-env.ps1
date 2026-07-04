#!/usr/bin/env pwsh
# Detect HARNESS_ROOT and persist it to "$HarnessRoot/.agent.env" as an export line.
# Works from the harness root or any of its worktrees.
# Idempotent: if the env file already exists, load it and skip detection.
$ErrorActionPreference = "Stop"

# Main working tree of the current repo (resolves through linked worktrees).
$CurrentMain = (Resolve-Path (Join-Path (git rev-parse --git-common-dir) "..")).Path

# Harness root: climb from the current repo to the outermost enclosing repo.
$HarnessRoot = $CurrentMain
while ($parent = (git -C (Join-Path $HarnessRoot "..") rev-parse --show-toplevel 2>$null)) { $HarnessRoot = $parent }

$EnvFile = Join-Path $HarnessRoot ".agent.env"

if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^export (\w+)="?(.*?)"?$') { Set-Item "Env:$($Matches[1])" $Matches[2] }
  }
  Write-Output "HARNESS_ROOT=$Env:HARNESS_ROOT"
  Write-Output "(existing .agent.env - skipped detection)"
  exit 0
}

@(
  "export HARNESS_ROOT=`"$HarnessRoot`""
) | Set-Content -Path $EnvFile

Write-Output "HARNESS_ROOT=$HarnessRoot"
