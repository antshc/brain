---
description: Write a bottom line — the single decision-oriented statement of a research or investigation's key finding, why it matters, and the recommended action. Use when drafting a research document's conclusion, summarizing findings for decision-makers, writing an executive takeaway, or turning investigation results into a recommendation.
name: bottom-line
---
# Bottom line

A bottom line answers, per investigated subject, in exactly three sentences — one sentence per answer:

1. **What did we find?** — the finding, one sentence.
2. **So what?** — why it matters, one sentence.
3. **Now what?** — the recommended action, or the confirmed/unconfirmed status, one sentence.

## Write it

1. List the investigated subjects (services, components, options). Done when every subject in the research scope has one bullet.
2. Open each bullet with the finding in **bold**, one sentence, as the answer itself, not the path to it. Done when a reader who reads only the bold text knows every conclusion.
3. Follow with so what — one sentence with the deciding fact or consequence (cost, risk, capability unlocked). Done when each finding is tied to a fact or outcome.
4. End with now what — one sentence with the recommended action. Done when each bullet has an action or status.
5. Mark gaps explicitly: bold the risk or partial result as the finding; end any claim the evidence does not prove with bold **Not confirmed**, the same tag as What we did. Done when no bullet implies more certainty than the evidence gives.
6. Cut everything else — method, evidence detail, open questions, work items — into the sections below. Done when the bottom line alone still reads as complete.

## Rules

- Decision-oriented, not information-oriented: a reader acting on the bottom line alone makes the right call.
- **Plain language** in every section of the research document: write in ASD-STE100 Simplified Technical English (STE) — active voice, max 25 words per sentence, one idea per sentence, one meaning per word; name no actors ("we", "a team member") — start with the action ("Checked …", "Did not check …") or make the system the subject; keep high-level technical terms (components, runtimes, libraries, protocols, e.g. OpenSSL, ICU, Python 3, certificate export); exclude low-level identifiers (class, script, and file names, paths, commands) except in Remaining work, Next steps, and the trailing parentheses of Action items; include version names/IDs only when the topic is an upgrade.
- **Action items** use non-technical language: a non-engineer reads each item and knows what changes and why. Name the outcome, not the mechanism; no version numbers or time-outs unless the topic is an upgrade. The sentence must read complete without the names.
- **Action items** may name classes, test methods, files, and scripts, only in trailing parentheses, as a terse action plus plain words with spaces, then the type (class, test, bash script, txt config): no backticks, underscores, camel case, or file extension, e.g. "(fix install step in Orchestrator Environment Fixture class)", "(update expectations in Some Test Case Success test)", "(raise limit in Supported Distros List txt config)". Add a name only where it saves the implementer a search. No setting or image names; no commands, paths, or values.
- **Action items** are deliverable functional slices: one bullet per slice, grouping every task needed to deliver one user-visible or testable outcome. Never one bullet per task; never split a slice across bullets.
- Write each action item as an outcome sentence, then "Done when" with the checkable completion condition. Do not use user-story form ("As a …, I want …").
- Order slices by dependency; state a prerequisite slice in the "Done when" condition ("only after …"). Done when each slice can be delivered and verified on its own.
- Lead with the conclusion; never with the setup or method.
- Negative results count: state "does not need X" as its own bullet with the one-line reason.
- No hedging ("it depends", "could potentially") unless the recommendation is genuinely conditional — then state the condition as part of the action.
- Not an **executive summary**: a summary spans paragraphs and covers findings, evidence, and conclusions; a bottom line is one decision per subject, stated once, in three sentences.

## In a full research document

Place the bottom line first, before any method or evidence. Fill this structure; omit an empty optional section.

```markdown
# [Research] {{topic|question or change, with subjects in parentheses}}

## Bottom line

- **{{finding|what did we find; exactly one sentence, plain language}}** {{soWhat|why it matters; exactly one sentence}} {{nowWhat|recommended action, or status ending in bold **Not confirmed**; exactly one sentence}}

## What we did

- **{{subject}}:** {{methodAndResult|what we checked, where (test, staging, production), how (code review, automated test, manual check, cloud command line), and what it showed; 1-5 sentences, plain language}} {{skipped|optional; "Did not check …" for scope left out on purpose}} **{{outcome|Confirmed \| Not confirmed \| Blocked}}**

## Open questions / decisions
<!-- @: optional; questions a person must answer, not tasks -->
- {{question}}

## Remaining work
<!-- @: required; research left to finish, incl. every unproven claim and what would confirm it; ideally none -->
- {{workItem|imperative, one goal; name the concrete target — claim, test, component — with exact names and values (versions, time-outs)}}
- No remaining work. {{conclusion|use only when nothing is left; one sentence on why the research is complete}}

## Action items
<!-- @: required; one bullet per deliverable functional slice, not per task; non-technical language, outcome not mechanism; no user-story form -->
- {{actionItem|imperative outcome, one slice; plain business wording; name the product area; class names only in trailing (Name with spaces), no files, scripts, settings, images, commands, or values}} Done when {{doneWhen|checkable completion condition covering the slice's tasks; prerequisite slices as "only after …"}}.

## Next steps
<!-- @: required; ordered next moves after this research: decisions, handoffs, follow-up work -->
1. {{step|imperative; owner or handoff target when known}}

## References
<!-- @: required; link every research outcome page (test report, evidence page, sub-research file) behind a bullet in What we did, then other sources -->
- [{{title|research outcome page or source name}}]({{link|URL, or repo-relative path for local pages}})
```

### Example

```markdown
# [Research] Node.js 22 upgrade for (Checkout service, Product catalog, Order email worker)

## Bottom line

- **Only the Checkout service needs the Node.js 22 upgrade.** It runs on Node.js 18, which reaches end of life. Change the runtime setting; no code change is needed.
- **The Product catalog does not run Node.js** (.NET 8). It has no Node.js end-of-life risk. Do not upgrade it.
- **The Order email worker already runs Node.js 22.** It has no end-of-life risk. Do not upgrade it.
- **The payment provider supports only up to Node.js 20.** Checkout may break on Node.js 22. Test the provider SDK on Node.js 22 before release. **Not confirmed**
- **Checkout starts on Node.js 22, but the end-to-end purchase test timed out at the payment step.** A full purchase may not work after the upgrade. Find the cause of the time-out before release. **Not confirmed**

## What we did

- **Checkout service:** Checked how the service selects its Node.js version. The version comes from the base image `node:18-alpine`. Built the service on `node:22.9-alpine` in staging, and it started. Then the end-to-end purchase test timed out at the payment step. Did not check refunds or gift cards. **Not confirmed**
- **Order email worker:** Checked the Node.js version on the running worker in production. The version is `v22.9.0`. **Confirmed**

## Open questions / decisions

- Wait until the payment provider supports Node.js 22, or upgrade now and test it?

## Remaining work

- Find the cause of the 30-second payment time-out in the end-to-end purchase test on Node.js 22.
- Verify the payment provider SDK, the image-resizing library, and the TLS connection to the payment provider on Node.js 22.

## Action items

- Run the Checkout service on the newer Node.js version. Done when the service uses the newer version, the automated checks expect it (update expectations in Checkout Runtime Tests test), and the end-to-end purchase test passes.
- Announce the newer version as supported. Done when the announcement is published, only after product image resizing passes its checks.

## Next steps

1. Decide whether to wait for payment provider support or upgrade now.
2. Run the open validation in Remaining work on Node.js 22 in staging.
3. Apply the action items after validation passes.

## References

- [Checkout staging build and purchase test results](reports/checkout-node22-staging.md)
- [Order email worker production version check](reports/order-email-worker-node-version.md)
- [Node.js release schedule](https://nodejs.org/en/about/previous-releases)
```
