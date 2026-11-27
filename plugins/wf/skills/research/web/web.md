# Web

Route procedure for an external question answered from primary sources: official docs, specifications, source code, first-party APIs, and live AWS/Azure accounts. Spawns `weby`; restored SDK gaps go to the `codebase` agent.

## Conditional resources

| Trigger | Resource |
|---|---|
| Provider is AWS | `web/aws.md` |
| Provider is Azure | `web/azure.md` |

## Workflow

1. **Frame.** Preserve the question and requested framing. Resolve target (product, library, standard, provider), versions, and for a provider: mode (`question` or `implementation`), services, operations, region, account/subscription, and whether live values matter. Codebase facts the answer depends on → `codebase` lookups (step 3), not `weby` source reading. State a bounded interpretation when the target is vague. *Done when* each brief names target and, for a provider, mode.
2. **Spawn.** Fill Brief; append the selected provider resource path. Spawn one `weby` per independent question or provider in one parallel batch. *Done when* every worker returned a draft or a blocker.
3. **Resolve SDK gaps.** For each returned `codebase` lookup, spawn the `codebase` agent per Spawning agents with it as the task; batch independent lookups. Merge each verdict into its UNKNOWN as FACT or a confirmed gap. *Done when* no returned lookup is unanswered.
4. **Verify.** Spot-check deciding citations and CLI observations; reconcile conflicts with one bounded `weby` follow-up naming both sources. *Done when* remaining UNKNOWNs cannot change the answer or implementation path.
5. **Present.** Apply Delivery to the worker's draft with light edits only. *Done when* the report pointer is returned.

## Brief

Fill the placeholders; send this section as the worker prompt.

> {QUESTION}

- Target and context — {TARGET_AND_CONTEXT}
- Provider reference — {PROVIDER_REFERENCE}; read it in full; none → omit provider-only rules.
- Requested framing — {OUTPUT_SHAPE}

**Research**

1. Primary sources first: official docs, specs, source, first-party API/SDK references, release notes, live account results. Secondary sources only as leads to a primary one. Evidence order: live result > API/SDK reference > restored SDK package > service docs > quota/availability docs > secondary.
2. Read each deciding source in full at the relevant section; pin version, date, region, or `api-version` when behavior depends on it.
3. Cite every material claim in place: URL + section; SDK → package@version + type/member; live → exact CLI/MCP query + field. Never pool citations in a trailing Sources list. Never record secrets from CLI output.
4. Label claims: **FACT** (cited), **LIMIT** (cited constraint + implementation impact), **ASSUMPTION** (why plausible + exact lookup to confirm), **UNKNOWN** (named gap + next check). Record conflicting sources with both citations.
5. Stop when the question is answered; leave unrelated topics unexplored.

**Provider only**

- Cover only dimensions the answer turns on: resources/SKUs, operation semantics, SDK behavior, identity, permissions (action/role, plane, scope, conditions), networking, quotas and regional availability, pagination/throttling/retries, documented failures. `implementation` mode: verify every parameter the implementation sends (required, allowed values, default, API version, response shape, errors).
- Quotas: classify hard, adjustable, default, or applied; documented default ≠ applied value. Query the live account when the applied value matters.
- Probes: only when docs cannot settle a deciding fact. Read-only CLI per the provider reference (show/list/describe/get, dry-run, what-if); **MUST NOT** create, update, delete, tag, or assign. CLI missing, unauthenticated, or denied → UNKNOWN with the exact command; continue from docs.
- Restored SDK fact needs XML docs or decompiled assembly → UNKNOWN plus a ready `codebase` lookup naming checkout, package, version, type/member, and the claim. The router runs it.

**Return** inline, no file:

- **Answer** — direct answer citing the finding IDs it rests on.
- **Findings** — table `ID | Type | Finding | Evidence`.
- Provider: one section per deciding dimension (Operations, SDK, Identity, Permissions, Quotas, Retries, Networking, Failures), each claim cited; `question` mode keeps only those the answer depends on, `implementation` mode covers every relevant one.
- **Assumptions / Unknowns** — table `Type | Finding | Verification`.
- **Lookups** — `codebase` lookups for the router, if any.
- **Sources checked**.

*Done when* the Answer rests only on cited FACT/LIMIT and remaining UNKNOWNs cannot change it.
