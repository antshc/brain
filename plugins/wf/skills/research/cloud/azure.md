# Azure

Provider reference for an Azure cloud part. Apply the loaded Cloud inspection contract.

## Contents

- Docs
- SDK
- Azure CLI
- Gotchas

## Docs

Search and fetch official Microsoft Learn documentation — service docs, REST/ARM references, RBAC built-in roles, quotas and limits, networking. Use the Microsoft Learn MCP tools (docs search, docs fetch) when installed; otherwise the `mslearn` CLI (`npx @microsoft/learn-cli`) or fetch `learn.microsoft.com` pages directly. Search with product, feature, intent, and resolved SDK version when applicable; fetch the full page for complete limits, parameters, or incomplete excerpts.

## SDK

Azure SDK (`Azure.*`, `Microsoft.Azure.*`):

1. Resolve the version from the workspace — `Directory.Packages.props`, `Directory.Build.props`, `Directory.Build.targets`, `*.csproj`; absent → `obj/project.assets.json`. Never reuse a version from an earlier session.
2. Search official Microsoft code samples and API reference for the package, version, namespace, type, and member — use the Microsoft Learn MCP code sample search when installed.
3. Not settled, or Learn unavailable → send an Explore request directly to `hunter` with `@shape: nuget` to verify the type, member, signature, and behavior using the restored package’s XML docs or decompiled assembly. If Hunter is unavailable, report the blocked lookup and continue independent evidence work.

Other SDKs: resolve the version from the dependency manifest and lockfile, then use Docs.

## Azure CLI

Read-only research of the live subscription. Check `command -v az`; absent → UNKNOWN per Probes.

1. **Identity** — `az account show`; record tenant, subscription, and principal type. Never print credentials.
2. **Pin** — pass `--subscription` on every call; never rely on the implicit default.
3. **Discover** — `az <group> <command> --help` for unfamiliar commands or flags.
4. **Read** — only `show`, `list`, `list-*`, `get-*`, plus:

| Need | Command |
|---|---|
| Compute usage vs limit | `az vm list-usage --location <region>` |
| Network usage vs limit | `az network list-usages --location <region>` |
| Applied quota (any provider) | `az quota show` / `az quota usage list --scope <scope>` |
| Role assignments | `az role assignment list --assignee <id> --scope <scope> [--include-inherited]` |
| Role actions / data actions | `az role definition list --name <role>` |
| Provider API versions, regions | `az provider show --namespace <ns> --query "resourceTypes[?resourceType=='<type>']"` |
| SKU / regional availability | service `list-skus` (e.g. `az vm list-skus --location <region>`) |
| ARM read with pinned version | `az rest --method get --url <ARM url>?api-version=<v>` |
| Deployment validation | `az deployment group what-if` |

5. **Shape output** — `--query '<JMESPath>' -o json` to extract the cited field.

Prefer service-specific commands over generic `az resource`. **MUST NOT** run create, update, set, delete, assign, or any `az rest` other than `--method get`.

## Gotchas

**Azure REST behavior is pinned to an `api-version`.** A parameter or response field in one version is absent in another; record the version every REST claim was read against.

**Control plane and data plane carry separate permissions.** `Microsoft.Storage/storageAccounts/read` does not grant blob reads; record which plane each action or data action serves.

**`az quota` needs the `Microsoft.Quota` provider registered.** Not registered → fall back to the service-specific usage command and record the gap.
