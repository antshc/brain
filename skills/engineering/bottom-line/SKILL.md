---
description: Write a bottom line — the single decision-oriented statement of a research or investigation's key finding, why it matters, and the recommended action. Use when drafting a research document's conclusion, summarizing findings for decision-makers, writing an executive takeaway, or turning investigation results into a recommendation.
name: bottom-line
---
# Bottom line

A bottom line answers, per investigated subject, in 1–3 sentences:

1. **What did we find?** — the finding.
2. **So what?** — why it matters.
3. **Now what?** — the recommended action, or the confirmed/unconfirmed status.

## Write it

1. List the investigated subjects (services, components, options). Done when every subject in the research scope has one bullet.
2. Open each bullet with the verdict in **bold**, as the answer itself, not the path to it. Done when a reader who reads only the bold text knows every conclusion.
3. Follow with why — the deciding fact or consequence (cost, risk, capability unlocked). Done when each verdict is tied to a fact or outcome.
4. Mark gaps explicitly: prefix untested claims with `Untested;`; state what was confirmed and what was **not confirmed yet**. Done when no bullet implies more certainty than the evidence gives.
5. Cut everything else — method, evidence detail, open questions, work items — into the sections below. Done when the bottom line alone still reads as complete.

## Rules

- Decision-oriented, not information-oriented: a reader acting on the bottom line alone makes the right call.
- Lead with the conclusion; never with the setup or method.
- Negative results count: state "does not need X" as its own bullet with the one-line reason.
- No hedging ("it depends", "could potentially") unless the recommendation is genuinely conditional — then state the condition as part of the action.
- Not an **executive summary**: a summary spans paragraphs and covers findings, evidence, and conclusions; a bottom line is one decision per subject, stated once.

## In a full research document

Place the bottom line first, before any method or evidence. Fill this structure; omit an empty optional section.

```markdown
# [Research] {{topic|question or change, with subjects in parentheses}}

## Bottom line

- **{{verdict|one subject's answer, one sentence}}** {{why|deciding fact or consequence; 0-2 sentences}}

## What we did as part of the research

- **{{subject}}:** {{methodAndResult|what we checked and what it showed; 1-5 sentences, plain non-technical English; keep concrete evidence — versions, IDs, commands}}

## Still needs validation
<!-- @: optional; what is unproven, and why -->
- {{gap|claim not yet confirmed and what would confirm it}}

## Open questions / decisions
<!-- @: optional; questions a person must answer, not tasks -->
- {{question}}

## Remaining work
<!-- @: optional; imperative work items -->
- {{workItem|imperative, one action}}

## References
<!-- @: optional -->
- {{source}}
```

### Example

```markdown
# [Research] Node.js 22 upgrade for (Checkout service, Product catalog, Order email worker)

## Bottom line

- **Only one service needs the Node.js 22 upgrade: the Checkout service.** It runs on Node.js 18, which reaches end of life; Node.js 22 is selectable by changing the container base image only, no code change.
- **The Product catalog does not run Node.js** (.NET 8). It does not need the upgrade.
- **The Order email worker already runs Node.js 22.** It does not need the upgrade.
- Untested; the payment provider SDK used by Checkout lists Node.js 20 as its newest supported version and may break on 22.
- Checkout started on Node.js 22, but the end-to-end purchase test timed out, so a completed order is **not confirmed yet**.

## What we did as part of the research

- **Checkout service:** Reviewed how the service picks its runtime and found it comes from the container base image `node:18-alpine`. Built the service on `node:22.9-alpine` and confirmed it started; the end-to-end purchase test then timed out at the payment step.
- **Order email worker:** Opened a shell in the running worker and checked its version: `node --version` returned `v22.9.0`. It already runs Node.js 22.

## Still needs validation

- A purchase on Checkout running Node.js 22 did not complete end to end (payment step timed out, cause unknown).

## Open questions / decisions

- Whether to wait for the payment provider to officially support Node.js 22 or upgrade now and test it ourselves.

## Remaining work

- Switch the Checkout base image to `node:22.9-alpine`.
- Run an end-to-end purchase on Node.js 22; investigate the payment step timeout.
```
