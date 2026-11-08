# Install MS and set up Azure CLI

Follow this file only on explicit request in Copilot CLI. Resolve this file's absolute path before making changes. This installer configures the local machine and can run from any directory.

## Install the Copilot plugin

1. Check `copilot plugin marketplace list --json`. If `brain` is absent, run `copilot plugin marketplace add antshc/brain`. Use the existing Brain marketplace when it points to that repository or to this installer checkout for local testing. Stop on a source conflict.
2. Check `copilot plugin list --json`. Install a missing plugin with `copilot plugin install ms@brain`. Local marketplaces can show uninstalled entries as disabled with `source: live`. For these entries, check only the matching `enabledPlugins` key in Copilot settings. An absent key permits the initial install; an explicit `false` is disabled. Recheck that `ms` is enabled from `brain` and that its version matches [plugin.json](../plugin.json). Report policy blocks, disabled installs, version mismatches, and failed commands before writing target files. Leave upgrades and enablement of existing installs to the user.

## Set up Azure CLI

1. Check `az --version` (`Get-Command az` on PowerShell). When absent, follow [Microsoft's installation instructions](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli/) for the detected OS and Linux distribution. On Windows with WinGet, use `winget install --exact --id Microsoft.AzureCLI`. Ask the user to handle required elevation. If the current shell cannot see the new command, ask the user to reopen the terminal and resume this installer. Verify `az --version`.
2. Check presence of `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` without printing values. If any is missing, have the user provision it locally through their environment or secret store before resuming. Keep credentials out of the Copilot prompt, logs, project files, and shell profiles.
3. Check that `auth-principal` is loaded. If it is missing after installation, ask the user to run `/restart` and say “Resume the MS installer.” Then *run the `auth-principal` skill to authorize Azure CLI with the configured service principal*.
4. Report plugin status, Azure CLI version, authorization status and any missing prerequisites. This installer writes zero repository files.
