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
4. Mark gaps explicitly: bold the risk or partial result as the verdict; end any claim the evidence does not prove with bold **Not confirmed**, the same tag as What we did. Done when no bullet implies more certainty than the evidence gives.
5. Cut everything else — method, evidence detail, open questions, work items — into the sections below. Done when the bottom line alone still reads as complete.

## Rules

- Decision-oriented, not information-oriented: a reader acting on the bottom line alone makes the right call.
- **Plain language** in every section of the research document: write in ASD-STE100 Simplified Technical English (STE) — active voice, max 25 words per sentence, one idea per sentence, one meaning per word; name no actors ("we", "a team member") — start with the action ("Checked …", "Did not check …") or make the system the subject; keep high-level technical terms (components, runtimes, libraries, protocols, e.g. OpenSSL, ICU, Python 3, certificate export); exclude low-level identifiers (class, script, and file names, paths, commands) except in Remaining work; include version names/IDs only when the topic is an upgrade.
- Lead with the conclusion; never with the setup or method.
- Negative results count: state "does not need X" as its own bullet with the one-line reason.
- No hedging ("it depends", "could potentially") unless the recommendation is genuinely conditional — then state the condition as part of the action.
- Not an **executive summary**: a summary spans paragraphs and covers findings, evidence, and conclusions; a bottom line is one decision per subject, stated once.

## In a full research document

Place the bottom line first, before any method or evidence. Fill this structure; omit an empty optional section.

```markdown
# [Research] {{topic|question or change, with subjects in parentheses}}

## Bottom line

- **{{verdict|one subject's answer, one sentence, plain language}}** {{why|deciding fact or consequence; 0-2 sentences, plain language}}

## What we did

- **{{subject}}:** {{methodAndResult|what we checked, where (test, staging, production), how (code review, automated test, manual check, cloud command line), and what it showed; 1-5 sentences, plain language}} {{skipped|optional; "Did not check …" for scope left out on purpose}} **{{outcome|Confirmed \| Not confirmed \| Blocked}}**

## Still needs validation
<!-- @: optional; what is unproven, and why -->
- {{gap|claim not yet confirmed, the component or dependency at risk, and what would confirm it}}

## Open questions / decisions
<!-- @: optional; questions a person must answer, not tasks -->
- {{question}}

## Remaining work
<!-- @: optional; imperative work items an engineer can pick up -->
- {{workItem|imperative, one goal; name the concrete target — setting, test, list, image, component — with exact names and values (versions, time-outs)}}

## References
<!-- @: optional -->
- {{source}}
```

### Example

```markdown
# [Research] Node.js 22 upgrade for (Checkout service, Product catalog, Order email worker)

## Bottom line

- **Only one service needs the Node.js 22 upgrade: the Checkout service.** It runs on Node.js 18, which reaches end of life. The move to Node.js 22 needs only a settings change and no code change.
- **The Product catalog does not run Node.js** (.NET 8). It does not need the upgrade.
- **The Order email worker already runs Node.js 22.** It does not need the upgrade.
- **Checkout may break on Node.js 22: the payment provider supports only up to Node.js 20.** **Not confirmed**
- **Checkout starts on Node.js 22, but a full purchase does not complete yet:** the end-to-end purchase test timed out at the payment step. **Not confirmed**

## What we did

- **Checkout service:** Checked how the service selects its Node.js version. The version comes from the base image `node:18-alpine`. Built the service on `node:22.9-alpine` in staging, and it started. Then the end-to-end purchase test timed out at the payment step. Did not check refunds or gift cards. **Not confirmed**
- **Order email worker:** Checked the Node.js version on the running worker in production. The version is `v22.9.0`. **Confirmed**

## Still needs validation

- On Node.js 22, a purchase in Checkout does not complete. The payment step times out. The cause is unknown.
- The payment provider SDK, the image-resizing library, and the TLS connection to the payment provider are not tested on Node.js 22.

## Open questions / decisions

- Wait until the payment provider supports Node.js 22, or upgrade now and test it?

## Remaining work

- Switch the Checkout base image to `node:22.9-alpine`.
- Update `Checkout Runtime Version` and `Supported Runtimes` tests expectations.
- Run an end-to-end purchase on Node.js 22 with card and wallet payments; investigate the 30-second payment time-out.
- Verify the payment provider SDK and its TLS connection on Node.js 22.
- Validate the image-resizing library on Node.js 22; then add Node.js 22 to the supported-runtime list.
```
