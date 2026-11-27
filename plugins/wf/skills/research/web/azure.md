# Azure

Web provider resource. Apply the Brief, including Provider only.

- **Docs** — Microsoft Learn tools (docs search, fetch, code sample search) or `learn.microsoft.com`: service docs, REST/ARM references, built-in RBAC roles, quotas and limits, networking.
- **SDK** — Azure SDK (`Azure.*`, `Microsoft.Azure.*`): first official code samples and API reference for package, version, namespace, type, member; unsettled or Learn unavailable → restored package per the SDK rule.
- **Live subscription** — the Azure CLI. Discover through help: the signed-in account (tenant, subscription, principal type); usage-vs-limit and quota commands for the resource provider; role assignments (including inherited) and role definitions for actions and data actions; resource provider details for API versions and regions; SKU listings for regional availability; what-if for deployment validation. Prefer service-specific commands over generic resource commands; raw ARM calls are GET-only with a pinned `api-version`. Pin the subscription.
- **Gotchas** — REST behavior is pinned to an `api-version`; record it for every REST claim. Control and data planes carry separate permissions (account read does not grant blob reads); record each action's plane. The generic quota commands need the `Microsoft.Quota` provider registered; otherwise use the service's usage command and record the gap.
