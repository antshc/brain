# wf plugin

Everyday workflow automation skills that carry a feature from an open-ended idea to agent-executable GitHub issues.

## Skill flow

1. **Discovery loop** — [`/wayfinder`](skills/wayfinder/SKILL.md) charts a map of decision tickets (grilled via `/grill-design`, investigated via `/research`, sanity-checked via `/prototype`) until the destination — a spec — is clear; `/to-spec` then synthesizes it.
2. **Requirements capture** — `/to-capabilities` splits the spec into capabilities and adds them as requirements to the feature design doc; `/record-adr` pulls any architectural decisions out of the spec and adds them to the same doc.
3. **Story slicing** — `/to-stories` breaks the feature design doc down into one atomic story per capability.
4. **Story hardening** — `/grill-design` interviews and sharpens each story, run once per story.
5. **Ticket cut** — `/to-tickets` slices each hardened story into agent-executable GitHub issues.

```mermaid
flowchart TD
    W{wayfinder<br/>chart & work a map of decision tickets<br/>via grill-design/research/prototype} -->|destination clear| S[to-spec<br/>synthesize spec from resolved decisions]
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
