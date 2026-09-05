# wf plugin

Everyday workflow automation skills that carry a feature from an open-ended idea to agent-executable GitHub issues.

## Skill flow

1. **Discovery loop** — [`/wayfinder`](skills/wayfinder/SKILL.md) charts a map of decision tickets (grilled via `/grill-design`, investigated via `/research`, sanity-checked via `/prototype`) until the destination — a spec — is clear; `/to-spec` then synthesizes it.
2. **Requirements capture** — `/to-capabilities` independently turns an idea or spec into capability-aligned requirement sets when a standalone requirements artifact is needed.
3. **Design synthesis** — `/to-zdesign` combines resolved Wayfinder decisions and one or more specs into an authoritative feature design, reconciling capabilities and merging stronger evidence into an existing design.
4. **Story slicing** — `/to-stories` breaks the feature design down into one atomic story per capability.
5. **Story hardening** — `/grill-design` interviews and sharpens each story, run once per story.
6. **Ticket cut** — `/to-tickets` slices each hardened story into agent-executable GitHub issues.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
flowchart TD
    W{"wayfinder or grill-design<br/>resolve unknowns"}
    S["to-spec"]
    SPEC[("Spec")]
    ZD["to-zdesign<br/>synthesize or merge feature design"]
    DESIGN[("Feature design")]
    STORIES["to-stories<br/>break design into per-capability stories"]
    GRILL{"grill-design<br/>interview & sharpen, one story at a time"}
    TICKETS["to-tickets<br/>cut each story into agent-ready GitHub issues"]

    W -- no unknowns left --> S
    S --> SPEC
    SPEC -- direct --> TICKETS

    W -- no unknowns left --> ZD
    SPEC --> ZD
    ZD --> DESIGN

    DESIGN --> STORIES
    STORIES --> GRILL
    GRILL --> TICKETS

    classDef default fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9,stroke-width:2px
```
