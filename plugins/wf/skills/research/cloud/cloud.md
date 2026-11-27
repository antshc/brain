# Cloud

Route procedure for an independent AWS or Azure provider question. Spawns `cloudy`; restored SDK gaps go to `hunty`.

## Conditional resources

| Trigger | Resource |
|---|---|
| Every Cloud brief | `cloud/cloud-inspection-template.md` |
| Provider is AWS | `cloud/aws.md` |
| Provider is Azure | `cloud/azure.md` |

## Workflow

1. **Frame.** Preserve the question and requested framing. Resolve provider, mode (`question` or `implementation`), services, operations, region, account/subscription, relevant dimensions, and whether live values matter. Split one brief per provider/question. *Done when* each brief names provider and mode.
2. **Spawn.** Fill the Cloud brief below into `agents/cloudy.md`; append the template and the selected provider reference in full. Spawn independent briefs in one parallel batch. *Done when* every worker returned a filled template or a blocker.
3. **Resolve SDK gaps.** For each returned `hunty` lookup, spawn the `hunty` agent per Spawning agents with it as `@work`; spawn independent lookups in one batch. Merge each verdict into the matching UNKNOWN as FACT or a confirmed gap. *Done when* no returned lookup is unanswered.
4. **Verify.** Spot-check deciding citations and CLI observations; reconcile conflicts with one bounded `cloudy` follow-up. *Done when* remaining UNKNOWNs cannot change the answer or implementation path.
5. **Deliver.** Apply Delivery. *Done when* the report pointer is returned.

## Cloud brief

- Question and mode.
- Provider, services, operations, region, account/subscription, resource group, architecture: only what applies.
- Dimensions the answer turns on.
- Live values needed: yes/no; safe read-only CLI access available: yes/no/unknown.
- Requested framing verbatim.
- Codebase facts the answer depends on → `hunty` lookups (step 3), not `cloudy` source reading.
