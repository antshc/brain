---
name: research-aws-capability
description: Research AWS API, SDK, IAM, networking, quota, retry, and failure constraints for an implementation. Use when a design depends on AWS behavior or service limits.
compatibility: Requires AWS Documentation MCP Server (https://knowledge-mcp.global.api.aws)
---

# Research an AWS capability

Use official AWS MCP/documentation as source of truth. Produce one evidence-backed research document; research facts, not design decisions.

## Workflow

1. Frame the implementation question, services, APIs, region/partition, architecture, and account scope.
2. Research only relevant dimensions: API contract, SDK package/method behavior, IAM, networking, quotas, pagination, throttling/retries, errors, availability, lifecycle, cost.
3. Verify exact API parameters, allowed values, defaults, required fields, response shape, and documented errors.
4. Verify region/partition/resource-shape support and quota type: hard, adjustable, or account-specific.
5. Probe only when documentation cannot settle a design-relevant fact. Prefer dry-run or read-only calls; record command and observed field.
6. Classify findings as FACT, LIMIT, ASSUMPTION, or UNKNOWN. For LIMIT, state implementation impact.
7. Fill [aws-capability-research-template.md](aws-capability-research-template.md) and write to `docs/ongoing/<slug>.md` unless the user names another location.

## Evidence

Priority: live probe > AWS API/SDK reference > service guide > quotas/availability docs > release notes > secondary sources.

Cite every non-trivial claim inline with the full official URL and section. A probe citation includes the command and observed response field. Separate documented defaults from the current account's applied values.

## Done

Every API parameter the implementation sends is verified; IAM, networking, limits, retries/throttling, and failure conditions relevant to the flow are covered; remaining unknowns cannot change the implementation path.
