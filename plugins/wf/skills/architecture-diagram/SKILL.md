---
name: architecture-diagram
description: Document software architecture with a Mermaid system context diagram, solution-level container diagram, or deployment view. Use for system landscape and scope questions, current-state architecture, and architecture deltas, including added, removed, or modified containers, systems, actors, relationships, hosts, runtimes, or deployment nodes.
---

# Architecture Diagram

## When to use

Use this skill to document software architecture as either:

### System Context Diagram

Show the system under design as a single box with the actors and external systems around it. Use when the question is scope and integration boundaries, not internal structure.

### Container Diagram

Show deployable/runnable containers and the actors or external systems around them at solution level.

### Deployment View

Show deployment topology, hosting, runtime, or infrastructure placement. Model the view with Mermaid `C4Deployment` using deployment nodes and deployed containers.

## Reference

Official Mermaid C4 syntax: https://mermaid.ai/open-source/syntax/c4.html

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including requests such as `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show the relevant current architecture.
- **Delta mode:** show only added, modified, or removed elements, plus the minimum unchanged context needed to connect them.

System Context is current-mode only; a delta request selects the Container Diagram view.

## 2. Select view and open its template

### System Context Diagram

Open [system-context-template.md](templates/system-context-template.md).

### Container Diagram

Open [container-diagram-template.md](templates/container-diagram-template.md).

### Deployment View

Open [deployment-view-template.md](templates/deployment-view-template.md). Render deployment views with Mermaid `C4Deployment`; use `Deployment_Node`/`Node` for deployment topology and place deployed containers inside the node that hosts them.

Open the selected template before drafting. Follow its drawing, styling, delta, and Mermaid rules; do not compose from memory.

Ground current-state elements in the actual codebase or repository evidence. Do not guess. Show only elements relevant to what is being documented.

**Done when:** the selected template was opened this run; the selected view follows its rules; current mode uses the base palette; delta mode uses the delta rules and minimum context and was drawn as a Container Diagram or Deployment View, never a System Context Diagram; Deployment View uses `C4Deployment`; no unused placeholder or instruction-only comment remains.
