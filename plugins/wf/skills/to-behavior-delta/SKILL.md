---
name: to-behavior-delta
description: Document only what a capability adds, modifies, or removes as a styled Mermaid diagram — a class diagram, flowchart, swimlane diagram, sequence diagram, or deployment view. Use whenever an implementation appendix, changelog, or PR description needs a diagram delta rather than a full current-state diagram — even if the user just says "diagram the delta", "show what changed", or "add a delta diagram" without naming this skill. Never for a solution-level diagram (C4 container/solution diagram, standalone flowchart, high-level sequence diagram) — those are always complete and owned by `/to-behavior-diagram` alone.
---

Show only added, modified, or removed elements, plus the minimum unstyled elements needed to connect them — never a full, unrelated diagram of untouched behavior.

## 1. Produce the base diagram

Follow `/to-behavior-diagram` skill to pick and open the matching template — Class Diagram, Flowchart, Swimlane Diagram, Sequence Diagram, or Deployment View. Do not compose from memory.

## 2. Apply the delta overlay

Style the base diagram per its kind:

- **Class Diagram:** mark added classes `:::added`, removed classes `:::removed`, changed classes `:::memberChanged` with `[add]`/`[rem]`-prefixed members; add the three `classDef` lines (`added` `#4a7a5a` stroke, `removed` `#8a4a4a` stroke, `memberChanged` `#8b949e` dashed stroke). Show only new, modified, and deleted classes/fields/methods — omit unchanged members of a changed class. An intermediate class needed only to complete a connection between two delta classes stays unstyled, listing only the member(s) that connection uses.
- **Flowchart:** mark added nodes `:::added`, removed nodes `:::removed` (`#4a7a5a`/`#8a4a4a` stroke `classDef`s); there is no `:::memberChanged` equivalent — restyle a materially changed node `:::added`, or leave it unstyled and describe the change in prose. Omit unchanged nodes not needed to connect the delta.
- **Swimlane Diagram:** same `:::added`/`:::removed` convention as Flowchart. A lane that is itself entirely new or removed has no supported Mermaid styling mechanism (no border-color hook on `subgraph`) — call it out in prose instead. Omit unchanged nodes and lanes not needed to connect the delta.
- **Sequence Diagram:** no `:::` styling mechanism exists for sequence diagrams — mark a new or changed step with a `note over` call-out or a leading `NEW:`/`CHANGED:` label in the message text. Omit lifelines and messages that are unchanged and not needed to connect the delta.
- **Deployment View:** apply `UpdateElementStyle(alias, $borderColor="...")` per element instead of `classDef`: added `#4a7a5a`, removed `#8a4a4a`, unchanged `#8b949e` (included only to complete a connection to a delta element). Add a `**Behaviour changes**` bullet list (`+`/`-`/`~` prefix) for an in-place node change (resized instance, new runtime version, changed scaling policy) not visible in the diagram's added/removed elements; omit the list when there is none.

**Done when:** the base template was opened via `/to-behavior-diagram` skill this run; only added, modified, or removed elements are shown or styled, plus the minimum unstyled elements needed to connect them; the diagram's kind uses its own styling convention above, never another kind's; no unused example element or hidden instruction remains.
