# Research template

Place the bottom line first, before any method or evidence. Insert the Bottom line procedure's returned bullets. Fill this structure; omit an empty optional section. Preserve supplied route-specific explanations, evidence tables, diagrams, source coverage and confidence as additional sections before References; never discard material evidence to fit the scaffold.

```markdown
# [Research] {{topic|question or change, with subjects in parentheses}}

## Bottom line

- **{{finding|what did we find; plain language}}** {{soWhat|why it matters}} {{nowWhat|recommended action, or status ending in bold **Not confirmed**}}

## What we did

- **{{subject}}:** {{methodAndResult|what we checked, where (test, staging, production), how (code review, automated test, manual check, cloud command line), and what it showed; 1-5 sentences, plain language}} {{skipped|optional; "Did not check …" for scope left out on purpose}} **{{outcome|Confirmed \| Not confirmed \| Blocked}}**

## Open questions / decisions
<!-- @: optional; questions a person must answer, not tasks -->
- {{question}}

## Remaining work
<!-- @: required; research left to finish, incl. every unproven claim and what would confirm it; ideally none -->
- {{workItem|imperative, one goal; name the concrete target — claim, test, component — with exact names and values (versions, time-outs)}}
- No remaining work. {{conclusion|use only when nothing is left; one sentence on why the research is complete}}

## Next steps
<!-- @: required; ordered next moves after this research: decisions, handoffs, follow-up work -->
1. {{step|imperative; owner or handoff target when known}}

## References
<!-- @: required; link every research outcome page (test report, evidence page, sub-research file) behind a bullet in What we did, then other sources -->
- [{{title|research outcome page or source name}}]({{link|URL, or repo-relative path for local pages}})
```

## Example

```markdown
# [Research] Node.js 22 upgrade for (Checkout service, Product catalog, Order email worker)

## Bottom line

- **Only the Checkout service needs the Node.js 22 upgrade.** It runs on Node.js 18, which reaches end of life. Change the runtime setting. No code change is needed.
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

## Next steps

1. Decide whether to wait for payment provider support or upgrade now.
2. Run the open validation in Remaining work on Node.js 22 in staging.
3. Upgrade the Checkout service and announce support after validation passes.

## References

- [Checkout staging build and purchase test results](reports/checkout-node22-staging.md)
- [Order email worker production version check](reports/order-email-worker-node-version.md)
- [Node.js release schedule](https://nodejs.org/en/about/previous-releases)
```

## Related terms

In common industry practice they are different layers, though in this document they overlap.

| Term | Industry meaning | Reader |
|---|---|---|
| Bottom line (BLUF / executive summary) | The conclusion and recommendation, placed first and short | Decision-maker |
| Research outcome / findings / results | What the investigation found, with supporting evidence and detail | Peer or engineer |
| Action items | Concrete tasks, each with an owner, due date, and status | Doers |
| Next steps | The high-level sequence of what happens after the research | Everyone |
