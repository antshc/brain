# Architecture Diagram

## System Context Diagram

Show the system under design as a single box with the actors and external systems around it. Use when the question is scope and integration boundaries, not internal structure.

## Container Diagram

Show deployable/runnable containers and the actors or external systems around them at solution level.

## Component Diagram

Decompose one selected deployable into architecturally relevant components and their dependencies. Use when internal responsibilities inside that deployable matter; keep method-level detail out.

## Deployment View

Show deployment topology, hosting, runtime, or infrastructure placement. Model the view with Mermaid `C4Deployment` using deployment nodes and deployed containers.

## Reference

Official Mermaid C4 syntax: https://mermaid.ai/open-source/syntax/c4.html


## Delta routing

System Context is current-mode only. For a System Context delta, select Container when the change affects deployables or Component when it affects responsibilities inside one deployable.

## Rendering

Use `C4Component` for Component and show one deployable boundary. Use `C4Deployment` for Deployment View and place deployed containers inside their hosting `Deployment_Node`/`Node`.

Put `%% diagram-id: {{diagramId}}` after the closing `---` of the config frontmatter and immediately above the Mermaid type line.
