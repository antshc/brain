---
name: draft-cloud-scenario
description: Draft a new cloud scenario that reproduces a bug's reported symptom and validates a proposed fix against real Azure or AWS resources, sourced from the bug's ticket/summary docs or a free-text description. Use when the user asks to write, draft, or create a test scenario, validation plan, or reproduction plan for an escalation, or to turn a workaround option into an executable scenario doc.
disable-model-invocation: true
---

# Draft Cloud Test Scenario

A scenario doc is meant to be executed phase by phase against real resources later — draft it once from the bug, and every fact in it must already be grounded, not left for the first run to discover. Never invent a resource name, flag, or expected result that isn't traceable to the ticket, the summary, or the real source code.

## Setup

1. Read the ticket or the description of the problem — and, if present, a separate summary doc — for: reported symptom, root cause/mechanism, evidence, and every workaround option under consideration. If neither exists, take the reported symptom and fix option from the user's free-text description directly.
2. Identify the target cloud (Azure or AWS) from the ticket's site/platform info. *Done when* one cloud is named — ask if genuinely ambiguous, never draft a mixed scenario.

## Cloud CLI guidance

Reproduce and validate directly against the target cloud's own CLI — `az` for Azure, `aws` for AWS. Load existing aws or azure cloud skills for the valuable environment information. For each phase, discover the exact subcommand and flags for the operation at hand (create a resource from an image vs. from a raw/imported source, attach/detach a volume, swap the boot volume, stop/start the instance, read console/boot output, tear down, etc..) via the CLI's own help or documentation, and check the choice against the real code path from step 1 — the two clouds cover the same operation shapes even though the exact command names differ.

## Workflow

1. **Ground the mechanism** → before writing any command, find the real source file and method that performs the operation under test (resource selection, creation, tagging) via semantic/symbol search — not text search alone. Note its exact creation semantics: which API/CLI operation type it uses (e.g. import-from-source vs. create-from-image), and which branch sets which properties. *Done when* the scenario has a "must match the real code path" section citing a specific file and line range, stating why a naive alternative command would produce a different, non-representative result.
2. **Write Scope** → state the symptom this scenario reproduces, and explicitly exclude the actual root cause when it isn't being fixed here, naming the tracking ticket for it. *Done when* a reader can tell the broken end-state is built directly with CLI commands, not by driving the real product flow.
3. **Write Target environment** → subscription/account, resource group or equivalent, region, base image/AMI, size/instance type, as a variable block reusable across every phase's commands. *Done when* every phase below references these variables instead of repeating literals.
4. **Write Naming convention** → a table mapping each test resource name to its ticket analog and role, mirroring the ticket's real resource names closely enough that phase commands read like the incident. *Done when* every resource named in a later phase appears in this table first.
5. **Write phases** → numbered `## Phase N — <name>` sections, each a short ordered list of steps with exact commands in fenced code blocks, ending in explicit verification commands and an **Expected:** line stating the pass criterion, not just the mechanics. Only add a one-time prerequisite phase (e.g. building a reusable source image/blob) when a later phase's fidelity requirement can't otherwise be met cheaply. *Done when* every phase's expected result is independently checkable from command output alone, without rerunning the scenario.
6. **Write Cleanup** → a final phase deleting every resource created above, in the target cloud's real dependency order (e.g. detach network interfaces before deleting the security group/NSG they reference). Mark it **destructive — requires explicit confirmation before running**, regardless of cloud. *Done when* every resource created in a phase above has a matching delete here, and the resource group/account itself is left untouched unless the ticket calls for removing it too.
7. **Write Caveats and Open items** → carry forward the fix option's own documented limitations (from the summary doc) as Caveats; list every naming/region/size/depth-of-validation choice the drafter could not confirm as Open items for review before execution. *Done when* no open item duplicates a caveat and no caveat is actually resolvable by the drafter right now.
8. **Verify** → re-read the draft against the Quality Check below.

## Quality Check

- Every command names only resources defined in the Naming convention table — no undeclared resource appears in a phase.
- The mechanism section cites real source, not the ticket's prose alone.
- Every phase's **Expected:** line is checkable from command output, not from "it should work."
- Cleanup is ordered by the target cloud's real delete-dependency rules, not copied from the other cloud.
- Nothing destructive runs without the confirmation gate stated in Cleanup.
- Status header reads `Draft — pending review before execution`; no Run history section exists yet on a first draft.

## Output skeleton

```markdown
# <TICKET> — <one-line title>: test scenario (<option under test>)

**Status:** Draft — pending review before execution
**Purpose:** Validate whether <option> from [<TICKET>-summary.md](<TICKET>-summary.md) is viable, by reproducing the broken end-state described in [<TICKET>.md](<TICKET>.md) and applying the proposed remediation.

## Scope

<what symptom is reproduced; what root cause is explicitly excluded and why>

## <Mechanism section title> (must match the real code path)

<file+line citation, exact API/CLI operation type, why a naive alternative would diverge>

## Target environment

| Item | Value |
| --- | --- |

## Naming convention

| Test resource | Ticket analog | Role |
| --- | --- | --- |

## Phase 1 — <name>

1. ...

**Expected:** ...

## Phase N — Cleanup

**Requires explicit confirmation before running** (destructive):

```bash
...
```

## Caveats carried over from <option>

- ...

## Open items for review

- ...
```
