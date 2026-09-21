---
name: research-data
description: "Research a system's data as-built: keys, indexes, and the access patterns they serve; the sole writer per item type; read consistency and index lag; attribute-shape evolution and backfill; conditional writes, versioning, and idempotency; retention and expiry. Use when a design or change turns on data shape, key design, who owns a table, whether a read can be stale, how an attribute is migrated, whether concurrent writes are safe, or how records are aged out."
---

# Research a data model

Data, not deployables. One item type has one writer and many readers, so the unit here is the **item type** and the store holding it — a boundary that cuts across services and often across repos.

- Mechanism inside one deployable → Run `/research-capability` skill.
- A flow crossing process boundaries → Run `/research-deployables` skill.
- Provider semantics, quotas, and API parameters behind the store → Run `/research-aws` skill or `/research-azure` skill.

Grounding is shared, not restated: follow `/research-capability` skill **Evidence ladder**, **Claim types**, and **Citations** for every claim written here. IaC and migration files are executing code for this skill's purposes; an entity class is a *declaration* of shape, and the serializer that writes it is the *behavior*.

## Workflow

1. **Frame** — name the decision the data has to support. "Can two checkouts reserve the same seat?" beats "how is the booking table modeled?".
2. **Inventory the stores** — read the table/collection/schema definitions out of IaC, migrations, and config: keys, indexes, streams, expiry settings, and the binding naming the real resource, account, and region.
3. **Collect access patterns before judging keys** — enumerate every read and every write from their call sites, each with its filter, sort, and expected result count. Keys are judged against this list; a key justified by nothing on it is dead weight, and a pattern served by no key is served by a scan.
4. **Attribute every write to its writer** — find-references on the store binding and the grant that permits the write, across every repo that could hold one.
5. **Read the shape off the write path** — the persisted attribute set is whatever the serializer emits, which drifts from what the model class declares: ignored members, custom converters, nulls dropped on write, and older items written by older code.
6. **Settle each dimension** — Schemas, Ownership, Consistency, Migrations, Concurrency, Retention. Each section below names what to establish and the failure it catches.
7. **Probe when static reading can't settle it** — read one real item and diff its attributes against the model, run the query and check whether it scanned, write twice concurrently and see which guard fires. Discard the probe, keep the result.

**Done when** every access pattern names the key or index that serves it and every key and index names a pattern that needs it; every item type names its sole writer and its readers; every read states its consistency and its lag sources; every in-flight attribute change states its backfill and completion signal; every racing write states its guard; every item type states its retention; and the remaining unknowns can't change the design.

## Schemas

Establish, per store: the **partition key** and its cardinality, the sort key and its composite structure, and every secondary index with its keys, its projection, and whether it shares the base partition key or spans the table.

Establish, per item type: attribute names, types, optionality, nested shape, enumerated values, and the size of the largest realistic item.

Establish, per store: **single-table** (several item types in one store, told apart by a discriminator attribute and key prefixes) or table-per-type. Record the discriminator and the prefix grammar — in a single-table design the key *encoding* is the schema, and an undocumented prefix is unreadable to everyone but its author.

A key design is only ever right relative to the access patterns, so record the patterns beside it. **A pattern served by a full scan or a post-fetch filter is a finding, not a design** — say which pattern, how much it reads, and what key or index would serve it.

*Where it hides:* IaC key/index definitions and migration files · entity or item classes and their serialization attributes · query call sites, which reveal the pattern the keys were shaped for · the ORM or mapper configuration.

## Ownership

Establish, per item type: the **sole writer** — the one deployable that creates and updates it — plus every reader.

Where the store has no cross-table foreign keys, ownership is a convention, not a constraint, so prove it rather than infer it from the name: cite the write call sites *and* the grant (IAM policy, role, database user, connection string) that permits the write. **Two deployables holding write grants to one item type is a finding even when only one writes today** — the grant is what makes the second writer possible.

Record readers as an implicit contract: a reader coupling to an attribute the writer owns means the writer cannot rename or retype it unilaterally, and that coupling is invisible from the writer's repo.

## Consistency

Establish, per read: eventually or strongly consistent, and what the caller does with a stale answer.

- **Default is usually eventual**, with strong consistency a per-call option that costs more and is unavailable on some read paths.
- **Secondary indexes lag the base store** — an item written and then queried through a global/cross-partition index in the same request can come back missing or stale. Indexes sharing the base partition key usually don't lag.
- **Transactional scope** — what commits atomically together, and what is two writes that can half-fail. Name the intermediate state a half-failure leaves behind.
- **Replicas** — cross-region replication, read replicas, and caches each add their own lag between the write and the read.

The failure this catches: a request that writes and then immediately reads back through an index, cache, or replica, and passes every test because the test runs slower than production.

## Migrations

Where the store validates no shape on write, **migration means attribute-shape evolution, not DDL**: old items keep their old shape until something rewrites them, so every read path tolerates both shapes for the whole life of the change.

Establish, per change: the attribute added, renamed, retyped, or dropped; the dual-read window and which code reads both shapes; the **backfill** mechanism (change-stream-triggered rewrite, scan-and-update job, or lazy-on-next-write); the signal that proves the backfill finished; and the rollback while it is in flight.

**A rename is an add, a backfill, a read switch, and a drop** — four deploys, not one edit. A lazy backfill never completes for cold items, so it needs a floor date or a sweep.

Where the store does validate shape, establish instead: the migration files and their order, whether the change is expand-then-contract or a breaking single step, and what it locks while it runs.

## Concurrency

Establish, per write that can race: the guard, and what the caller does when the guard fires.

- **Conditional write** — the predicate that makes a conflicting write *fail* rather than clobber, the error the caller receives, and whether the caller retries, surfaces, or swallows it.
- **Optimistic locking** — a version attribute read with the item, asserted on write, and incremented; the **lost update** is what it buys. Record whether the retry re-reads the item or replays stale values.
- **Idempotency** — retried writes are the norm, not the exception (client retries, at-least-once delivery, re-invoked handlers). Record the idempotency key, where the dedupe state lives, and how long it lives; a dedupe record that expires before the retry window is no dedupe at all.
- **Atomic update expressions** versus read-modify-write for counters, sets, and list appends.

The failure this catches: one path guarded and another path writing the same item unguarded, which makes the guard look present and the item still lose updates.

## Retention

Establish, per item type: how long it lives, what removes it, and what sees the removal.

- **Expiry attribute** — which attribute drives it, its unit (epoch seconds versus milliseconds — the wrong unit deletes immediately or never), who sets it and on which writes, and whether updates refresh it.
- **Delete latency** — expiry is typically best-effort and can trail the deadline by hours, so readers filter expired items themselves rather than trusting the store to have removed them.
- **Archive** — whether a change stream feeds an archive before deletion, and whether the archive write is confirmed before the item is unrecoverable.
- **Soft versus hard delete** — a tombstone attribute leaves the item visible to every query that forgets to filter it, and to every index that projects it.
- **Floors and ceilings** — a compliance minimum and a privacy maximum both constrain the number, and they are set outside the code.

## Output

Write `docs/ongoing/research-<slug>-data.md` unless the user names a location.

Fill [data-research-template.md](data-research-template.md), obeying its `**Rules**` blocks and deleting every one of them from the result.

## Gotchas

- **An entity class is a claim about shape, and stored items are the evidence** — items written by earlier code, by a different service, or by a console operator carry attributes no current class declares. Read a real item before describing the shape.
- **An index name in IaC proves the index exists, not that anything queries it** — pair every index with the access-pattern row that needs it, or record it as unused.
- **A local development store is not the production store** — an emulator, in-memory fake, or single-node instance answers consistency, lag, and expiry questions differently from the real one, so those claims need production configuration as evidence.
