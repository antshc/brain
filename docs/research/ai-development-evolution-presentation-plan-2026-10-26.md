# AI Development Evolution: Hand-Drawn Presentation Plan

Planning only. This document defines the visual guidelines and the seven-slide outline. It does not contain or authorize generation of slides, image assets, or a `.drawio` deck.

Source research: [AI Development Evolution Research (2026-10-25)](./ai-development-evolution-research-2026-10-25.md).

## Color and visual guidelines

**Theme:** draw.io **Hand-drawn**, styled as a clean engineering whiteboard on warm paper.

| Role | Color | Hex | Usage |
| --- | --- | --- | --- |
| Paper | Warm ivory | `#FAF8F2` | Consistent slide background |
| Ink | Charcoal | `#222B35` | Titles, labels, outlines, main connectors |
| Stage 1 | Slate | `#64748B` | Prompt & Context Engineering |
| Stage 2 | Blue | `#0284C7` | Agentic Development |
| Stage 3 | Amber | `#D97706` | Agentic Workflows |
| Stage 4 | Green | `#059669` | Agentic Software Factories |
| Warning | Red | `#EF4444` | Blockers, failures, caveats only |

- **MUST** use the same stage color throughout slides 2–6 and 7 where a stage is highlighted. Colors identify concepts, never decoration.
- **MUST** use 16:9 landscape pages, wide margins, one dominant drawing per slide, and short legible labels.
- **MUST** use rough marker-style outlines and sketch-style arrows consistently. Keep connector lines away from text.
- **MUST** maintain high contrast. Keep backgrounds neutral and use accent fills sparingly.
- **MUST** keep quantitative charts, diagrams, and text editable in draw.io when slides are eventually created.
- **MUST** use authentic project names and logos where available. Use sketch-style conceptual illustrations for mechanisms; avoid unrelated stock photos.
- **SHOULD** use Kalam or Patrick Hand for short headings and Inter for body labels. Fall back to a legible sans-serif when those fonts are unavailable.
- **SHOULD** use one main message per slide and place supporting explanations in presenter notes. Do not shrink text to fit an overcrowded diagram.
- **MUST NOT** generate real slides, `.drawio` files, or image assets as part of this planning step.

## Seven-slide plan

### 1. What Is the Software Development Life Cycle (SDLC)?

- **Key message:** Software delivery is a continuous lifecycle with feedback informing future work.
- **Content:** Planning, Requirements, Design, Implementation, Testing, Deployment, Operations, Feedback. Present these as a useful lifecycle model, not as the only formal SDLC definition.
- **Visual:** One large circular, hand-drawn lifecycle diagram with eight labeled phases and a clear feedback connection.

### 2. Four Stages of AI Software Development

- **Key message:** The unit of automation grows from reusable instructions to ongoing software delivery operations.
- **Content:**
  1. **Prompt & Context Engineering (slate):** Humans drive the work using reusable knowledge and instructions.
  2. **Agentic Development (blue):** Agents act on bounded engineering tasks and verify results.
  3. **Agentic Workflows (amber):** A process coordinates dependent SDLC activities, agents, and gates.
  4. **Agentic Software Factories (green):** Persistent event intake and durable orchestration operate delivery under human governance.
- **Visual:** Four hand-drawn stations along a single evolution path, with a one-line difference and control owner at each station.
- **Caveat:** The four stages are the source research's conceptual taxonomy, not an established industry standard.

### 3. GitHub Popularity and the Four-Stage Landscape

- **Key message:** Popularity, breadth of skills, and software-factory maturity measure different things.
- **Content:** Rank the five named skills creators by GitHub stars, show forks as a secondary value, and place projects in the four-stage landscape.
- **Popularity order from the research snapshot (2026-10-25):**
  1. Matt Pocock, **302,868 stars**, **25,471 forks** (Stage 3).
  2. Affaan Mustafa / ECC, **288,418 stars**, **42,762 forks** (Stage 3).
  3. Garry Tan / gstack, **137,622 stars**, **20,402 forks** (Stage 3).
  4. Addy Osmani / Agent Skills, **110,342 stars**, **11,516 forks** (Stage 3).
  5. Lauren Tan / pstack, **13,971 stars**, **1,396 forks** for the entire Cursor Plugins repository (Stage 2 with Stage 3 features).
- **Additional placements:** SSSF and super-board primarily at Stage 3; Warp Factories at Stage 4; Atlassian AI SDLC as a Stage 4 operating model; Teamwork Graph as a context foundation.
- **Visual:** Hand-drawn horizontal ranking bars on one side and an aligned four-stage project landscape on the other.
- **Caveats:** pstack's metrics are a proxy for Cursor Plugins, not individual pstack popularity. Stars and forks do not demonstrate product quality or maturity. Warp Factories was described as early access in the research.

### 4. Agentic Workflow

- **Key message:** A workflow controls the engineering sequence, delegation, and gates for a bounded run.
- **Content:** Human/workflow trigger, specification, planning, implementation, verification, code review, and delivery. Highlight dependencies, fan-out/fan-in, and human approvals.
- **Visual:** A sketch-style SDLC conveyor belt with specialized agents at stations and verification gates between phases.
- **Distinction:** A workflow can run autonomously once started without continuously listening for new external work.

### 5. Agentic Software Factory

- **Key message:** The factory operates the delivery lifecycle persistently and responds to new work and feedback.
- **Content:** GitHub/user/scheduled events, intake, durable queue/state, orchestrator, isolated agent runs, deterministic checks, human approvals, release, observability, and feedback.
- **Visual:** A large hand-drawn software factory with incoming events, agent workstations, gates, an output conveyor, and a monitoring loop.
- **Examples:** Warp Factories and Atlassian's AI SDLC operating-model architecture, with their maturity and evidence limitations preserved.

### 6. Core Principles of Agentic Systems

- **Key message:** Reusable execution mechanisms underpin workflows and factories; durable event-driven operation completes the factory model.
- **Content:**
  - **Loop:** Execute, check results, retry or stop.
  - **Fan-out / Fan-in:** Parallelize independent work, then gather outcomes.
  - **Agent Team:** Assign bounded responsibilities to specialized agents.
  - **Ledger:** Persist state, decisions, evidence, and progress beyond one session.
  - **Self-improvement:** Use failures, reviews, and telemetry to improve later runs.
  - **Deterministic Gates:** Require explicit, verifiable conditions before transitions.
- **Visual:** Six hand-drawn mechanisms arranged around a simple orchestration sketch. Each mechanism has one icon and one short explanation.

### 7. Matt Pocock's Skills: Composable Agentic Workflows

- **Key message:** Specialized skills support discovery, design decisions, work breakdown, implementation orchestration, and review.
- **Content:**
  - **grill-with-docs:** Interview within a repository, clarify terminology, and record a glossary and ADRs.
  - **wayfinder:** Map an uncertain, multi-session effort into dependent decision tickets.
  - **to-spec:** Convert settled decisions into a specification.
  - **to-tickets:** Break a specification into implementation tickets.
  - **implement-spec:** Coordinate implementation of the specification.
  - **code-review:** Run separate standards and specification-compliance reviews of a diff.
- **Visual:** Two alternative planning on-ramps, **grill-with-docs** for a one-session effort and **wayfinder** for a large multi-session effort, converging into **to-spec → to-tickets → implement-spec → code-review**. Depict the workflow with hand-drawn document, ticket, agent, and review icons.
- **Scope:** Do not feature the standalone **implement** skill.
- **Source:** [Matt Pocock's Skills](https://github.com/mattpocock/skills); [grill-with-docs](https://github.com/mattpocock/skills/blob/main/docs/engineering/grill-with-docs.md); [wayfinder](https://github.com/mattpocock/skills/blob/main/docs/engineering/wayfinder.md); [code-review](https://github.com/mattpocock/skills/blob/main/docs/engineering/code-review.md).
