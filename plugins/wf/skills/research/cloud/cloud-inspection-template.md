# Cloud Inspection: {{topic}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- One provider per document.
- Every claim carries its evidence in place per **Citations** in the cloud-inspection reference; no pooled Sources section.
- Every LIMIT states its implementation impact.
- `question` mode: keep Answer, Findings, Assumptions / Unknowns, plus only the dimension sections the answer depends on; delete the rest. `implementation` mode: fill every section.
- Nothing reaches the Answer without a FACT or LIMIT behind it.

- Provider: AWS | Azure
- Mode: question | implementation
- Question: {{question}}
- Scope: {{services, operations, region, account or subscription, resource group, architecture — only what applies}}
- Status: investigating | answered

## Answer

**Rules:** direct answer citing the finding IDs and sections it rests on.

{{answer}}

## Findings

**Rules:** facts the Answer rests on that no dimension section below holds.

| ID | Type | Finding | Evidence |
|---|---|---|---|
| F1 | FACT / LIMIT | {{statement; a LIMIT states its impact}} | {{doc URL + section, or CLI/MCP query + field}} |

## Assumptions / Unknowns

| Type | Finding | Verification |
|---|---|---|
| ASSUMPTION / UNKNOWN | {{finding}} | {{exact doc lookup or read-only probe that would settle it}} |

## Resources

{{services, resources, SKUs, and tiers in scope, with evidence}}

## Operations

**Rules:** API version — the Azure `api-version` read against; `—` for AWS.

| Operation | API version | Semantics / parameters | Evidence |
|---|---|---|---|
| {{API, REST, or ARM operation}} | {{version or —}} | {{required fields, allowed values, defaults, response shape, errors}} | {{doc URL + section, or CLI/MCP query + field}} |

## SDK

| Package @ version | Client / method | Behavior | Evidence |
|---|---|---|---|
| {{package@version}} | {{client/method}} | {{behavior, version-specific notes}} | {{doc URL + section, or restored package type/member}} |

## Identity and Credentials

{{AWS: IAM role, instance/task role, credential provider chain, assume-role path. Azure: managed identity, service principal, `DefaultAzureCredential` chain, token audience — with evidence}}

## Permissions

**Rules:** Plane — Azure `control` / `data`; `—` for AWS. Scope — AWS resource ARN and condition keys; Azure subscription, resource group, or resource.

| Action / role | Plane | Scope / resource / conditions | Reason | Evidence |
|---|---|---|---|---|
| {{action or role}} | {{plane or —}} | {{scope}} | {{reason}} | {{evidence}} |

## Quotas

| Quota | Region | Value | Type | Implementation impact | Evidence |
|---|---|---:|---|---|---|
| {{quota}} | {{region}} | {{value}} | hard / adjustable / default / applied | {{impact}} | {{evidence}} |

## Pagination, Throttling, Retries

{{paginated operations and continuation tokens, throttling errors and `Retry-After`, SDK retry mode/policy and attempt count, required backoff — with evidence}}

## Networking

{{public endpoints, VPC endpoints / PrivateLink or private/service endpoints, DNS, security groups or firewall rules, ports — with evidence}}

## Failure Handling

| Failure | Operation / error code | Implementation impact | Evidence |
|---|---|---|---|
| {{failure}} | {{operation / code}} | {{impact}} | {{evidence}} |
