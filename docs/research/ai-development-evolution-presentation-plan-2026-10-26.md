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
  3. **Agentic Workflows (amber):** Coordinate agents and engineering activities to complete a defined process.
  4. **Agentic Software Factories (green):** Operate repeatable software delivery across work items, workflows, policies, and feedback.
- **Visual:** Four hand-drawn stations along a single evolution path, with a one-line difference and control owner at each station.
- **Caveat:** The four stages are a presentation taxonomy, not an industry standard or strict linear maturity ladder. Event triggers, persistent state, and human approvals can exist in Stage 3 workflows; Stage 4 manages delivery across runs.

### 3. GitHub Popularity and the Four-Stage Landscape

- **Key message:** Popularity, breadth of skills, and software-factory maturity measure different things.
- **Content:** Rank the five named skills creators by GitHub stars, show forks as a secondary value, and place projects in the four-stage landscape.
- **Popularity order from the research snapshot (2026-10-25):**
  1. Matt Pocock, **302,868 stars**, **25,471 forks** (Stage 3).
  2. Affaan Mustafa / ECC, **288,418 stars**, **42,762 forks** (Stage 3).
  3. Garry Tan / gstack, **137,622 stars**, **20,402 forks** (Stage 3).
  4. Addy Osmani / Agent Skills, **110,342 stars**, **11,516 forks** (Stage 3).
  5. Lauren Tan / pstack, **13,971 stars**, **1,396 forks** for the entire Cursor Plugins repository (Stage 2 with Stage 3 features).
- **Additional placements:** SSSF primarily at Stage 3; super-board is a Stage 3/factory-leaning boundary case; Warp Factories is a Stage 4 platform example; Atlassian AI SDLC is a Stage 4 operating-model example, not a single factory product; Teamwork Graph is a context foundation.
- **Visual:** Hand-drawn horizontal ranking bars on one side and an aligned four-stage project landscape on the other.
- **Caveats:** pstack's metrics are a proxy for Cursor Plugins, not individual pstack popularity. Stars and forks do not demonstrate product quality or maturity. Stage assignments are interpretive and can overlap. Warp Factories is early access.

### 4. Agentic Workflow

- **Key message:** A workflow coordinates one bounded engineering process, regardless of how it starts.
- **Content:** Manual, API, event, or scheduled trigger; specification, planning, implementation, verification, review, and PR handoff. Highlight dependencies, fan-out/fan-in, retries, checkpoints, and human approvals.
- **Visual:** A sketch-style SDLC conveyor belt with specialized agents at stations and verification gates between phases, clearly labeled as *one workflow run*.
- **Distinction:** A workflow may be durable, event-triggered, and autonomous within scope. Those capabilities do not alone make it a factory.

### 5. Agentic Software Factory

- **Key message:** A factory operates repeatable delivery across many work items and workflows under shared governance and measurement.
- **Content:** User/issues/PRs/incidents/scheduled inputs; standardized intake, priorities, policies, durable work-item state, multiple workflow runs, isolated execution, explicit CI/security gates, human approvals, PR handoff, operational metrics, and evaluated improvement.
- **Visual:** A large hand-drawn software factory showing multiple incoming work streams feeding shared management, three reusable Stage 3 workflow stations, approved PR outputs, and a measurement/feedback loop. Draw deployment and production monitoring as optional downstream integrations.
- **Examples:** Warp Factories (early-access platform; returns PRs and does not merge) and Atlassian's AI SDLC (operating-model architecture, not a standalone factory product).
- **Reference:** Use the [Stage 3 vs. Stage 4 comparison screenshot](./ai-development-evolution-presentation-plan-2026-10-26/1000017425.jpg) for conceptual structure only; it contains phone UI chrome and is not a slide-ready image.

### 6. Core Principles of Agentic Systems

- **Key message:** Workflows and factories share execution mechanisms; cross-run governance, delivery metrics, and systematic improvement characterize the factory operating model.
- **Content:**
  - **Loop:** Execute, check results, retry or stop.
  - **Fan-out / Fan-in:** Parallelize independent work, then gather outcomes.
  - **Agent Team:** Assign bounded responsibilities to specialized agents.
  - **Ledger:** Persist state, decisions, evidence, and progress; useful in both workflows and factories.
  - **Self-improvement:** Evaluate failures, reviews, and telemetry; propose and validate changes before adoption.
  - **Deterministic Gates:** Enforce explicit CI/test/policy conditions; distinguish from probabilistic agent reviews and human judgment.
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
