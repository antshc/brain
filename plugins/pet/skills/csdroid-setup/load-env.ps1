# Load CSDROID_HARNESS_ROOT and CSDROID_WORKSPACE_ROOT into the current session.
# DOT-SOURCE this file, do not execute it: `. <skill-dir>/load-env.ps1`
# Loads .csdroid.env if present; otherwise detects inline as a fallback so a
# skill still runs standalone (mirrors detect-env.ps1 without writing the file).

$EnvFile = Join-Path (git rev-parse --show-toplevel) ".csdroid.env"

if (Test-Path $EnvFile) {
  Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^export (\w+)="?(.*?)"?$') { Set-Item "Env:$($Matches[1])" $Matches[2] }
  }
} else {
  $Env:CSDROID_HARNESS_ROOT = (Resolve-Path (Join-Path (git rev-parse --git-common-dir) "..")).Path
  while ($parent = (git -C (Join-Path $Env:CSDROID_HARNESS_ROOT "..") rev-parse --show-toplevel 2>$null)) { $Env:CSDROID_HARNESS_ROOT = $parent }
  $workspace = Join-Path $Env:CSDROID_HARNESS_ROOT "workspace"
  if ((Test-Path $workspace) -and (git -C $workspace rev-parse --show-toplevel 2>$null)) {
    $Env:CSDROID_WORKSPACE_ROOT = (git -C $workspace rev-parse --show-toplevel)
  } else {
    $Env:CSDROID_WORKSPACE_ROOT = $Env:CSDROID_HARNESS_ROOT
  }
}
