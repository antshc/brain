# wf plugin

Everyday workflow automation skills that carry an Initiative from an open-ended idea to agent-executable GitHub issues.

[Design](skills/design/SKILL.md) keeps Spec, Tickets, and Wayfinder operations in separate sections of a shared [GitHub reference](skills/design/references/github.md). [The WF installer](install/install.md) sets up baseline labels, including a labels-only repair mode. Spec and ticket publishing can explicitly fall back to local Markdown, reporting offline or partial publication rather than GitHub success. [research](skills/research/SKILL.md) and [index-docs](skills/index-docs/SKILL.md) initialization remain local-document workflows. Other skills' Jira metadata and workflows are unchanged.

[subagents](skills/subagents/SKILL.md) owns worker dispatch, model roles, Arena candidate comparison, and Swarm partition or race runs. [research](skills/research/SKILL.md) owns How for current code behavior and Why for historical rationale alongside its existing inspection routes.

[`/design grill`](skills/design/SKILL.md) owns session-ledger operations through its [track-ledger reference](skills/design/references/track-ledger.md), including ownership, resumable questions, and pending writes. It loads closing, verification, and external-source procedures on demand from its bundled references. To configure a `grill!` shortcut, point it to `/design grill`.

Its interview presents the entire ready decision frontier as one numbered batch per round, with recommendations phrased for "yes" to accept. Dependent questions wait for later rounds; partial answers leave the remaining ready questions together for batched follow-up. Inline recording and user-controlled closure remain unchanged.

[record-architecture](skills/record-architecture/SKILL.md) replaces the seven standalone architecture record/render commands. Its modes are `adr`, `building-block`, `deployment-view`, `term`, `concept-body`, `concept-record`, and `decision-bullet`; the two render-only modes never save files or update indexes. Explicit modes take precedence, clear natural-language requests route automatically, and ambiguous requests prompt for the intended artifact. [define-concept](skills/define-concept/SKILL.md) still owns concept discovery and questioning; recording settled knowledge does not repeat the interview.

The [Feature design tactic](skills/draft-artifact/SKILL.md) renders slice decision bullets from its bundled decision reference, without invoking the recording skill.

[github](skills/github/SKILL.md) provides Git conventions and one CLI for Git and GitHub operations. [Review](skills/review/SKILL.md) routes PR code review, comment follow-up, blast radius, test gaps, architecture drift, and human-led review through one skill. Use `/design review` to review a technical design for gaps and implementation readiness.

## Skill flow

1. **Discovery loop** — resolving unknowns before a spec or design is clear has two mechanics for the same purpose: [`/design wayfinder`](skills/design/SKILL.md) charts a map of decision tickets on the issue tracker for work too big for one session, resolving each ticket via `/design grill`, `/research`, or `/experiment`; `/design grill` run directly interviews a smaller effort in one session, with no map or tickets. Either way, once no unknowns are left, the next step is `/design spec` (or `/draft-artifact design` directly).
2. **Spec synthesis** — `/design spec` synthesizes the spec from the resolved Wayfinder decisions or Grill conversation, the step right after the discovery loop; a spec can feed `/design tickets` directly or go on into design synthesis.
3. **Design synthesis** — `/draft-artifact design` combines resolved Wayfinder decisions and one or more specs into an authoritative feature design, reconciling capabilities and merging stronger evidence into an existing design.
4. **Story breakdown** — `/factory-mode stories` ([Stories playbook](install/assets/factory-mode/playbooks/stories.md), installed per repo) accepts requirements, `/design spec` output, or `/draft-artifact design` output and assembles an approved ordered story list with numbered headings, dependencies, and Jira metadata; it runs [`draft-artifact`](skills/draft-artifact/SKILL.md) in Story mode once per approved row. Use `/draft-artifact story` for a standalone User story.
5. **Story hardening** — `/design grill` interviews and sharpens each story, run once per story.
6. **Ticket cut** — `/design tickets` proposes implementation slices from a spec and creates GitHub sub-issues after approval.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-idea-to-implementation-swimlane
swimlane-beta TB
  accTitle: Idea to implementation responsibility
  accDescr: Shows discovery choosing a simple or complex path, each producing a spec that implement turns into an implementation.

  subgraph discovery [Discovery]
    idea([Idea])
    resolve[1 - Resolve unknowns<br/>/design wayfinder or /design grill]
    choosePath{2 - Choose path}
  end

  subgraph simple [Simple path - SMPL]
    sketchFirst{2a.1 - Sketch code first?}
    smplArchitect[2a.1a.1 - architect<br/>code sketch]
    smplToSpec[2a.2 - /design spec]
    smplSpec[(2a.3 - Spec)]
  end

  subgraph complex [Complex path - CMPLX]
    toZdesign[2b.1 - draft-artifact design<br/>synthesize or merge feature design]
    design[(2b.2 - Feature design)]
    toStories[2b.3 - factory-mode stories<br/>assemble design into stories]
    cmplxArchitect[2b.4 - architect<br/>for each story]
    cmplxToSpec[2b.5 - /design spec]
    cmplxSpec[(2b.6 - Spec)]
  end

  subgraph implementation [Implementation]
    implementSpec[3 - implement<br/>sequential or parallel]
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

Resolves unknowns with `/design wayfinder` (work too big for one session) or `/design grill` (one session), synthesizes the feature design with `/draft-artifact design`, then breaks the design into User stories with `/factory-mode stories`.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-design-to-stories-swimlane
swimlane-beta TB
  accTitle: Design and story breakdown responsibility
  accDescr: Shows unknowns resolved by /design wayfinder or /design grill, a feature design synthesized by draft-artifact design, and the design broken down into User stories by the factory-mode Stories playbook.

  subgraph discovery [Discovery]
    idea([Idea])
    effortSize{1 - Fits one session?}
    wayfinder[1a.1 - /design wayfinder<br/>chart and resolve decision tickets]
    grillDesign[1b.1 - /design grill<br/>interview in one session]
  end

  subgraph design [Design]
    toZdesign[2 - draft-artifact design<br/>synthesize or merge feature design]
    designDoc[(3 - Feature design)]
  end

  subgraph breakdown [Story breakdown]
    toStories[4 - factory-mode stories<br/>assemble ordered story list]
    draftStory[[5 - draft-artifact story<br/>once per approved row]]
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

Starts from one existing User story: `/writing-style sharpen` hardens it, `/architect` sketches the code, `/design spec` writes the spec, and `/implement` implements it.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-story-to-implementation-swimlane
swimlane-beta TB
  accTitle: Story to implementation responsibility
  accDescr: Shows one User story sharpened, sketched by architect, turned into a spec, and implemented by implement.

  subgraph story [Story hardening]
    userStory([User story])
    sharpen[1 - writing-style sharpen]
  end

  subgraph design [Design]
    architect[2 - architect<br/>code sketch]
    toSpec[3 - /design spec]
    spec[(4 - Spec)]
  end

  subgraph implementation [Implementation]
    implementSpec[5 - implement]
    done([Implementation])
  end

  userStory --> sharpen -->|sharpened story| architect --> toSpec --> spec -->|spec| implementSpec --> done

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
```

### Story to direct implementation

Starts from one existing User story with no spec: `/writing-style sharpen` hardens it, `/architect` sketches the code, and the **implement** reply makes `/architect` build against the accepted sketch in the current branch. It commits the scaffold first, then fills in code, surfacing every deviation from the sketch. If the same friction keeps coming back, it scraps the sketch and re-runs the design. Replying **accept** instead follows Story to implementation.

```mermaid
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: wf-story-to-direct-implementation-swimlane
swimlane-beta TB
  accTitle: Story to direct implementation responsibility
  accDescr: Shows one User story sharpened, sketched and reviewed by architect, then implemented by architect against the accepted sketch, with scrap and redesign on repeated friction.

  subgraph story [Story hardening]
    userStory([User story])
    sharpen[1 - writing-style sharpen]
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

| Task | Entry |
| --- | --- |
| Architecture, behavior, or code diagrams | `/doc-diagram <diagram type>` with optional current or delta mode |
| Initialize docs | `/index-docs Initialize missing docs` |
| Story, bug report, feature handover, or feature design | `/draft-artifact story`, `/draft-artifact bug`, `/draft-artifact toi`, `/draft-artifact design` |
| Deepen a task prompt or restate intent | `/writing-style sharpen` |

Diagram examples: [architecture](skills/doc-diagram/examples/architecture.md), [behavior](skills/doc-diagram/examples/behavior.md), and [code](skills/doc-diagram/examples/code.md).

| Group | Skills |
| --- | --- |
| Discovery and research | `define-concept`, `define-research`, `experiment`, `explore-codebase` (NuGet tactic), `research` |
| Design and backlog | `architect`, `design` (`grill`, `spec`, `tickets`, `wayfinder`, `review`); `factory-mode` Stories playbook (repo-level) |
| Documentation and drafting | `doc-contracts`, `doc-diagram`, `draft-artifact`, `index-docs`, `record-architecture`, `writing-style` |
| Implementation and tooling | `diagnosing-bugs`, `github`, `implement`, `principles`, `show-me-your-work`, `subagents` |
