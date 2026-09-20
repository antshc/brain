---
name: research-cloud
description: Research AWS or Azure implementation constraints across services, APIs, SDKs, IAM/RBAC, networking, quotas, retries, and failures. Use when implementation or design depends on cloud-provider behavior.
compatibility: Requires the provider MCP configured by the solution plugin.
---

# Research cloud

Research facts and constraints; leave design decisions to `cloud-design`.

## Sources

Detect AWS or Azure from the task.

- **AWS:** use AWS Documentation MCP for official docs. Use live/account tools when available for applied quotas or resource state.
- **Azure:** use Azure MCP for subscription/resource facts and Microsoft Learn MCP for official API, SDK, RBAC, quota, networking, and failure documentation.
- Prefer provider MCP evidence over memory or secondary sources.
- Treat documented defaults and current account/subscription values as different facts.

Evidence priority: live provider result > official API/SDK reference > official service docs > official quotas/availability docs > secondary sources.

## Workflow

1. Frame the implementation question and scope: provider, services, APIs, region, architecture, account/subscription.
2. Research only relevant dimensions:
   - services/resources
   - API operations and semantics
   - SDK package, client, methods, version-specific behavior
   - authentication and IAM/RBAC
   - required permissions
   - networking, DNS, endpoints, private connectivity
   - quotas/limits and regional availability
   - pagination, throttling, retries/backoff
   - documented errors and failure conditions
3. Verify every API parameter the implementation sends: required/optional, allowed values, defaults, response shape, errors.
4. For quotas, mark hard, adjustable, default, or applied. Query the provider when the applied value matters.
5. Probe only when official docs cannot settle a design-relevant fact; prefer read-only/dry-run calls.
6. Record findings as **FACT**, **LIMIT**, **ASSUMPTION**, or **UNKNOWN**. Every LIMIT states implementation impact.
7. Fill [cloud-research-template.md](cloud-research-template.md).

## Citations

Every non-trivial fact gets evidence immediately beside it:

- official provider URL + section for documented behavior;
- MCP/live query + observed field for account/subscription facts.

Do not pool unsupported claims under a generic Sources section.

## Output

Write `docs/ongoing/research-<slug>-cloud.md` unless the user specifies another path.

## Done

All implementation-relevant API semantics, SDK behavior, permissions, networking, limits, retry/throttling, and failure conditions are covered; remaining UNKNOWNs cannot change the implementation path.
