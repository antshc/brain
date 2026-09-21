# {{Provider}} Research

- Topic: {{topic}}
- Question: {{implementation question}}
- Scope: {{services, APIs, region, architecture, account/subscription}}
- Status: investigating | answered

## Services

{{services/resources with evidence}}

## APIs

| API | Semantics / parameters | Evidence |
|---|---|---|
| {{operation}} | {{required fields, allowed values, defaults, response/error behavior}} | {{provider URL + section or MCP result}} |

## SDK

| Package | Client / method | Behavior | Evidence |
|---|---|---|---|
| {{package}} | {{client/method}} | {{behavior}} | {{provider URL + section}} |

## Authentication

{{IAM role / managed identity / service principal / credential chain findings with evidence}}

## Required Permissions

| Permission / role | Scope / resource | Reason | Evidence |
|---|---|---|---|

## API Limits

| Limit | Value | Type | Implementation impact | Evidence |
|---|---:|---|---|---|
| {{limit}} | {{value}} | hard / adjustable / default / applied | {{impact}} | {{evidence}} |

## Retry / Throttling

{{pagination, throttling errors, SDK retry behavior, retry/backoff requirements with evidence}}

## Networking

{{endpoints, DNS, public/private access, VPC/VNet/private endpoints, ports with evidence}}

## Failure Handling

| Failure | API / error | Implementation impact | Evidence |
|---|---|---|---|

## Assumptions / Unknowns

| Type | Finding | Verification |
|---|---|---|
| ASSUMPTION / UNKNOWN | {{finding}} | {{exact doc lookup or provider probe}} |

## Sources

{{official provider sources and live queries used}}
