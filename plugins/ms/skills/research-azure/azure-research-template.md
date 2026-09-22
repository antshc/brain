# Azure Research: {{topic}}

- Question: {{implementation question}}
- Scope: {{services, operations, region, subscription, resource group, architecture}}
- Status: investigating | answered

## Resources

{{resources, SKUs, and tiers in scope, with evidence}}

## Operations

| Operation | API version | Semantics / parameters | Evidence |
|---|---|---|---|
| {{REST or ARM operation}} | {{api-version}} | {{required fields, allowed values, defaults, response shape, errors}} | {{Learn URL + section, or `az`/MCP query + field}} |

## SDK

| Package | Client / method | Behavior | Evidence |
|---|---|---|---|
| {{package}} | {{client/method}} | {{behavior, version-specific notes}} | {{Learn URL + section}} |

## Authentication

{{managed identity, service principal, `DefaultAzureCredential` chain, token audience — with evidence}}

## RBAC Permissions

| Role / action | Plane | Scope | Reason | Evidence |
|---|---|---|---|---|
| {{role or action}} | control / data | {{subscription, resource group, or resource}} | {{reason}} | {{evidence}} |

## Quotas

| Quota | Value | Type | Implementation impact | Evidence |
|---|---:|---|---|---|
| {{quota}} | {{value}} | hard / adjustable / default / applied | {{impact}} | {{evidence}} |

## Pagination, Throttling, Retries

{{continuation tokens, 429 and `Retry-After` behavior, SDK retry policy and attempt count, required backoff — with evidence}}

## Networking

{{public endpoints, private endpoints, service endpoints, Private DNS zones, firewall rules, ports — with evidence}}

## Failure Handling

| Failure | Operation / error code | Implementation impact | Evidence |
|---|---|---|---|

## Assumptions / Unknowns

| Type | Finding | Verification |
|---|---|---|
| ASSUMPTION / UNKNOWN | {{finding}} | {{exact doc lookup or read-only probe that would settle it}} |
