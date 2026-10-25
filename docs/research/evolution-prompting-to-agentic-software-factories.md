# Evolution from Prompting to Agentic Software Factories

A conceptual four-stage maturity path for AI-assisted software engineering. The stages describe the increasing autonomy and scope of AI systems, not a formal industry standard.

## 1. Prompt & Context Engineering

- Humans provide prompts, instructions, project context, and knowledge.
- AI generates answers, designs, and code.
- Reusable guidance and shared domain vocabulary improve the consistency of responses.
- **Main difference:** AI understands what to do, but humans drive execution.

## 2. Agentic Development

- AI agents inspect code, implement features, execute tools, and run tests.
- Autonomous feedback loops enable agents to evaluate results and correct failures.
- Specialized agents can collaborate, delegate, and review one another's work.
- **Main difference:** AI executes development tasks autonomously.

## 3. Agentic Workflows

- Agents coordinate SDLC activities such as specification, planning, implementation, testing, and review.
- Workflows manage dependencies, handoffs, quality gates, and human approvals.
- Defined process boundaries make multi-step delivery repeatable and observable.
- **Main difference:** AI orchestrates development processes, not just individual tasks.

## 4. Agentic Software Factories

- Event-driven automation connects the SDLC end to end.
- Agents react to issues, pull requests, CI failures, user feedback, and operational events.
- The system supports continuous execution, monitoring, verification, recovery, and improvement.
- Humans govern goals, constraints, risk policies, and critical decisions.
- **Main difference:** AI operates the software delivery lifecycle, with humans governing goals and critical decisions.

## Fundamental Evolution

| Stage | Control model | Core shift |
| --- | --- | --- |
| 1. Prompt & Context Engineering | Human drives AI | Instructions |
| 2. Agentic Development | AI executes tasks | Execution |
| 3. Agentic Workflows | AI orchestrates processes | Orchestration |
| 4. Agentic Software Factories | AI operates software delivery | Autonomous delivery |

**Core progression:** Instructions → Execution → Orchestration → Autonomous Delivery.

## Distinctions and Examples

- A skill collection, such as [Matt Pocock's engineering skills](https://github.com/mattpocock/skills), can span multiple stages. Its reusable instructions support context engineering; coding and verification skills support agentic development; and its spec, ticket, implementation, and review sequences support agentic workflows.
- An event-driven SDLC is a capability of a software factory, not necessarily a separate evolution stage.
- A software factory needs more than agent instructions: it also needs persistent orchestration, event handling, state management, execution environments, verification, observability, and human governance.
- Greater autonomy does not eliminate human involvement. Human approvals remain important at risk-sensitive or ambiguous decisions.

## References

- [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents): distinguishes predefined workflows from agents that dynamically direct their actions.
- [OpenAI — Agents](https://developers.openai.com/api/docs/guides/agents): agent runtimes, tools, state, and orchestration.
- [OpenAI — Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals): automatic checks and human-in-the-loop approval boundaries.
- [Matt Pocock — Skills for Real Engineers](https://github.com/mattpocock/skills): composable engineering skills and workflows.
