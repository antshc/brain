# Skill Composition

## Purpose

A capability that grows past one skill can be divided two ways, and each has a failure the other avoids: copying
the shared steps into every skill that needs them leaves several drifting implementations of one behaviour,
while giving every fragment its own model-invoked skill spends always-loaded description budget on skills the
agent never needs to find. This Concept fixes how a capability is divided and how the pieces reach each other.

## Design Guidance

- **Give each skill one purpose** - Make a skill responsible for one purpose that can be named in a single phrase.
- **Divide by caller count** - Keep behaviour inline when one skill needs it, give behaviour needed by several
  skills or agents to one owning skill, and make human-only behaviour a user-invoked skill.
- **Compose by invoking the owner** - When a skill needs behaviour outside its purpose, invoke the skill that owns
  it instead of adding a second responsibility.
- **Keep one implementation** - Give shared behaviour exactly one owner; never restate, paraphrase, inline, or copy
  its procedure into a caller or another skill.
- **Invoke documented actions** - Reach another skill's behaviour by naming its documented action as
  `` `/{{skillName}}` `` **{{ActionName}}** instead of spelling out the command or internal steps it wraps.
- **Expose action contracts** - Document the values an action reads and returns so callers can use it without
  reading its internals.
- **Choose invocation deliberately** - Keep a `description` only when an agent or another skill must discover the
  skill unprompted; otherwise set `disable-model-invocation: true`. A model-invoked skill spends context on every
  turn, while a user-invoked skill makes the human responsible for remembering it.
- **Keep agent bodies lean** - Limit an agent body to its objective, ordered workflow, and verdict, and delegate
  every specialised procedure to a skill invoked by name.
- **Extract family flow skills** - Move a workflow shared by a family of agents into one flow skill that every
  member invokes. Two agents needing the same procedure is the clearest signal that it does not belong in either
  agent.
- **Describe family members as deltas** - Keep only frontmatter, the flow-skill invocation, and overridden phases
  in each member; do not copy the shared workflow.
- **Reference skills, not agents** - Do not point one agent file at another agent file: skill names resolve, while
  an agent does not know its install path or how to address a sibling file.
- **Separate genuinely different families** - Give families with different steps separate flow skills instead of
  making one flow skill branch on its caller.
- **Keep delegation engines generic** - A skill whose purpose is delegation owns only the mechanics. The caller
  supplies the question, prompt instruction, or skill name, its inputs verbatim, and any artifact the subagent may
  write; the engine does not maintain a list of work it can run.
- **Keep delegated entry one-way** - A skill run by a delegation engine states which concerns the engine owns and
  does not invoke that engine itself, avoiding two entry paths through the same procedure.
- **Discover specialist families from the roster** - A main skill names its extension family as `skillname-*`,
  discovers current members from the available skill roster, and selects one by its description and declared
  compatibility rather than a hardcoded list.
- **Split extension responsibilities** - A specialist owns its subject-specific procedure and contract; the main
  skill owns family discovery, routing, and the shared continuation or verification. `/research` applies this
  with `research-*` and `inspect-*` so a new matching specialist changes available behaviour without adding a
  hardcoded branch to `/research`.
- **Keep adjacent concerns separate** - This record owns division and call style. The
  [resource-access concept](structure-resource-access-skill.md) owns what an infrastructure-access skill
  encapsulates, and the [skill-owned-code concept](structure-skill-owned-code.md) owns where skill code and tests
  live.
- **Leave authoring mechanics to authoring guidance** - Use
  [agent-skills.instructions.md](../../.github/instructions/agent-skills.instructions.md) for wording descriptions,
  naming skills, and laying out folders.

## Violation signals

- The same steps, table, or checklist appearing in two `SKILL.md` files.
- An agent body carrying a procedure one of its skills already documents.
- A caller spelling out the command a skill wraps, instead of naming the skill.
- A skill whose description needs "and" to state what it does.
- A model-invoked skill no agent and no other skill ever reaches.
- A delegating skill listing the skills it can run, or a delegated skill invoking its own delegator.
- A main skill contains a hardcoded list of specialist skills that belong to an extensible `skillname-*` family.
