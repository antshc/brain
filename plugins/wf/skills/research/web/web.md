# Web

Route procedure for an external question that is not an AWS/Azure provider question. Spawns `weby`.

## Workflow

1. **Frame.** Preserve the question, target (product, library, standard, version) and requested framing. State a bounded interpretation when the target is vague. *Done when* the question and target are explicit.
2. **Spawn.** Fill `agents/weby.md`: `{QUESTION}`, `{TARGET_AND_CONTEXT}` (target, versions, known constraints), `{OUTPUT_SHAPE}` (requested framing verbatim). Spawn one `weby` per independent question in one parallel batch. *Done when* every worker returned findings or a blocker.
3. **Verify.** Spot-check deciding citations; resolve source conflicts with one bounded `weby` follow-up naming both sources. A deciding fact about restored package behavior in a local checkout → an Explore lookup naming the package and member. *Done when* every deciding claim is cited or marked unknown.
4. **Deliver.** Apply Delivery. *Done when* the report pointer is returned.
