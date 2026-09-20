---
name: research-aws-capability
description: Research an AWS capability's envelope — what it supports, its hard edges, and what each edge costs a design — and produce a Markdown research doc citing every claim to an official AWS doc URL. Use when a design leans on an AWS service or API to extend product logic, when asked whether AWS can do X, which parameters and allowed values an API accepts, what limits, quotas, prerequisites, regional or instance-type availability, IAM permissions, or cost apply, or what a design must do for cases that fall outside what AWS supports.
compatibility: Requires AWS Documentation MCP Server (https://knowledge-mcp.global.api.aws)
---

# Research an AWS capability

Source of truth is official AWS documentation and live API responses, not recollection. Output: one Markdown file mapping the capability's **envelope** — the region of behavior AWS actually supports — with every claim cited to a doc URL and every edge classified by what it costs the design.

Route every doc lookup through the `search-aws-docs` skill.

## Workflow

1. **Frame** — name the design intent and the AWS capability meant to carry it, as a decision. "Can `RegisterImage` build a bootable AMI from our EBS snapshots for arm64 and UEFI guests?" beats "how do AMIs work?".
2. **Scope** — services, API actions, regions and partitions, instance families, OS and architectures, account model in scope, and what is explicitly out.
3. **Map the surface** — search for the owning service's user guide chapter, the API reference for each action, and the service's quotas page. Collect candidates before reading any deeply.
4. **Read the contract** — per API action the design will call: exact parameter names, allowed values, defaults, required vs optional, mutually exclusive combinations, response shape, and error codes.
5. **Find the edges** — where the envelope ends: prerequisites, unsupported combinations, regional and partition availability, quotas (hard vs adjustable), IAM actions and condition keys, propagation delay and eventual consistency, cost.
6. **Rank by risk** — confirm in this order: does the capability exist for the target region, partition, and resource shape → hard limits that cannot be raised → prerequisites → IAM → error and retry semantics → cost → ergonomics.
7. **Probe** when docs are silent, stale, or self-contradictory: the smallest live call that settles it — `--dry-run`, a `Describe*`, or one throwaway resource in a scratch account. Delete the resource, keep the response.
8. **Price each edge** — every constraint lands in exactly one class: **supported**, **fallback** (the design needs a second path), or **blocker** (this design path dies here).
9. **Record on confirmation** — write each Fact and Limit with its citation immediately, and drop the options it rules out.

**Done when** every parameter the design will send has a confirmed allowed-value range, every edge in scope is named with a citation or probe result, each edge carries its class, and the remaining unknowns can't change the design choice.

## Evidence ladder

Live API response from a probe > AWS API reference (parameter and error contract) > service user guide > Service Quotas or the service's endpoints-and-quotas page > What's New post or release notes > AWS blog or conference talk > third-party post > recollection.

Docs state the *documented* envelope; only a live call proves *this account's* envelope — opt-in region state, applied quota values, feature enablement. When they disagree, record the mismatch as a finding.

## Claim types

- **FACT** — confirmed against a doc page or probe; carries a citation.
- **LIMIT** — an edge of the envelope, marked hard or adjustable, carrying its design class (supported / fallback / blocker).
- **ASSUMPTION** — plausible, unconfirmed; state why, and what would verify it.
- **UNKNOWN** — a named gap, stated as a concrete next probe.
- **CONCLUSION** — the verdict the facts support.

## Citations

Cite the full doc URL plus the section heading inline, immediately after the claim it supports — never pooled at the end. Quote the deciding sentence when short enough to settle the claim on sight. Cite a probe as the command plus the observed response field. "The AWS docs say" without a URL is not a citation.

## Output

Write to `docs/ongoing/<slug>.md` unless the user names a location or the repo documents research elsewhere. Fill [aws-capability-research-template.md](aws-capability-research-template.md), obeying its `**Rules**` blocks and deleting every one of them from the result.

Diagram: `flowchart` for the envelope — inputs branching into the supported path, the fallback path, and each blocker. Use `sequenceDiagram` instead when the finding is about call order, propagation, or polling. Every node or message names the doc URL or probe that established it, keeping the diagram falsifiable.

## Gotchas

- **Availability is per region, partition, instance family, and architecture, not per service** — a capability in the user guide may be absent in the target region, in GovCloud, or in China. Confirm each axis the design depends on.
- **An API reference's allowed-value list lags the user guide** — when they disagree, a `--dry-run` call settles it.
- **A quota page's "default" is the account's starting value, not its current one** — read the applied value from Service Quotas or a `Describe*` call.
