---
name: research-aws
description: Research AWS implementation constraints — services, API operations, SDK behavior, IAM, VPC/endpoints, Service Quotas, pagination, throttling and retries, and documented failures — and capture them as an evidence-backed research file. Use when an implementation or design decision turns on how an AWS service actually behaves, or to answer a standalone question about an AWS service with evidence.
compatibility: Requires AWS Documentation MCP Server (https://knowledge-mcp.global.api.aws). Applied-quota and resource-state facts additionally require an authenticated AWS CLI.
---

# Research AWS constraints

Facts and constraints, each carrying its evidence. One provider per file — for Azure, Run `/research-azure` skill.

## Sources

- Official AWS docs, API references, and SDK references → Run `/search-aws-docs` skill.
- AWS SDK for .NET package contracts, signatures, and version behavior → Run `/search-aws-sdk-nuget` skill.
- Applied quotas, resource state, and effective permissions → read-only AWS CLI (`aws service-quotas get-service-quota`, `aws <service> describe-*`/`list-*`, `aws iam simulate-principal-policy`).

Evidence priority: live account result > official API/SDK reference > official service docs > Service Quotas / regional availability docs > secondary sources.

**Documented default and applied account value are different facts.** Record which one you have.

## Workflow

1. **Frame** — state the question and scope: services, API operations, region, account, architecture. Set the mode: `implementation` when a design or implementation decision depends on the answer, `question` otherwise.
2. **Research only the dimensions the answer turns on** — services and resources; API operation semantics; SDK client, methods, and version-specific behavior; credentials and IAM; required actions, resource ARNs, and condition keys; VPC, endpoints, DNS, and PrivateLink; Service Quotas and regional availability; pagination, throttling, retries and backoff; documented errors and failure conditions.
3. **Implementation mode: verify every API parameter the implementation sends** — required or optional, allowed values, default, response shape, and the errors it can raise.
4. **Classify each quota** — hard, adjustable, default, or applied. Query Service Quotas when the applied value is what the design depends on.
5. **Probe only when the docs cannot settle a design-relevant fact** — prefer read-only calls and `--dry-run`.
6. **Record every finding as FACT, LIMIT, ASSUMPTION, or UNKNOWN.** Every LIMIT states its impact.
7. **Fill** [aws-research-template.md](aws-research-template.md) — `question` mode keeps the core sections plus only the dimension sections the answer depends on; `implementation` mode fills every section.

## Citations

Evidence sits immediately beside the claim it supports:

- documented behavior → AWS doc URL + section;
- account-specific facts → the CLI or MCP query run, plus the field observed in the result.

Pooling unsupported claims under a generic Sources section hides which claim is unbacked — cite each one in place.

## Output

Write `docs/ongoing/research-<slug>-aws.md` unless the user names another path.

## Done

`question` mode: the Answer rests only on cited findings, and the remaining UNKNOWNs cannot change it.

`implementation` mode: every implementation-relevant API semantic, SDK behavior, IAM action, network path, quota, retry rule, and failure condition is covered with evidence, and the remaining UNKNOWNs cannot change the implementation path.
