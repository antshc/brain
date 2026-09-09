---
name: architecture-diagram
description: Document software architecture with a Mermaid solution-level container diagram or deployment view. Use for current-state architecture and architecture deltas, including added, removed, or modified containers, systems, actors, relationships, hosts, runtimes, or deployment nodes.
---

# Architecture Diagram

## When to use

Use this skill to document software architecture as either:

### Container Diagram

Show deployable/runnable containers and the actors or external systems around them at solution level.

### Deployment View

Show deployment topology, hosting, runtime, or infrastructure placement. Model the view with Mermaid `C4Container` using the deployment-view template.

## Reference

Official Mermaid C4 syntax: https://mermaid.ai/open-source/syntax/c4.html

## 1. Select mode

Use **current mode** by default.

Use **delta mode** when the user asks for a delta or change-focused diagram, including requests such as `diagram the delta`, `show what changed`, `show changes`, or `show added/removed/modified elements`.

- **Current mode:** show the relevant current architecture.
- **Delta mode:** show only added, modified, or removed elements, plus the minimum unchanged context needed to connect them.

## 2. Select view and open its template

### Container Diagram

Open [container-diagram-template.md](templates/container-diagram-template.md).

### Deployment View

Open [deployment-view-template.md](templates/deployment-view-template.md). The deployment view is still rendered with Mermaid `C4Container`; the template defines deployment-specific modeling rules.

Open the selected template before drafting. Follow its drawing, styling, delta, and Mermaid rules; do not compose from memory.

Ground current-state elements in the actual codebase or repository evidence. Do not guess. Show only elements relevant to what is being documented.

**Done when:** the selected template was opened this run; the selected view follows its rules; current mode uses the base palette; delta mode uses the delta rules and minimum context; no unused placeholder or instruction-only comment remains.
