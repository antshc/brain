---
name: find-root-cause
description: Drive a problem down to its root cause on evidence alone — every claim cited to official documentation or to code, every rejected guess written into a resumable root-cause markdown file. Use when asked why something fails, breaks, regresses, or misbehaves, to diagnose a bug or incident, or to resume an interrupted investigation from its root-cause file.
argument-hint: '<symptom> (e.g. "uploads over 100 MB fail with 504 only in staging"), optionally a path to an existing root-cause file'
---

# Find the root cause

The run is safe to interrupt and repeat. The **ledger** — one markdown file — is the whole memory of the investigation: what is known, what was guessed, and what killed each guess. Nothing lives only in this conversation.

Two words carry the method:

- **Evidence** — a cited fact: `path:line` in the source, a quoted line of official documentation with its URL, or a probe with its actual output — a command, an HTTP request and response, a log excerpt with its host and timestamp, a browser trace. Everything else is a **lead**: a plausible claim from a blog, an answer site, a design doc, an ADR, a graph or semantic-search hit, or your own recollection. A lead may point you at evidence; it may never stand in for it.
- **Falsify** — a **hypothesis** earns its place by predicting something checkable. You attack it to break it, and you accept it only after the prediction survives a check that could have failed.

## 0. Open or resume the ledger

The ledger is `rca-<slug>.md`, `<slug>` naming the symptom (e.g. `rca-large-upload-504-staging.md`). Unless the user named a path, put it where this repository already keeps notes — `docs/notes/`, `docs/`, or `notes/` if one exists, otherwise the repository root.

Search those locations for an existing `rca-*` file on this symptom before creating one.

| Found | Do |
|---|---|
| Yes, `Status: root cause found` | Report the recorded root cause and its evidence, and **stop** unless the user asks to reopen. |
| Yes, still open | Read it whole. Its `Ruled out` rows are closed — you MUST NOT re-test one; its open hypotheses and next probe are this run's starting point. Skip to §3. |
| No | Create it from the template in §5, `Status: investigating`, and continue. |

Done when the ledger file exists on disk and its state has been read.

## 1. Pin the symptom

No hypothesis before the symptom is exact. Get, from the user or from the artefacts they gave you:

- The observable, quoted verbatim — error text, stack trace, log line, wrong value, timing.
- Where and when it was observed: environment, version or build, timestamp.
- The trigger, and whether it is deterministic or intermittent.
- The **delta** — what changed, or what makes a working case differ from a failing one (a version, a config value, an input size, an account, a region).
- The expected behaviour, and what makes the user believe it.

Ask outright for anything missing that would change the search. Record every answer as a fact in the ledger, each with its source; mark anything unverified as an assumption.

Done when the ledger's `Symptom` section states the observable, the trigger, and the delta — or records explicitly that a given one is unavailable.

## 2. Establish the ground truth

Collect the facts that any explanation must fit, before guessing at mechanisms.

Read the repository's own instruction files first (`AGENTS.md`, `copilot-instructions.md`, `README.md`, and any navigation policy they state) and obey their routing, search scoping, and authoritative-source order — they outrank the defaults below.

Whenever this host exposes a skill for the target, prefer it over an ad-hoc search. Three naming patterns cover the routing:

- `search-*` — read a body of source or documentation you don't have locally (another repository, a vendor's docs).
- `inspect-*` — read a dependency's real shipped API or behaviour (decompiled or vendored source).
- `query-*` — read live state from a running system or cloud account.

| Question | Reach for, when available |
|---|---|
| What does this code actually do | the local checkout, with an LSP navigation skill or tool for any symbol; text search only for literals and generated files |
| What does a codebase we don't have locally do | the matching `search-*` skill, else the host's repository-search tool |
| What does a dependency actually do | the matching `inspect-*` skill, else the package's published source |
| What does the vendor guarantee — limits, quotas, semantics, error codes, defaults | the vendor's `search-*` docs skill or docs MCP (e.g. an AWS or Azure documentation server), else fetch the vendor's own page |
| What is the live cloud state | the matching `query-*` skill, else `aws` / `az` CLI with an explicit profile/subscription, plus the provider's own logs and metrics |
| How does the running web UI actually behave | the Playwright MCP — drive the flow, read the DOM, and capture console errors and the network requests behind the symptom |
| What does the HTTP API actually return | `curl -sv` against the endpoint — record status, headers, and body; redact credentials |
| Is it resolution, routing, TLS, or the port | `nslookup` / `dig`, `ping`, `traceroute` / `tracepath`, `ss` / `netstat`, `openssl s_client`, `nc -vz` |

### 2a. Read the running system's configuration

Start from the map, not the host. If `ARCHITECTURE.md` exists (and any deployment view it points at, e.g. `DEPLOYMENT.md`), read its deployment information first — nodes and hosts, which process or container runs where, ports and endpoints, identity provider and downstream dependencies, and the config files each node owns. It tells you which layers below are in play and where to connect; treat it as a **lead** — it can be stale, so every value it states must still be confirmed against the running system before it becomes a fact.

A default in the source is not the value in force. Whenever the symptom is environment-specific, version-specific, or absent on a working case, the deployed configuration is a fact class of its own — read it from the running system rather than inferring it from the repository, and cite host and path or resource id.

| Layer | What to read | How |
|---|---|---|
| Identity provider (e.g. Keycloak) | realm settings, client and its protocol mappers, redirect/web-origin URIs, roles and role mappings, token and session lifespans, active sessions, server version | the admin console via a navigation skill or the Playwright MCP, else the Admin REST API with `curl`; on the host, the server config file and startup arguments |
| Compute instance (e.g. EC2 / VM) | instance type, image id and build, state and launch time, security groups, subnet and routing, attached volumes, instance profile/role, tags, user data, instance metadata | the matching `query-*` skill or `aws ec2 describe-*` / `az vm show`; on the host, `ssh` then the instance-metadata endpoint |
| Operating system on the host | service state and unit definitions, installed package and binary versions, clock and timezone, disk and memory headroom, open ports, kernel and firewall rules | `ssh`, then `systemctl status`, `journalctl`, `rpm -q` / `dpkg -l`, `timedatectl`, `df -h`, `free -m`, `ss -tulpn` |
| Running application | the **effective** configuration — config files as deployed, environment variables of the live process, feature flags and tweaks, connection strings and endpoints (names only, never values that are secret), log level, and the version/build actually running | `ssh` to the VM, then `docker ps` to see which containers and image tags are actually running, and for each one `docker inspect` (env, mounts, ports, restart count) and `docker logs`; for a non-containerised process read the deployed config files and `/proc/<pid>/environ`; else the application's own configuration/health/version endpoint |
| Data and dependencies it talks to | the records the failing flow actually reads, plus the reachability and version of each downstream service | a read-only query against the store (via a `query-*` skill where one exists) and a `curl` of each dependency's health or version endpoint |

Compare the failing environment's configuration against a working one wherever a working case exists — the diff between the two is usually the delta §1 asked for, and it is evidence rather than a lead.

Every probe here is **read-only**. Confirm with the user before any command that mutates state, restarts a service, or writes to a cloud account, and never paste a credential, token, or key into the ledger — cite the file or secret name instead.

Web material counts only when it is **primary**: the vendor's documentation, an API reference, a release note or changelog, an RFC or standard, or the dependency's own source. A blog post, forum answer, or AI summary is a lead — chase it to the primary page and cite that instead, or mark the fact unverified.

Done when every fact in the ledger carries a citation, the effective configuration of each layer the symptom touches is recorded, and each un-citable claim is written as an assumption rather than a fact.

## 3. Enumerate the hypotheses

Write down every mechanism that could produce this symptom given the facts — including the boring ones (config, permissions, version skew, caching, clock, retries, ordering, resource exhaustion) and the possibility that the reported behaviour is correct and the expectation is wrong.

Each hypothesis states a **mechanism** — how the cause produces this exact symptom — and a **prediction**: something that must be observable if it holds and absent if it does not. A hypothesis with no falsifiable prediction is not yet a hypothesis; sharpen it or drop it.

Order them by cost of falsification, cheapest first, breaking ties by how much of the fact set each would explain.

Done when the ledger's `Hypotheses` table holds every candidate with its mechanism, its prediction, and its rank, all `open`.

## 4. Falsify, one at a time

Take the cheapest open hypothesis. Run the check its prediction demands, reaching for the probe in §2 that answers it — read the deciding code, quote the deciding documentation line, run the deciding request or command, inspect the deciding record on the running system.

Write the outcome into the ledger **before** starting the next hypothesis. This single ordering is what makes an interrupted run resumable.

| Outcome | Record |
|---|---|
| Prediction absent | `ruled out`, with the evidence that killed it. |
| Prediction present | `confirmed`, with the evidence — then go to §5. |
| Check inconclusive | `blocked`, with what was tried and the exact access, data, or repro that would unblock it. |

A check that surfaces a new fact goes into `Facts` too, and may add or re-rank hypotheses — do that re-ranking explicitly in the ledger, not in your head.

Every hypothesis ruled out with no candidate left means the fact set is incomplete: return to §2 for a new class of fact (a wider log window, another layer, the next hop) rather than re-testing a closed row.

Done when one hypothesis is `confirmed`, or every hypothesis is `ruled out` or `blocked` and the ledger names the next probe.

## 5. Confirm and write the root cause

A confirmed hypothesis becomes the root cause only once it survives all three:

1. **Mechanism chain** — cause to symptom in ordered steps, each step carrying its own citation, with no "and then somehow".
2. **Fits every fact** — it accounts for the intermittency, the delta, the working cases, and each fact in the ledger; any fact it contradicts sends it back to §4.
3. **Nothing else fits** — the ruled-out rows show why each rival is excluded.

Then finish the ledger: set `Status: root cause found`, fill `Root cause`, and leave `Ruled out` intact — the rejected guesses are the record of what has already been paid for.

Ledger template:

```markdown
# RCA: <symptom in one line>

- Status: investigating | root cause found | blocked
- Opened: <YYYY-MM-DD> · Updated: <YYYY-MM-DD>
- Scope: <service / repo / environment / version>

## Symptom
Observable (verbatim), trigger, delta, expected behaviour.

## Facts
| # | Fact | Evidence (path:line, doc URL + quoted line, or command + output) |
|---|---|---|

## Effective configuration
| Layer | Setting | Value in force (failing) | Value in force (working) | Read from (host/resource + path) |
|---|---|---|---|---|

## Assumptions
| # | Assumption | Why unverified | What would verify it |
|---|---|---|---|

## Hypotheses
| # | Hypothesis (mechanism) | Prediction if true | Cost | Status |
|---|---|---|---|---|

## Ruled out
### H<n> — <hypothesis>
Checked: <what was done>
Result: <what was observed>
Evidence: <citation>

## Root cause
Mechanism chain, step by step, each step cited. Why every other hypothesis is excluded.

## Next probe
The single cheapest unrun check — the resume point.
```

Done when the ledger passes all three tests, or `Status` stays `investigating` and `Next probe` names one concrete check.

## 6. Report

Lead with the root cause in one sentence, then the mechanism chain, then the ledger's path. Name the guesses ruled out and what killed each — that is what stops the next person from re-running them. Separate the fix from the finding: propose it, and change code only if the user asks.

An unfinished run reports the same way, ending on `Next probe` instead of a root cause. Say plainly that no root cause is established yet; a confident guess presented as a finding is the one outcome this skill exists to prevent.
