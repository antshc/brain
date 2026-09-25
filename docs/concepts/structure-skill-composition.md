# Skill Composition

## Purpose

A capability that grows past one skill can be divided two ways, and each has a failure the other avoids: copying
the shared steps into every skill that needs them leaves several drifting implementations of one behaviour,
while giving every fragment its own model-invoked skill spends always-loaded description budget on skills the
agent never needs to find. This Concept fixes how a capability is divided and how the pieces reach each other.

## Rules

- A skill MUST be responsible for exactly one purpose, nameable in a single phrase.
- A skill that needs behaviour outside its own purpose MUST reach it by invoking the skill that owns it.
- Behaviour needed by more than one caller MUST be owned by exactly one skill.
- A caller MUST reach another skill's behaviour by invoking its documented action, naming it as
  `` `/{{skillName}}` `` **{{ActionName}}**.
- A caller MUST NOT restate, paraphrase, or inline the steps of the skill it invokes.
- The same procedure MUST NOT be written in two skills.
- An action MUST document the values it reads and what it returns, so a caller can invoke it without reading
  the skill's internals.
- A skill MUST keep a `description` only when an agent or another skill must reach it unprompted; otherwise it
  MUST set `disable-model-invocation: true`.
- An agent body MUST carry only its objective, workflow, and verdict, and MUST delegate every specialised
  procedure to a skill it invokes by name.
- A workflow shared by a family of agents MUST live in one flow skill each member invokes.
- A member of such a family MUST carry only the phases it overrides, and MUST NOT restate the shared workflow.
- An agent file MUST NOT point at another agent file: a skill name resolves, an agent's install path does not.
- One flow skill MUST NOT serve two families whose steps differ, because it then branches on its caller.
- A skill whose purpose is delegation MUST NOT name the work it can run; the caller supplies the question,
  prompt instruction, or skill name, its inputs verbatim, and any artifact the subagent may write.
- A skill reached that way MUST NOT invoke the engine that runs it, and MUST state which of its concerns the
  calling engine owns.

## Design Guidance

Divide by counting callers, not by size:

| Callers | Home | Reached by |
|---------|------|------------|
| one skill | that skill, inline | nothing — it is not shared |
| several skills or agents | the one skill that owns the purpose | `` `/{{skillName}}` `` **{{ActionName}}** |
| a human only | a user-invoked skill, no `description` | the human typing its name |

A skill extends itself the same way it shares: when the behaviour it needs sits outside its own single purpose,
it invokes the skill that owns that purpose instead of growing a second responsibility. The owned mechanics stay
in one place, and every sibling that needs them gets them by calling rather than copying.

Invocation is the second cut, and it is paid for in different currencies. A model-invoked skill spends context
on every turn for a description that may never fire; a user-invoked skill spends nothing there but makes you the
index that has to remember it exists. Split off a model-invoked skill only when you have a trigger word you
actually type, or when another skill must reach it.

An agent body holds its objective, its ordered workflow, and the verdict it returns; every procedure that could
be stated without knowing which agent is running it belongs in a skill the body invokes by name. Two agents
needing the same procedure is the clearest signal it was never the agent's to hold.

A family of agents — one general member and several specialised ones — is the same cut seen from the agent side.
The temptation is to copy the general member and edit it, or to have each specialist read the general one as a
parent. Copies drift on every base change; the parent pointer has no addressing mechanism behind it, because an
agent knows neither its own install path nor a way to name a sibling file. Both dissolve once the shared workflow
moves into a **flow skill**: each member is then frontmatter, a flow-skill invocation, and only the phases it
overrides — a delta, not a copy. Two families with genuinely different steps get two flow skills, because one
skill serving both would branch on its caller, which is worse than the duplication it avoids.

A third cut appears once a skill's purpose is *delegation itself* — running another skill inside a subagent with
the context, target, and tools that skill needs. Naming its passengers turns the engine into a second index of
the skill roster, stale from the first skill that joins or leaves; so the engine holds the delegation mechanics
and the caller holds the pairing. The passenger is the mirror of that: it states which concerns the calling
engine owns and invokes no engine itself, because a skill that calls the engine that calls it has two entry
paths through one procedure.

Two related records own adjacent areas: [structure-resource-access-skill](structure-resource-access-skill.md) owns *what* a skill encapsulates
when its purpose is infrastructure access, and [structure-skill-owned-code](structure-skill-owned-code.md) owns where a skill's code and
tests live. This record owns the division and the call style only.

How to word a description, name a skill, or lay out its folders is write-time guidance, not design — see
[agent-skills.instructions.md](../../.github/instructions/agent-skills.instructions.md).

## Violation signals

- The same steps, table, or checklist appearing in two `SKILL.md` files.
- An agent body carrying a procedure one of its skills already documents.
- A caller spelling out the command a skill wraps, instead of naming the skill.
- A skill whose description needs "and" to state what it does.
- A model-invoked skill no agent and no other skill ever reaches.
- A delegating skill listing the skills it can run, or a delegated skill invoking its own delegator.
