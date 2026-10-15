# Data Inspection: {{subject}}

**Rules** — apply while filling this scaffold, then delete this block and every `**Rules:**` line from the result.

- Every repository file mention and claim carries a file reference per **File references** in the skill — a write call site, a query call site, an IaC/migration line, or a grant. A bare table or attribute name is not evidence.
- Stored items outrank entity classes; IaC and migrations outrank READMEs and diagrams. Record every mismatch as a finding rather than resolving it silently.
- Access patterns and keys are filled as a pair: every pattern names what serves it, every key and index names a pattern that needs it. Leftovers on either side are findings.
- Use `—` where a dimension genuinely does not apply to an item type; leave nothing blank.

- Question: {{the exact decision the data has to support}}
- Scope: {{stores, item types, services in and out of scope}}
- Status: stores inventoried | patterns {{n}}/{{m}} settled | answered

## Summary

**Rules:** 2-3 sentences answering the framed question. Lead with whatever most surprises a reader who assumed the obvious model.

{{summary}}

## Stores

**Rules:** one row per store. `Model` is single-table with its discriminator, or table-per-type. `Binding` cites the IaC/config line naming the real resource, account, and region.

| Store | Engine | Model | Item types | Partition key | Sort key | Binding |
|---|---|---|---|---|---|---|
| {{table, collection, schema}} | {{engine or managed service}} | {{single-table — discriminator \| per-type}} | {{types held}} | {{attribute, cardinality}} | {{attribute, composite structure, or —}} | {{file reference}} |

## Access patterns

**Rules:** one row per distinct read or write, from its call site. `Served by` names the key, index, or `SCAN`. A `SCAN` or post-fetch filter row states what it reads and which key would serve it, in `Notes`.

| # | Pattern | Op | Served by | Caller | Expected rows | Notes | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | {{get X by Y \| list Z for period \| upsert W}} | {{get \| query \| scan \| put \| update \| delete \| transact}} | {{key \| index name \| SCAN}} | {{deployable / handler}} | {{1 \| n \| unbounded}} | {{filter, sort, pagination, cost}} | {{file reference}} |

## Keys and indexes

**Rules:** one row per index, including the base key. `Serves` lists access-pattern numbers; an index serving none is recorded as unused. `Lags base` is the consistency claim this index forces on its readers.

| Index | Type | Partition key | Sort key | Projection | Serves | Lags base | Evidence |
|---|---|---|---|---|---|---|---|
| {{base \| index name}} | {{base \| same-partition \| cross-partition \| relational index}} | {{attribute}} | {{attribute or —}} | {{all \| keys only \| attribute list}} | {{pattern #s \| unused}} | {{yes \| no}} | {{file reference}} |

## Item shapes

**Rules:** one table per item type, under a `### {{itemType}}` subsection. `Source` is the serializer or mapper that actually emits the attribute, not the class that declares it. Record attributes found on stored items but absent from the code as their own rows.

### {{itemType}}

| Attribute | Type | Required | Values / format | Source | Evidence |
|---|---|---|---|---|---|
| {{name}} | {{type}} | {{yes \| no}} | {{enum, encoding, key prefix grammar}} | {{file reference}} | {{file reference or probed item}} |

## Ownership

**Rules:** one row per item type. `Sole writer` is one deployable or a finding. `Write grants` cites every principal permitted to write, whether or not it does — a second grant is a finding. `Reader coupling` names the attributes readers depend on, since those are the ones the writer cannot change alone.

| Item type | Sole writer | Write grants | Readers | Reader coupling | Evidence |
|---|---|---|---|---|---|
| {{type}} | {{deployable}} | {{principals + policy file reference}} | {{deployables}} | {{attributes}} | {{file reference}} |

## Consistency

**Rules:** one row per read. `Lag source` is index, replica, cache, or none. `Stale impact` states what the caller does wrong with a stale answer — "none" is a valid, and load-bearing, answer.

| Read | Consistency | Lag source | Stale impact | Evidence |
|---|---|---|---|---|
| {{pattern #}} | {{eventual \| strong}} | {{cross-partition index \| replica \| cache \| none}} | {{consequence}} | {{file reference}} |

**Rules:** one row per multi-write operation. `Atomic` says whether the writes commit together; `Half-failure state` names the intermediate the system is left in when they don't.

| Operation | Writes | Atomic | Half-failure state | Evidence |
|---|---|---|---|---|

## Migrations

**Rules:** one row per in-flight or planned attribute change. `Read tolerance` cites the code that handles both shapes. `Completion signal` is the observable proving the backfill finished — a count, a sweep result, a floor date. Omit the section when no shape change is in flight, and say so in Unknowns.

| Change | Old shape | New shape | Read tolerance | Backfill | Completion signal | Rollback | Evidence |
|---|---|---|---|---|---|---|---|
| {{add \| rename \| retype \| drop}} | {{shape}} | {{shape}} | {{file reference}} | {{stream \| scan job \| lazy-on-write}} | {{observable}} | {{action while in flight}} | {{file reference}} |

## Concurrency

**Rules:** one row per write that can race. `Guard` is the condition expression, version attribute, atomic update, or `NONE`. A `NONE` row on a contended item is a finding. `Idempotency` names the key and where its dedupe state lives with its lifetime.

| Write | Racing with | Guard | On conflict | Idempotency | Evidence |
|---|---|---|---|---|---|
| {{pattern #}} | {{concurrent caller or retry source}} | {{condition \| version attribute \| atomic update \| NONE}} | {{error + caller behavior}} | {{key; dedupe store; TTL}} | {{file reference}} |

## Retention

**Rules:** one row per item type. `Expiry attribute` includes the unit. `Delete latency` states whether readers must filter expired items themselves. `Archive` says whether the archive write is confirmed before the item becomes unrecoverable.

| Item type | Lifetime | Mechanism | Expiry attribute | Delete latency | Archive | Evidence |
|---|---|---|---|---|---|---|
| {{type}} | {{duration or indefinite}} | {{TTL \| sweep job \| explicit delete \| soft delete}} | {{attribute + unit, or —}} | {{bound + reader filtering}} | {{target + confirmation, or —}} | {{file reference}} |

## Facts

**Rules:** one row per confirmed claim the tables above don't already carry — encoding conventions, cost cliffs, hot-partition risk, what survives a failed write. Prefer facts that contradict the assumed model over facts that confirm it.

| # | Fact | Evidence |
|---|---|---|
| 1 | {{fact}} | {{file reference — `deciding line quoted`}} |

## Assumptions

**Rules:** plausible but unconfirmed. `What would verify it` is a concrete action — a query to run, an item to read, a file to open.

| # | Assumption | Why unverified | What would verify it |
|---|---|---|---|

## Unknowns

**Rules:** `Next probe` names the exact query, command, or file.

| # | Unknown | Next probe |
|---|---|---|

## Conclusion

**Rules:** state the answer the evidence supports, and name the single constraint that actually decides it when several bear on the question.

{{conclusion}}
