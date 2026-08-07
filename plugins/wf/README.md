# wf plugin

Everyday workflow automation skills that carry a feature from an open-ended idea to agent-executable GitHub issues.

## Skill flow

1. **Discovery loop** — [Wayfinder](https://github.com/mattpocock/skills/tree/main/skills/engineering/wayfinder) explores the codebase and surfaces unknowns; `/to-spec` synthesizes the conversation into a spec. The two hand off to each other until no unknowns remain.
2. **Requirements capture** — `/to-capabilities` splits the spec into capabilities and adds them as requirements to the feature design doc; `/record-adr` pulls any architectural decisions out of the spec and adds them to the same doc.
3. **Story slicing** — `/to-stories` breaks the feature design doc down into one atomic story per capability.
4. **Story hardening** — `/grill-design` interviews and sharpens each story, run once per story.
5. **Ticket cut** — `/to-tickets` slices each hardened story into agent-executable GitHub issues.

```mermaid
flowchart TD
    W[Wayfinder<br/>explore codebase, surface unknowns] --> S[to-spec<br/>synthesize spec from conversation]
    S -->|unknowns remain| W
    S -->|no unknowns left| SPEC[(Spec)]

    SPEC --> CAP[to-capabilities<br/>split spec into capabilities]
    CAP -->|requirements| DESIGN[(Feature design doc)]
    SPEC --> ADR[record-adr<br/>capture architectural decisions from the spec]
    ADR -->|decisions| DESIGN

    DESIGN --> STORIES[to-stories<br/>break design into per-capability stories]
    STORIES --> GRILL{grill-design<br/>interview & sharpen, one story at a time}
    GRILL --> TICKETS[to-tickets<br/>cut each story into agent-ready GitHub issues]
```
