# arc42 Cross-cutting Concepts

Cross-cutting concepts describe rules, patterns, and approaches that apply across multiple building blocks of a system.

Document only the concepts relevant to the system.

## Domain Concepts

- **Domain model** — Core domain entities, relationships, and behavior.  
  Examples: `Customer`, `Order`, `Payment`, `RecoveryPlan`.

- **Business data model** — Business-relevant data structures and relationships.  
  Examples: order schema, customer profile, invoice structure.

- **Business processes** — Domain workflows and responsibilities.  
  Examples: order fulfillment, failover, refund processing.

- **Ubiquitous language** — Shared domain terminology used consistently.  
  Examples: `VPG`, `Failover`, `Recovery Site`, `Protected VM`.

## Architecture & Design Patterns

- **Architecture patterns** — Recurring system-level structural approaches.  
  Examples: modular monolith, microservices, event-driven architecture, hexagonal architecture.

- **Design patterns** — Recurring component-level design solutions.  
  Examples: repository, strategy, factory, circuit breaker.

## User Experience

- **User interface** — Common UI structure and interaction conventions.  
  Examples: navigation, forms, tables, dialogs.

- **Usability** — Rules for efficient and understandable interaction.  
  Examples: confirmation for destructive actions, actionable errors.

- **Internationalization** — Handling languages, locales, dates, and formats.  
  Examples: English/Czech translations, localized date formats.

- **Validation** — User-facing input validation conventions.  
  Examples: required fields, range validation, inline errors.

- **Accessibility** — Making interfaces accessible to different users.  
  Examples: keyboard navigation, screen-reader labels, contrast requirements.

## Safety & Security

- **Security** — Protecting identities, data, and system access.  
  Examples: OAuth/OIDC, RBAC, TLS, encryption, secrets management.

- **Safety** — Preventing failures from causing unacceptable harm.  
  Examples: fail-safe shutdown, operation interlocks, validation before destructive actions.

## Under-the-Hood Concepts

- **Persistence** — How data is stored and retrieved.  
  Examples: PostgreSQL, DynamoDB, repository abstraction.

- **Distribution** — How workloads and data are distributed.  
  Examples: multiple services, worker nodes, regional deployment.

- **Communication & integration** — How components and external systems communicate.  
  Examples: REST, gRPC, Kafka, Azure Service Bus.

- **Transactions** — How consistency and transaction boundaries are handled.  
  Examples: database transaction, saga, outbox pattern.

- **Sessions** — How user or client sessions are managed.  
  Examples: Keycloak session, JWT lifetime, refresh token.

- **Caching** — How reusable data is cached and invalidated.  
  Examples: Redis, in-memory cache, TTL.

- **Concurrency & parallelization** — How concurrent work is coordinated.  
  Examples: worker pools, async processing, TPL Dataflow.

- **Error handling** — Common failure detection and propagation rules.  
  Examples: exception mapping, retries, circuit breakers.

- **Validation / plausibility checks** — Internal checks for valid data and state.  
  Examples: schema validation, state transition validation.

- **Business rules** — How domain rules are represented and enforced.  
  Examples: eligibility rules, pricing rules, RPO constraints.

- **Batch processing** — Processing non-interactive workloads.  
  Examples: nightly cleanup, bulk import, snapshot janitor.

- **Reporting** — Preparing and exposing aggregated information.  
  Examples: audit reports, usage reports, operational dashboards.

## Development Concepts

- **Build** — How source code becomes deployable artifacts.  
  Examples: `dotnet build`, Docker builds, CI pipelines.

- **Testing** — Shared testing strategy and conventions.  
  Examples: unit, integration, contract, end-to-end tests.

- **Deployment** — How artifacts are packaged and released.  
  Examples: Helm charts, Docker Compose, blue-green deployment.

- **Code generation** — How generated source or artifacts are managed.  
  Examples: OpenAPI clients, protobuf classes, ORM models.

- **Configuration** — How environment-specific behavior is supplied.  
  Examples: environment variables, `appsettings.json`, AWS Parameter Store.

- **Migration** — How versions, schemas, and data evolve.  
  Examples: DB migrations, configuration migration, upgrade scripts.

## Operations Concepts

- **Installation** — How the system is initially installed.  
  Examples: installer, Helm deployment, bootstrap script.

- **Administration** — How operators configure and maintain the system.  
  Examples: user management, certificate rotation, configuration changes.

- **Runtime management** — How running components are controlled.  
  Examples: restart service, scale workers, enable maintenance mode.

- **Monitoring** — How health and performance are observed.  
  Examples: Prometheus metrics, CloudWatch alarms, health checks.

- **Logging** — Common logging conventions and destinations.  
  Examples: structured JSON logs, correlation IDs, centralized logging.

- **Scaling** — How system capacity is increased or reduced.  
  Examples: Kubernetes HPA, VM scale sets, worker scaling.

- **Clustering** — How multiple instances cooperate.  
  Examples: Kubernetes cluster, database cluster, Keycloak cluster.

- **Load balancing** — How traffic is distributed.  
  Examples: ALB, NGINX, Traefik.

- **High availability** — How service continues through failures.  
  Examples: redundant instances, multi-AZ deployment, automatic failover.

- **Disaster recovery** — How the system recovers from major failures.  
  Examples: backups, cross-region replication, recovery procedures.
