---
name: draft-hypotheses
description: Drafts a risk-ranked list of falsifiable hypotheses through grilling.
disable-model-invocation: true
---

# Draft Hypotheses

Grill the user until the assumptions that could change their decision are explicit, then output only the hypotheses worth testing. A hypothesis is a specific claim that evidence can disconfirm; a topic, question, preference, or settled fact is not a hypothesis.

## Frame the decision

Establish the decision or action the hypotheses must support, the candidate approach or options, and the constraints that can change the answer. Seed these from the conversation and any supplied artifacts before asking.

Finding facts is the agent's job. Use the environment and available sources for discoverable facts; ask the user for goals, boundaries, priorities, tolerances, and tradeoffs. Preserve a fact that cannot yet be discovered as an unknown only when resolving it requires research or an experiment.

**Done when:** the target decision, realistic options, and decision-changing constraints are explicit, while every unresolved factual claim is visible as a candidate hypothesis.

## Grill the tree

Map the problem as a decision tree. Each unresolved assumption branches into the assumptions that depend on it. Work breadth-first in rounds: the **frontier** is every question whose prerequisites are settled. Ask the whole frontier in one round, number each question, include a recommended answer, then wait for the user's answers.

When `vscode_askQuestions` is available, use it for the whole frontier in one call. Give each question a concise header, provide concrete options for bounded choices, mark the recommended option, and allow free-form input unless the answer must be restricted. When the tool is unavailable, use this fallback shape:

```markdown
**Q1 — {{short title}}**
{{decision-changing question}}

**Recommended:** {{answer and brief reason}}
```

After each answer, recompute the frontier. Probe for hidden assumptions across feasibility and hard limitations first, then performance and scale, reliability, security, operational complexity, and developer ergonomics. Open only branches that can invalidate an option, alter the decision, or change what evidence is needed. Prune a branch once it violates a hard constraint.

Challenge proposed claims with: "What observable evidence would prove this wrong?" Convert the answer into a disconfirmation condition. Merge claims that would be settled by the same evidence; split claims that could fail independently.

When the frontier is empty, summarize the shared understanding and ask the user to confirm that the grill is complete. Continue grilling if they expose another branch.

**Done when:** the user confirms completion; no decision-relevant assumption remains silent; and every surviving candidate names a claim, its decision impact, and observable disconfirming evidence.

## Produce the hypotheses

Rank surviving hypotheses by the risk that a false claim would invalidate the approach. Prefer this order: feasibility, hard limitations, performance and scale, reliability, security, operational complexity, then developer ergonomics.

Output only this list, with no preamble or follow-up:

```markdown
## Hypotheses

1. **H1 — {{short name}}:** {{specific falsifiable claim}}
   - **Impact:** {{decision or option changed if false}}
   - **Disconfirmed by:** {{observable evidence or experiment result}}
```

Include only unresolved, decision-relevant claims. State known facts as evidence inside a hypothesis only when needed; omit settled facts, preferences, questions, recommendations, and claims whose truth would not change the decision. Use one hypothesis per independently falsifiable claim.

**Done when:** every listed item can be independently disproved, every disconfirmation condition is observable, ordering is risk-first, and every item can change the target decision.