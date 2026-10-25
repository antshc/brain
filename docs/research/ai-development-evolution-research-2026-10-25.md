# Research: From Prompt Engineering to Agentic Software Factories

**Research date:** October 25, 2026  
**Scope:** The five named AI-skills creators, two open-source orchestration projects, Warp and Warp Factories, and Atlassian Jira / Teamwork Graph / AI SDLC guidance.  
**Method:** Review of the supplied project documentation and first-party product material; GitHub stars and forks retrieved from the GitHub repository API on the research date.

## Executive finding

The useful distinction is **instructions → task execution → process orchestration → an operating system for software delivery**. A skills collection can cover many stages; its highest-level commands do not necessarily turn it into an always-running factory. Conversely, a product called a “factory” may implement only agentic workflows today.

This four-stage model is a **conceptual taxonomy**, not a formal industry standard. Anthropic distinguishes predefined *workflows* from agents that dynamically direct actions; Atlassian describes an AI-native SDLC that combines enterprise context, workflow changes, measurement, and human judgment. [Anthropic](https://www.anthropic.com/research/building-effective-agents) · [Atlassian AI SDLC playbook](https://www.atlassian.com/blog/ai-at-work/ai-sdlc-transformation-playbook)

## Stage 1 — Prompt & Context Engineering

- **What changes:** The AI moves from isolated prompts to reusable instructions, repository rules, documentation, and connected organizational knowledge.
- **Control:** The human drives execution and supplies the relevant context.
- **Typical mechanisms:** Skill files, project instructions, terminology, retrieval, connected knowledge sources.
- **Why this is a separate stage:** Better context improves decisions, but it does not confer authority to take action or run a multi-step process.
- **Resources:** The `context-engineering` skill in [Addy Osmani's Agent Skills](https://github.com/addyosmani/agent-skills); domain modeling and agent writing in [Matt Pocock's Skills](https://github.com/mattpocock/skills); [Atlassian Teamwork Graph](https://www.atlassian.com/platform/teamwork-graph), which relates issues, code, documents, people, and decisions under permissions.

**Evidence-based distinction:** Teamwork Graph is a **context foundation**, not on its own a software factory. Atlassian uses it to make work and code context available to agents through apps, MCP, and CLI. [Atlassian Teamwork Graph](https://www.atlassian.com/platform/teamwork-graph) · [Atlassian playbook](https://www.atlassian.com/blog/ai-at-work/ai-sdlc-transformation-playbook)

## Stage 2 — Agentic Development

- **What changes:** A coding agent can inspect a repository, change code, use tools, run tests, and retry after failures.
- **Control:** The agent drives execution of a bounded engineering task; a developer still supplies the task and decisions that need human judgment.
- **Typical mechanisms:** Tool access, TDD, debugging loops, browser/UI verification, code-review subagents, parallel attempts.
- **Why this is a separate stage:** The AI now *acts on the environment* and verifies outcomes instead of returning advice or generated text.
- **Primary example:** [Lauren Tan (poteto)'s pstack](https://github.com/cursor/plugins/tree/main/pstack). Its `poteto-mode` routes to engineering disciplines such as architecture, adversarial investigation, TDD, parallel `swarm`/`arena`, and PR babysitting. This is primarily an agentic engineering toolkit rather than a persistent SDLC runtime.
- **Important nuance:** pstack also includes an **optional, dormant** `benny` automation pack for Slack-triggered triage and bounded bug fixes. That is a Stage 4-style integration when explicitly installed on Cursor Automations; it is not proof that pstack's core skills continuously run by themselves. [pstack README](https://github.com/cursor/plugins/blob/main/pstack/README.md) · [benny automation specification](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/FOR_AGENTS.md)

## Stage 3 — Agentic Workflows

- **What changes:** Individual agent tasks become a governed SDLC process: intake, specification, planning, implementation, testing, review, and handoff.
- **Control:** A human or defined workflow typically initiates a run; the workflow determines the steps, agents, dependencies, quality gates, and approvals.
- **Typical mechanisms:** Reusable process skills, task graphs, worktrees, phased execution, typed agent handoffs, automated review and evidence gates.
- **Why this is a separate stage:** The unit of automation shifts from **one task** to **a sequence of dependent engineering activities**.

### Sources classified primarily at Stage 3

1. **[Matt Pocock — Skills](https://github.com/mattpocock/skills).** `/to-spec`, `/to-tickets`, `/implement`, and `/implement-spec` coordinate work from a spec through task-graph implementation, parallel subagents, and review. The documentation deliberately emphasizes small composable human-invoked skills rather than an always-on process owner. **Reason:** process-level coordination exists, but no autonomous event-driven factory runtime is provided by the repository.
2. **[Affaan Mustafa — Everything Claude Code (ECC)](https://github.com/affaan-m/ECC).** A broad agent harness with specialized subagents, reusable skills, rules, hooks, and orchestration scripts. Its README reports 71 agents, 311 skills, and 97 maintained command shims at the time of review. **Reason:** substantial reusable engineering execution infrastructure, but skill/harness breadth does not alone establish continuously triggered end-to-end factory operations.
3. **[Garry Tan — gstack](https://github.com/garrytan/gstack).** Explicit sprint sequence: Think → Plan → Build → Review → Test → Ship → Reflect. Role-oriented engineering, product, design, QA, and release skills, with parallel sprint support. **Reason:** coherent multi-phase engineering process, generally initiated and steered by a human.
4. **[Addy Osmani — Agent Skills](https://github.com/addyosmani/agent-skills).** Twenty-five reusable skills and nine lifecycle commands across Define → Plan → Build → Verify → Review → Ship. `/build auto` can plan and complete the implementation in a bounded autonomous pass after approval. **Reason:** workflow composition and verification gates, not a standalone persistent event-processing platform.
5. **[Super Simple Software Factory (SSSF)](https://github.com/antshc/super-simple-software-factory/tree/main/.claude/skills/sssf).** Deterministic Python owns phase sequencing, typed envelopes, gate checks, retries, and SQLite run traces while coding agents work inside bounded steps. The documented v1 uses Pi; Claude Code integration is a stub and the visualizer is planned for a later pass. **Reason:** an agentic workflow engine / factory prototype, but the reviewed skill does not establish an always-on event-triggered SDLC.
6. **[EricTechPro — super-board](https://github.com/EricTechPro/super-board).** GitHub Project board as durable task state, autonomous Build → QA → Review waves, merge guards, evidence, and resume. It is started with `/super-board run`, which can drain a board. **Reason:** an advanced bridge toward factories; the documented default is a user-started autonomous workflow, not proof of continuously listening to external events.

**Boundary case:** pstack spans Stage 2 and parts of Stage 3 because `poteto-mode` coordinates specialized practices and PR follow-up. The optional `benny` automation extends into Stage 4 mechanisms.

## Stage 4 — Agentic Software Factories

- **What changes:** A persistent system accepts work from external events and coordinates agents over the delivery lifecycle without a person invoking every task.
- **Control:** Human governance sets objectives, risk boundaries, and approval gates; the system controls intake, scheduling, execution environments, retries, handoffs, evidence, monitoring, and continued progression.
- **Typical mechanisms:** Webhooks and schedules; durable queues/state; isolated compute; integrations with issue trackers and source control; permission and approval policies; observability; evaluation; continuous feedback.
- **Why this is a separate stage:** The unit of automation becomes **software delivery as an ongoing operational service**, not just a manually started workflow.

### Sources classified primarily at Stage 4

1. **[Warp Factories](https://www.warp.dev/factories)** (separate from the general [Warp open-source agentic development environment](https://github.com/warpdotdev/warp)). Its first-party documentation describes factories-as-code, triggers from existing tools, a foreman-led triage → spec → implement → verify → ship → monitor path, sandboxes, agent/model choice, evaluations, benchmarks, approvals, and self-improvement. **Reason:** it explicitly combines event-based intake, operational execution, governance, and feedback. **Maturity caveat:** the factory offering advertises early access; product claims are not independent performance verification.
2. **[Atlassian AI SDLC transformation playbook](https://www.atlassian.com/blog/ai-at-work/ai-sdlc-transformation-playbook)**, with [Jira](https://www.atlassian.com/software/jira), [Rovo](https://www.atlassian.com/software/rovo), and [Teamwork Graph](https://www.atlassian.com/platform/teamwork-graph). The playbook integrates connected context and measurement with planning, design, development, review, and proactive maintenance. Jira supplies tracked work and approvals; Teamwork Graph supplies permission-aware organizational context. **Reason:** this is a Stage 4 *operating-model architecture*, not evidence that Teamwork Graph alone is a complete factory product. Atlassian reports internal governed agent loops and outcomes, but these are vendor-reported results.

### Minimum credible factory boundary

The following checks distinguish a deployed factory from a good skill collection or one-off workflow:

1. Work can enter automatically from an event or schedule.
2. Runs, dependencies, progress, and recovery state persist beyond one agent session.
3. Execution is isolated and permissions are bounded.
4. Verifiable tests, checks, evidence, and human approvals govern transitions.
5. Monitoring, traces, failure detection, and audit history are available.
6. Feedback from CI, PRs, or production can generate follow-up work and improve the process.

This is a proposed evaluation rubric synthesized from the Warp and Atlassian descriptions, **not an industry certification checklist**.

## GitHub popularity — five named skills creators

**Snapshot date:** October 25, 2026. **Primary ranking: stars, descending.** Fork rank is shown separately because its order differs.

| Stars rank | Creator | AI-skills repository | Stars | Forks | Forks rank | Primary stage |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| 1 | Matt Pocock | [mattpocock/skills](https://github.com/mattpocock/skills) | 302,868 | 25,471 | 2 | 3 |
| 2 | Affaan Mustafa | [affaan-m/ECC](https://github.com/affaan-m/ECC) | 288,418 | 42,762 | 1 | 3 |
| 3 | Garry Tan | [garrytan/gstack](https://github.com/garrytan/gstack) | 137,622 | 20,402 | 3 | 3 |
| 4 | Addy Osmani | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 110,342 | 11,516 | 4 | 3 |
| 5* | Lauren Tan (poteto) | [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) | 13,971* | 1,396* | 5* | 2 → 3 |

**Critical metric caveat:** pstack is a **subdirectory** of `cursor/plugins`. Its stars and forks are the metrics for the **entire Cursor Plugins repository**, not for pstack itself. The fifth row is a labeled proxy, **not a valid apples-to-apples individual creator ranking**. No separate public `poteto/pstack` repository was found at the tested repository path. Repository stars and forks represent popularity/interest, not code correctness, adoption, or SDLC maturity.

The stars ordering is Matt → Affaan → Garry → Addy → Cursor Plugins proxy. The forks ordering is **Affaan → Matt → Garry → Addy → Cursor Plugins proxy**.

### Grouped by primary evolution stage

- **Stage 1:** No listed creator is *only* a prompt/context resource. All five contain reusable instructions or context practices.
- **Stage 2:** Lauren Tan / pstack (primary emphasis on agentic engineering rigor and tool-using coding; Stage 3 orchestration features and optional automations also exist).
- **Stage 3** (ordered by stars): Matt Pocock; Affaan Mustafa; Garry Tan; Addy Osmani. SSSF and super-board are additional workflow-oriented projects, not part of the five-creator ranking.
- **Stage 4:** No one of the five standalone skills repositories is best classified as a complete persistent software factory. Warp Factories and Atlassian's AI-native SDLC operating model are the clearest Stage 4 references in this source set.

**Other GitHub repositories (not part of the five-creator ranking):** [warpdotdev/warp](https://github.com/warpdotdev/warp) had 65,692 stars / 5,700 forks; [EricTechPro/super-board](https://github.com/EricTechPro/super-board) had 489 / 143; [antshc/super-simple-software-factory](https://github.com/antshc/super-simple-software-factory) had 0 / 0. The Warp repository metrics cover its broader open-source client, **not solely Warp Factories**.

## What these sources actually support

### Directly observable in the sources

- The five named skills sources all include actionable engineering skills; several include explicit development life-cycle workflows, agents, or subagents.
- Matt, Addy, Garry, and Affaan document repeatable multi-step engineering processes.
- SSSF documents deterministic phase control, typed handoffs, and verification gates.
- super-board documents board-driven task waves and a start/resume command.
- Warp markets a persistent, event-driven factory control plane and a triage-to-monitor lifecycle.
- Atlassian presents context + measurement + workflow shifts as two connected requirements of AI-native delivery.

### Interpretations, not independently verified claims

- Placing an individual project in a stage is an architectural inference based on the reviewed documentation, not a vendor-issued certification.
- Repository stars and forks cannot show which project creates higher quality software or which has more active production installations.
- Vendor-reported improvements (such as Atlassian's Teamwork Graph benchmark or Warp's cost stories) should not be treated as independent cross-vendor benchmarks.
- Branding a package a “factory” does not establish event-driven durability, monitored operation, or production readiness.

## Bottom line

**Facts:** The most-starred standalone skills repository in this set is Matt Pocock's (302,868); the most-forked is Affaan Mustafa's ECC (42,762). The pstack comparison is only a Cursor Plugins repository proxy. The documented open-source skill collections and manually started agent pipelines mainly occupy **Stages 2–3**, while Warp Factories and Atlassian's AI-native SDLC architecture address the broader **Stage 4** operating model.

**Reasoned conclusion:** The decisive move from *agentic workflows* to *agentic software factories* is not adding more prompts, skills, or subagents. It is adding persistent **event intake, durable state, governed execution, verification, observability, and feedback** so the SDLC can progress as a service under human oversight.

## Resource list

### Primary project sources

1. [Lauren Tan / pstack — Cursor Plugins](https://github.com/cursor/plugins/tree/main/pstack) · [automation specification](https://github.com/cursor/plugins/blob/main/pstack/automations/benny/FOR_AGENTS.md)
2. [Addy Osmani — Agent Skills](https://github.com/addyosmani/agent-skills)
3. [Matt Pocock — Skills](https://github.com/mattpocock/skills)
4. [Garry Tan — gstack](https://github.com/garrytan/gstack)
5. [Affaan Mustafa — Everything Claude Code](https://github.com/affaan-m/ECC)
6. [Super Simple Software Factory — SSSF skill](https://github.com/antshc/super-simple-software-factory/tree/main/.claude/skills/sssf)
7. [EricTechPro — super-board](https://github.com/EricTechPro/super-board)
8. [Warp open-source repository](https://github.com/warpdotdev/warp) · [Warp Factories](https://www.warp.dev/factories)
9. [Atlassian Teamwork Graph](https://www.atlassian.com/platform/teamwork-graph) · [Rovo](https://www.atlassian.com/software/rovo) · [Jira](https://www.atlassian.com/software/jira)
10. [Atlassian — The AI SDLC transformation playbook (October 1, 2026)](https://www.atlassian.com/blog/ai-at-work/ai-sdlc-transformation-playbook)

### Conceptual foundation

- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents): workflow/agent architectural distinction.
- [OpenAI — Agents guide](https://developers.openai.com/api/docs/guides/agents): tools, state, orchestration, runtime boundaries.
- [OpenAI — Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals): checks and human approval boundaries.

### GitHub popularity data

- Primary values: GitHub REST repository metadata for [mattpocock/skills](https://api.github.com/repos/mattpocock/skills), [affaan-m/ECC](https://api.github.com/repos/affaan-m/ECC), [garrytan/gstack](https://api.github.com/repos/garrytan/gstack), [addyosmani/agent-skills](https://api.github.com/repos/addyosmani/agent-skills), and [cursor/plugins](https://api.github.com/repos/cursor/plugins), collected October 25, 2026.
