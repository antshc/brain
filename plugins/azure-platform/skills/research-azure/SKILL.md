---
name: research-azure
description: Research Azure implementation constraints — services, REST/ARM operations, SDK behavior, Entra ID authentication, RBAC roles, VNet and private endpoints, subscription quotas, pagination, throttling and retries, and documented failures — and capture them as an evidence-backed research file. Use when an implementation or design decision turns on how an Azure service actually behaves.
compatibility: Requires Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp). Applied-quota and resource-state facts additionally require an authenticated Azure CLI.
---

# Research Azure constraints

Facts and constraints, each carrying its evidence. One provider per file — for AWS, Run `/research-aws` skill.

## Sources

- Official Microsoft docs, REST/ARM references, RBAC, quota, and networking documentation → Run `/search-ms-docs` skill.
- SDK client, method, and signature verification → Run `/search-ms-code-samples` skill.
- Applied quotas, resource state, and role assignments → Run `/query-azure` skill, restricted to read commands (`az ... show`/`list`, `az vm list-usage`, `az role assignment list`).

Evidence priority: live subscription result > official REST/SDK reference > official service docs > quota and regional availability docs > secondary sources.

**Documented default and applied subscription value are different facts.** Record which one you have.

## Workflow

1. **Frame** — state the implementation question and scope: services, operations, region, subscription, resource group, architecture.
2. **Research only the dimensions the decision turns on** — resources and their SKUs/tiers; REST or ARM operation semantics; SDK client, methods, and version-specific behavior; Entra ID identity (managed identity, service principal, `DefaultAzureCredential` chain); RBAC roles, data actions, and assignment scope; VNet, private endpoints, service endpoints, DNS, and firewall rules; subscription and per-resource quotas plus regional availability; pagination, throttling, retries and backoff; documented errors and failure conditions.
3. **Verify every request parameter the implementation sends** — required or optional, allowed values, default, API version, response shape, and the errors it can raise.
4. **Classify each quota** — hard, adjustable, default, or applied. Query the subscription when the applied value is what the design depends on.
5. **Probe only when the docs cannot settle a design-relevant fact** — prefer read-only commands and `--what-if` deployments.
6. **Record every finding as FACT, LIMIT, ASSUMPTION, or UNKNOWN.** Every LIMIT states its implementation impact.
7. **Fill** [azure-research-template.md](azure-research-template.md).

## Citations

Evidence sits immediately beside the claim it supports:

- documented behavior → Microsoft Learn URL + section;
- subscription-specific facts → the `az` or MCP query run, plus the field observed in the result.

Pooling unsupported claims under a generic Sources section hides which claim is unbacked — cite each one in place.

## Gotchas

**Azure REST behavior is pinned to an `api-version`.** A parameter or response field that exists in one version is absent in another, so record the version every REST claim was read against.

**Control plane and data plane carry separate permissions.** A role granting `Microsoft.Storage/storageAccounts/read` does not grant blob reads; record which plane each permission serves.

## Output

Write `docs/ongoing/research-<slug>-azure.md` unless the user names another path.

## Done

Every implementation-relevant operation semantic, SDK behavior, RBAC role, network path, quota, retry rule, and failure condition is covered with evidence, and the remaining UNKNOWNs cannot change the implementation path.
