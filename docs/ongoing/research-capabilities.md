# Extracted Research Capabilities

Status: proposal / ongoing

## Purpose

Extract the research responsibilities currently embedded in the design workflow. Research discovers evidence, facts, constraints, and viable options. It does not make design decisions.

## Capabilities

| Capability | Research scope | Expected evidence |
|---|---|---|
| Current implementation | Relevant components, responsibilities, dependencies, configuration, state, deployment, constraints, and extension points | Repository citations, existing architecture records, configuration, and tests |
| Capability tracing | Entry points, convergence points, execution path, effects, provider selection, fallbacks, and failure branches inside one deployable | `path:line` citations and focused probes |
| Cross-system tracing | Flow across deployables and internal/external integration boundaries | Producer, consumer, binding, and contract evidence |
| Integration contracts | APIs, events, schemas, SDKs, protocols, authentication, authorization, errors, timeouts, retries, idempotency, ordering, and versioning | Repository contracts plus authoritative protocol or provider documentation |
| .NET runtime | .NET runtime, Base Class Library, language, async, concurrency, cancellation, and lifecycle behavior | Official .NET documentation and source |
| ASP.NET Core | Hosting, middleware, dependency injection, configuration, endpoints, workers, health checks, and shutdown | Official ASP.NET Core documentation and source |
| SDKs | Package and client versions, methods, parameters, response models, pagination, retries, throttling, and errors | Official SDK reference, source, and package metadata |
| Libraries | Third-party library behavior, compatibility, constraints, configuration, and failure semantics | Maintainer documentation, source, and release notes |
| Protocols | Transport, serialization, framing, authentication, compatibility, and error semantics | Authoritative specifications and first-party documentation |
| Cloud | AWS/Azure services, APIs, SDKs, IAM/RBAC, networking, DNS, quotas, pagination, throttling, retries, regional availability, and failure behavior | Provider documentation and live account/subscription evidence when needed |
| Data | Existing schemas, ownership, consistency, concurrency, migrations, retention, and backward compatibility | Schema, persistence code, migrations, tests, and database documentation |
| Deployment | Current topology, configuration, secrets, installation, upgrade, migration, rollback, and cleanup behavior | IaC, manifests, deployment scripts, configuration, and operational documentation |
| Reliability | Existing failure modes, retry behavior, circuit breaking, durability, recovery, degraded modes, and RPO/RTO constraints | Runtime code, tests, telemetry, incident evidence, and dependency guarantees |
| Security | Trust boundaries, identities, permissions, secrets, network exposure, sensitive data, and audit behavior | Security configuration, IAM/RBAC policies, code, and authoritative platform documentation |
| Observability | Existing logs, metrics, traces, correlation, health checks, alerts, and diagnostic gaps | Instrumentation code, dashboards, alerts, and operational evidence |

## Research Skills

| Skill | Responsibility | Status |
|---|---|---|
| `research-capability` | Trace current behavior inside one deployable | Existing |
| `research-deployables` | Trace cross-deployable flows and integration contracts | Existing |
| `research-cloud` | Research AWS/Azure implementation constraints | Existing |
| `research` | Investigate other questions using authoritative primary sources | Existing |
| `research-dotnet` | Research .NET runtime, BCL, language, async, and concurrency behavior | Proposed |
| `research-aspnet-core` | Research ASP.NET Core hosting and application lifecycle behavior | Proposed |
| `research-sdk` | Research SDK packages, versions, clients, methods, retries, and errors | Proposed |
| `research-library` | Research third-party library behavior and compatibility | Proposed |
| `research-protocol` | Research protocol, transport, serialization, auth, and error semantics | Proposed |
| `research-data` | Research existing data models, ownership, consistency, and migration constraints | Proposed |
| `research-deployment` | Research current deployment, configuration, upgrade, and rollback behavior | Proposed |

Reliability, security, and observability are cross-cutting research dimensions. Keep them within the relevant capability, chain, cloud, runtime, or deployment research unless their scope becomes large enough to justify a dedicated skill.

## Common Output

Every research output should contain:

- framed question and scope;
- facts and constraints;
- current behavior;
- relevant contracts and boundaries;
- viable options when requested;
- limits and failure conditions;
- assumptions and unknowns;
- implementation impact;
- evidence beside every non-trivial claim.

Use `FACT`, `LIMIT`, `ASSUMPTION`, and `UNKNOWN` consistently. Research findings become evidence for Wayfinder decisions, `grill-design`, and `to-zdesign`.
