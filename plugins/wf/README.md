# wf plugin

Everyday workflow automation skills that carry an Initiative from an open-ended idea to agent-executable GitHub issues.

The backlog path ([wayfinder](skills/wayfinder/SKILL.md), [to-spec](skills/to-spec/SKILL.md), [to-tickets](skills/to-tickets/SKILL.md)) supports GitHub only. Each skill bundles its own GitHub reference; [init-wf](skills/init-wf/SKILL.md) sets up baseline labels, including a labels-only repair mode. Spec and ticket publishing can explicitly fall back to local Markdown, reporting offline or partial publication rather than GitHub success. [research](skills/research/SKILL.md) and [bootstrap-docs](skills/bootstrap-docs/SKILL.md) remain local-document workflows. Other skills' Jira metadata and workflows are unchanged.

[grill-design](skills/grill-design/SKILL.md) owns session-ledger operations through its [track-ledger reference](skills/grill-design/references/track-ledger.md), including ownership, resumable questions, and pending writes. It loads closing, verification, and external-source procedures on demand from its bundled references; `track-ledger` is not a standalone skill or command.

Its interview presents the entire ready decision frontier as one numbered batch per round, with recommendations phrased for "yes" to accept. Dependent questions wait for later rounds; partial answers leave the remaining ready questions together for batched follow-up. Inline recording and user-controlled closure remain unchanged.

[record-architecture](skills/record-architecture/SKILL.md) replaces the seven standalone architecture record/render commands. Its modes are `adr`, `building-block`, `deployment-view`, `term`, `concept-body`, `concept-record`, and `decision-bullet`; the two render-only modes never save files or update indexes. Explicit modes take precedence, clear natural-language requests route automatically, and ambiguous requests prompt for the intended artifact. [define-concept](skills/define-concept/SKILL.md) still owns concept discovery and questioning; recording settled knowledge does not repeat the interview.

[to-zdesign](skills/to-zdesign/SKILL.md) renders slice decision bullets from its own local [decision reference](skills/to-zdesign/decision-bullet.md), without invoking the recording skill.

## Skill flow

1. **Discovery loop** — resolving unknowns before a spec or design is clear has two mechanics for the same purpose: [`/wayfinder`](skills/wayfinder/SKILL.md) charts a map of decision tickets on the issue tracker for work too big for one session, resolving each ticket via `/grill-design`, `/research`, or `/experiment`; `/grill-design` run directly interviews a smaller effort in one session, with no map or tickets. Either way, once no unknowns are left, the next step is `/to-spec` (or `/to-zdesign` directly).
2. **Spec synthesis** — `/to-spec` synthesizes the spec from the resolved Wayfinder decisions or grill-design conversation, the step right after the discovery loop; a spec can feed `/to-tickets` directly or go on into design synthesis.
3. **Design synthesis** — `/to-zdesign` combines resolved Wayfinder decisions and one or more specs into an authoritative feature design, reconciling capabilities and merging stronger evidence into an existing design.
4. **Story breakdown** — `/to-stories` accepts requirements, `/to-spec` output, or `/to-zdesign` output and assembles an ordered story list with numbered headings, dependencies, and Jira metadata; it runs [`/draft-story`](skills/draft-story/SKILL.md) once per story for that story's formatted title and body, while `/draft-story` also runs standalone for one User story.
5. **Story hardening** — `/grill-design` interviews and sharpens each story, run once per story.
6. **Ticket cut** — `/to-tickets` slices each hardened story into agent-executable GitHub issues.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-idea-to-implementation-swimlane
swimlane-beta TB
  accTitle: Idea to implementation responsibility
  accDescr: Shows discovery choosing a simple or complex path, each producing a spec that implement-spec turns into an implementation.

  subgraph discovery [Discovery]
    idea([Idea])
    resolve[1 - Resolve unknowns<br/>wayfinder or grill-design]
    choosePath{2 - Choose path}
  end

  subgraph simple [Simple path - SMPL]
    sketchFirst{2a.1 - Sketch code first?}
    smplArchitect[2a.1a.1 - architect<br/>code sketch]
    smplToSpec[2a.2 - to-spec]
    smplSpec[(2a.3 - Spec)]
  end

  subgraph complex [Complex path - CMPLX]
    toZdesign[2b.1 - to-zdesign<br/>synthesize or merge feature design]
    design[(2b.2 - Feature design)]
    toStories[2b.3 - to-stories<br/>assemble design into stories]
    cmplxArchitect[2b.4 - architect<br/>for each story]
    cmplxToSpec[2b.5 - to-spec]
    cmplxSpec[(2b.6 - Spec)]
  end

  subgraph implementation [Implementation]
    implementSpec[3 - implement-spec<br/>sequential or parallel]
    done([Implementation])
  end

  idea --> resolve -->|no unknowns left| choosePath
  choosePath -->|simple| sketchFirst
  sketchFirst -->|no| smplToSpec
  sketchFirst -->|yes| smplArchitect --> smplToSpec
  smplToSpec --> smplSpec -->|parallel| implementSpec
  choosePath -->|complex| toZdesign --> design --> toStories --> cmplxArchitect --> cmplxToSpec --> cmplxSpec -->|sequential or parallel| implementSpec
  implementSpec --> done

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

### Design and story breakdown

Resolves unknowns with `/wayfinder` (work too big for one session) or `/grill-design` (one session), synthesizes the feature design with `/to-zdesign`, then breaks the design into User stories with `/to-stories`.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-design-to-stories-swimlane
swimlane-beta TB
  accTitle: Design and story breakdown responsibility
  accDescr: Shows unknowns resolved by wayfinder or grill-design, a feature design synthesized by to-zdesign, and the design broken down into User stories by to-stories.

  subgraph discovery [Discovery]
    idea([Idea])
    effortSize{1 - Fits one session?}
    wayfinder[1a.1 - wayfinder<br/>chart and resolve decision tickets]
    grillDesign[1b.1 - grill-design<br/>interview in one session]
  end

  subgraph design [Design]
    toZdesign[2 - to-zdesign<br/>synthesize or merge feature design]
    designDoc[(3 - Feature design)]
  end

  subgraph breakdown [Story breakdown]
    toStories[4 - to-stories<br/>assemble ordered story list]
    draftStory[[5 - draft-story<br/>once per story]]
    stories[/6 - User stories/]
    done([Stories ready])
  end

  idea --> effortSize
  effortSize -->|no| wayfinder -->|no unknowns left| toZdesign
  effortSize -->|yes| grillDesign -->|no unknowns left| toZdesign
  toZdesign --> designDoc -->|design| toStories --> draftStory --> stories --> done

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

### Story to implementation

Starts from one existing User story: `/sharpen` hardens it, `/architect` sketches the code, `/to-spec` writes the spec, and `/implement-spec` implements it.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-story-to-implementation-swimlane
swimlane-beta TB
  accTitle: Story to implementation responsibility
  accDescr: Shows one User story sharpened, sketched by architect, turned into a spec, and implemented by implement-spec.

  subgraph story [Story hardening]
    userStory([User story])
    sharpen[1 - sharpen]
  end

  subgraph design [Design]
    architect[2 - architect<br/>code sketch]
    toSpec[3 - to-spec]
    spec[(4 - Spec)]
  end

  subgraph implementation [Implementation]
    implementSpec[5 - implement-spec]
    done([Implementation])
  end

  userStory --> sharpen -->|sharpened story| architect --> toSpec --> spec -->|spec| implementSpec --> done

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

### Story to direct implementation

Starts from one existing User story with no spec: `/sharpen` hardens it, `/architect` sketches the code, and the **implement** reply makes `/architect` build against the accepted sketch in the current branch. It commits the scaffold first, then fills in code, surfacing every deviation from the sketch. If the same friction keeps coming back, it scraps the sketch and re-runs the design. Replying **accept** instead follows Story to implementation.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-story-to-direct-implementation-swimlane
swimlane-beta TB
  accTitle: Story to direct implementation responsibility
  accDescr: Shows one User story sharpened, sketched and reviewed by architect, then implemented by architect against the accepted sketch, with scrap and redesign on repeated friction.

  subgraph story [Story hardening]
    userStory([User story])
    sharpen[1 - sharpen]
  end

  subgraph design [Design]
    sketch[2 - architect<br/>ground and sketch]
    review{3 - architect review<br/>reply?}
    specFlow([Story to implementation flow])
  end

  subgraph implementation [Implementation]
    scaffold[4 - architect implement<br/>scaffold commit]
    fillIn[5 - Fill in code against sketch<br/>surface deviations]
    friction{6 - Repeated friction?}
    done([Implementation])
    scrap[6a.1 - Scrap sketch<br/>re-ground and subtract]
    loopBack([Next iteration - back to step 2])
  end

  userStory --> sharpen -->|sharpened story| sketch --> review
  review -->|implement| scaffold --> fillIn --> friction
  friction -->|no| done
  review -->|accept| specFlow
  friction -->|yes| scrap --> loopBack

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

## Skills

| Group                                     | Purpose                                      | Current skills                                                                            |
| ----------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **define- / discover-**                   | Resolve concept scope and other unknowns     | `define-concept`, `wayfinder`, `grill-design`, `experiment`, `explore-codebase` |
| **probe-**                                | Auto-discover facts in a system and record them | —                                                                                      |
| **research-**                             | Gather external/domain evidence              | `research`, `define-research`, `research-system`                                          |
| **inspect-**                              | Inspect implementations and artifacts        | `inspect-nuget-source`                                                                    |
| **to-**                                   | Transform one artifact/state into another    | `to-use-cases`, `to-spec`, `to-zdesign`, `to-stories`, `to-tickets`    |
| **architect**                             | Sketch, synthesize, review; hand off to spec or implement | `architect`                                                                               |
| **draft-**                                | Author standalone working artifacts          | `draft-bug`, `draft-story`                                                                |
| **record-**                               | Record settled architecture or render bodies | `record-architecture`                                                                     |
| **doc-**                                  | Render existing knowledge                    | `doc-architecture-diagram`, `doc-behavior-diagram`, `doc-code-diagram`, `doc-contracts`        |
| **docs- / setup-** | Workflow plugin documentation infrastructure | `bootstrap-docs`, `index-docs`, `init-wf`               |
| **normalize-**                            | Rewrite/reshape content                      | `normalize-requirements`, `sharpen`                                                       |
