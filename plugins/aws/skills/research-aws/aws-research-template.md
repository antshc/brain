# AWS Research: {{topic}}

- Mode: question | implementation
- Question: {{question}}
- Scope: {{services, API operations, region, account, architecture — only what applies}}
- Status: investigating | answered

## Answer

{{direct answer, citing the finding IDs and sections it rests on}}

## Findings

<!-- Facts the Answer rests on that no dimension section below holds. -->

| ID | Type | Finding | Evidence |
|---|---|---|---|
| F1 | FACT / LIMIT | {{statement; a LIMIT states its impact}} | {{AWS doc URL + section, or CLI/MCP query + field}} |

## Assumptions / Unknowns

| Type | Finding | Verification |
|---|---|---|
| ASSUMPTION / UNKNOWN | {{finding}} | {{exact doc lookup or read-only probe that would settle it}} |

<!-- Question mode: keep only the sections below the answer depends on; delete the rest. Implementation mode: fill every section. -->

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
