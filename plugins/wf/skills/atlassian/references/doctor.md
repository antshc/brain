# Doctor

Inspect the active Atlassian skill runtime without changing it:

```bash
<atl> doctor
```

Reports the active Python executable, configured `pythonPath`, supported package versions, and available `twg`, `mmdc`, and `drawio` binaries. Exit `0` means required Python packages are usable; missing or incompatible runtime packages exit `1` with `problems` and an exact install command.

Run after install and before diagnosing a command that reports missing Python imports. The launcher uses an explicit config `pythonPath` when present; in this source repository it also detects a dependency-complete `.venv/bin/python` upward from CWD.
