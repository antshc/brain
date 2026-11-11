# Cloud inspection

Inspector contract for a cloud part. Source of truth is the provider: official docs, API/SDK references, and the live account or subscription. Output: one Markdown draft per provider/question, every claim cited in place; coordinator owns delivery.

Use the brief's loaded provider reference; leave the other unread. Fill the loaded Cloud template.

## Contents

- Framing
- Dimensions
- Evidence ladder
- Claim types
- Quotas
- Probes
- Citations
- Output
- Done

## Framing

State question and scope: provider, services, operations, region, account or subscription, resource group, architecture — only what applies. Set mode:

- `implementation` — a design or implementation decision depends on the answer.
- `question` — standalone question.

## Dimensions

Research only the dimensions the answer turns on:

- services, resources, SKUs/tiers;
- API/REST/ARM operation semantics;
- SDK client, methods, version-specific behavior;
- identity and credentials;
- permissions — actions or roles, plane, scope, resource, condition keys;
- networking — endpoints, private endpoints/PrivateLink, DNS, firewall/security groups, ports;
- quotas and regional availability;
- pagination, throttling, retries, backoff;
- documented errors and failure conditions.

`implementation` mode: verify every parameter the implementation sends — required or optional, allowed values, default, API version, response shape, errors it can raise.

## Evidence ladder

Live account/subscription result > official API/SDK reference > restored SDK package (XML docs, decompiled) > official service docs > quota and regional availability docs > secondary sources.

## Claim types

- **FACT** — confirmed against a provider source or live result; carries a citation.
- **LIMIT** — a constraint; carries a citation and states its implementation impact.
- **ASSUMPTION** — plausible, unconfirmed; state why and the exact lookup or probe that would verify it.
- **UNKNOWN** — named gap, stated as a concrete next check.
- **CONCLUSION** — the answer the facts support.

## Quotas

Classify each quota: hard, adjustable, default, or applied. **Documented default and applied value are different facts** — record which one you have. Query the live account/subscription when the applied value is what the design depends on.

## Probes

Probe only when docs cannot settle a design-relevant fact. CLI use is **read-only**: show/list/describe/get, dry-run, what-if. **MUST NOT** create, update, delete, tag, or assign anything. Run autonomously — no user confirmation. CLI missing, unauthenticated, or access denied → record UNKNOWN with the exact command that would settle it; continue from docs.

## Citations

Evidence sits immediately beside the claim it supports:

- documented behavior → official doc URL + section;
- SDK behavior → package id + version + type/member, plus URL or source used;
- account/subscription facts → the exact CLI or MCP query run, plus the field observed.

Never pool citations under a generic Sources section — it hides which claim is unbacked. Never record secrets, keys, or tokens from CLI output.

## Output

Return the filled template inline for coordinator verification. Apply Caller-owned destinations from Research: saving requires an exact caller-supplied destination; define no default directory, filename, or provider suffix. Obey the template's `**Rules**` blocks and delete every one from the result.

## Done

- `question` mode: Answer rests only on cited findings; remaining UNKNOWNs cannot change it.
- `implementation` mode: every implementation-relevant operation, SDK behavior, permission, network path, quota, retry rule, and failure condition is covered with evidence; remaining UNKNOWNs cannot change the implementation path.
