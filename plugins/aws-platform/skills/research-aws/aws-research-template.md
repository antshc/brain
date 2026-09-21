# AWS Research: {{topic}}

- Question: {{implementation question}}
- Scope: {{services, API operations, region, account, architecture}}
- Status: investigating | answered

## Services

{{services and resources in scope, with evidence}}

## API Operations

| Operation | Semantics / parameters | Evidence |
|---|---|---|
| {{operation}} | {{required fields, allowed values, defaults, response shape, errors}} | {{AWS doc URL + section, or CLI/MCP query + field}} |

## SDK

| Package | Client / method | Behavior | Evidence |
|---|---|---|---|
| {{package}} | {{client/method}} | {{behavior, version-specific notes}} | {{AWS doc URL + section}} |

## Credentials

{{IAM role, instance/task role, credential provider chain, assume-role path — with evidence}}

## IAM Permissions

| Action | Resource ARN / condition keys | Reason | Evidence |
|---|---|---|---|

## Quotas

| Quota | Value | Type | Implementation impact | Evidence |
|---|---:|---|---|---|
| {{quota}} | {{value}} | hard / adjustable / default / applied | {{impact}} | {{evidence}} |

## Pagination, Throttling, Retries

{{paginated operations, throttling errors, SDK retry mode and attempt count, required backoff — with evidence}}

## Networking

{{public endpoints, VPC endpoints / PrivateLink, DNS, security groups, ports — with evidence}}

## Failure Handling

| Failure | Operation / error code | Implementation impact | Evidence |
|---|---|---|---|

## Assumptions / Unknowns

| Type | Finding | Verification |
|---|---|---|
| ASSUMPTION / UNKNOWN | {{finding}} | {{exact doc lookup or read-only probe that would settle it}} |
