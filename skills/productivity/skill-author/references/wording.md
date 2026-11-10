# Wording rules

How to phrase agent-facing text. Structure and content rules live in [best-practices.md](best-practices.md).

## Style

- **Rule first.** Write the actual rule or action first. Add the reason only when it changes interpretation or application.
- **Terse.** Extremely concise, agent-optimized, no fillers. Sacrifice grammar for concision. Omit explanation that does not change agent behavior.
- **Imperative, active voice.** Address the agent with direct commands: Read, Run, Verify, Report. Name the actor when not the agent ("The subagent returns…").
- **Observable over subjective.** Define behavior the agent can check, not goals ("Run affected tests and report results", not "Make sure everything works").
- **Consistent terms.** One term per concept across the document; reuse the same wording for the same rule, never synonyms.
- **Line wrapping.** One physical line per paragraph, bullet, or table cell.
- **Section references.** Use section titles without `#` markers.

## Normative wording

- **MUST** / **MUST NOT** for mandatory rules only.
- Plain imperative for workflow steps and guidance.
- **Prefer** / **SHOULD** for defaults that allow alternatives.

## Positive phrasing

State desired behavior ("write one-line comments"). Keep prohibitions only for hard guardrails that cannot be phrased positively; pair them with desired behavior.

## Leading words

Use familiar **leading words** (_lesson_, _tracer bullets_, _red_) to anchor behavior. Repeat the word, not its explanation.

- Collapse restatements: a triad spelled out at several sites, or a sentence gesturing at one idea → one word. "fast, deterministic, low-overhead" → _tight_ loop; "a loop you believe in" → _red_ (binary observable state).
- Prefer existing words; coined words need definitions.
- Reuse leading words across descriptions, bodies, prompts, and docs.
- A word too weak to beat the default (_be thorough_) is a no-op; use a stronger word (_relentless_).

## Precision patterns

| Intent | Weak | Better |
|---|---|---|
| Imperative | Consider running tests | Run the relevant tests |
| Constraint | Try to use existing tools | MUST use the existing tool |
| Conditional | Handle missing dependencies | If the dependency is unavailable, report the blocker |
| Scope | Keep changes small / Check everything | Modify only files required by the task |
| Rationale | Use a subagent | Delegate exploration to preserve parent context |
| Verification | Make sure everything works | Run affected tests and report results |
| Completion | Finish the task | Complete only when required outputs exist and verification passes |
| Reference loading | Read documentation | Read `references/aws.md` when targeting AWS |
| Proof | Be accurate | For each candidate, identify the triggering input or execution path |
| Completeness | Find the most important issue | Continue after the first finding |
| No result | Always suggest improvements | Return "No findings." after completing the pass |
| Failure | Guess what changed | If the target cannot be inspected, report "incomplete" and the missing evidence |

## No-op test

Delete sentences that do not change the model's default behavior. Settle disagreements by running the document.

## Duplication

Keep one authoritative copy per meaning; replace duplicates with pointers or delete them. Repeating leading words remains intentional.

Sources: repository `agent-skills.instructions.md` Style; [mattpocock/skills](https://github.com/mattpocock/skills) `writing-for-agents` leading words, negation, pruning; Agent Skills best practices KB and AI diff review agent KB (October 2026) wording tables; `shrink` skill rules.
