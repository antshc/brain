# Design Output Template

Instantiate this template at `docs/designs/{{featureSlug}}.md`. Remove every hidden instruction from the populated document.

````markdown
# {{featureName}}

<!-- The epic link (JIRA) in format [jira item id: title](link). -->

<details>
<summary>Reviewers</summary>

| **Role** | **Name** |
| --- | --- |
| Author (Feature Lead) | |
| Reviewers (Architect \ TL) | |
| PO | |
</details>

<!-- adf:toc -->

# Problem Statement and Goals

<!-- The problem that the user is facing, from the user's perspective, detail the motivation for the change, the issue or enhancement being addressed. Writing style: terse, concise, non-technical -->

{{problemAndGoals}}

# Glossary and Abbreviations

<details>
<summary>Glossary and Abbreviations</summary>

| **Term** | **Description** |
| --- | --- |
| {{term}} | {{description}} |

</details>

# Requirements

<!-- Keep this section fully synchronized with the PO. Make every requirement clear and self-explanatory; distinguish product requirements from technical requirements, and obtain PO approval for requirements from the development team. Use a top-level row for each stakeholder requirement and numbered sub-rows for its functional requirements. Italicize every functional sub-requirement. Leave Details empty on stakeholder requirement rows; only functional sub-requirement rows have Details. Render business rules as bullets and edge cases as bullets as unlabeled bullets lists in each functional sub-requirement's Details cell. Source is the requirement category (PO / Dev team), not source provenance. -->

<!-- adf:wide-table -->
| **#** | **Requirement** | **Priority** | **Details** | **Source** |
| --- | --- | --- | --- | --- |
| 1 | {{stakeholderRequirement\|states the desired outcome}} | {{priority\|MVP / Should have / Nice to have}} |  | {{requirementSource\|PO / Dev team}} |
| 1.1 | *{{functionalRequirement\|states the required behavior}}* | {{priority\|MVP / Should have / Nice to have}} | • {{businessRule\|State invariants, or None.}}<br>• {{edgeCase\|Boundary handling, or None.}} | {{requirementSource\|PO / Dev team}} |
| 1.2 | *{{functionalRequirement\|states the required behavior}}* | {{priority\|MVP / Should have / Nice to have}} | • {{businessRule\|State invariants, or None.}}<br>• {{edgeCase\|Boundary handling, or None.}} | {{requirementSource\|PO / Dev team}} |
| 2 | {{stakeholderRequirement\|states the desired outcome}} | {{priority\|MVP / Should have / Nice to have}} |  | {{requirementSource\|PO / Dev team}} |

# Assumptions and Limitations

<!-- List limitations: requirements the solution cannot meet because of constraints or drawbacks, such as high memory consumption or uncovered use cases. List assumptions: criteria that must be fully met for the solution to remain valid. -->

{{assumptionsAndLimitations}}

# Out of Scope

<!-- List items the proposed solution does not address but that the PO or other stakeholders might reasonably assume are included. -->

{{outOfScope}}

# Current State

<!-- Include the section only on user demand, otherwise remove section completely. if applicable, describe and diagram the application, component, or code area before the change. Visually distinguish components that this solution can change. -->

<details>
<summary>Current State</summary>

{{currentState}}

</details>

# Solution Overview

<!-- The solution to the problem, from the user's perspective. Writing style: terse, concise, non-technical -->

{{solutionOverview}}

<!-- A diagram is optional. This section is arc42's Building Block View. Include it when the solution spans multiple components and teams across the organization; otherwise include it only when the user explicitly requests it. Follow `/doc-architecture-diagram` skill use the Container Diagram (`C4Container`) for deployable building blocks in current mode; Beneath the representation, describe every shown building block's responsibility in a bullet with the building block name in bold. -->

{{architectureRepresentationDiagram}}

- **ElementName**: {{DiagramElementResponsibility| 1-3 sentences}}
- **ElementName**: {{DiagramElementResponsibility| 1-3 sentences}}

**{{the flow title| Cross Deployable Flow}}**

<!-- An optional section. Include only when a flow crosses multiple deployables. Follow `/doc-behavior-diagram` skill **Swimlane Diagram**; one lane per deployable, 1-5 major steps per lane. Do not compose a Mermaid skeleton from this template. -->

{{crossDeployableFlowDiagram}}

## Use cases
<!-- Describe where the user interacts with the feature and under what circumstances, such as install, create, upgrade, or undo operations. -->

- **{{Use case title}}**: {{Use case description}}

## {{functionalSliceTitle}}

<!-- Repeat the complete functional-slice block once or many times. Each slice owns one behavior and its decisions. Method-level behavior, Contracts details remains in Detailed Design. -->

<!-- Include exactly one current-mode behavior diagram for this slice. Follow `/doc-behavior-diagram` skill **Sequence Diagram** for flows visualization. The diagram title names the behavior without a `Flow Diagram:` or `Sequence Diagram:` prefix. Do not compose a Mermaid skeleton from this template. -->

{{functionalSliceBehaviorDiagram}}

**Decisions**

- **{{decisionName}}:** {{decisionContextAndRationale}}

# Testing Guidelines

<details>
<summary>Testing Guidelines</summary>

## Testing by Dev

<!-- Describe the development team's manual and automated testing, including unit, integration, and end-to-end coverage. -->

{{unitIntegrationAndEndToEndCoverage}}

## QA Testing Focus Areas

<!-- Identify QA focus areas and regression areas. If testing can proceed incrementally through mocks, integrations, or other methods, explain the testing stages. -->

{{qaFocusAndRegressionAreas}}

## Scale

<!-- Define scale-testing requirements and whether the feature can affect memory consumption, RPO/RTO, or system performance. Include concrete scenarios, quantities, thresholds, and test types such as protected and unprotected VM counts, hosts, volumes, and I/O rate. State whether QA scale regression and feature-specific scale testing are required. -->

{{scaleScenariosAndThresholds}}

</details>

# Rollout Considerations

<details>
<summary>Rollout Considerations</summary>

## Feature Flag

<!-- Contains the decision if the functionality will be disabled using the feature flag or tweak.  -->
<!-- If configuration tweaks added, modified, deleted during the design, add the table with the columns (Tweak name, Default, Description) -->

{{featureFlagAndReason}}

## Backward Compatibility

<!-- Describe backward compatibility, whether the feature must be tested against previous versions, and any special compatibility considerations. -->

{{backwardCompatibility}}

## Upgrade Considerations

<!-- Describe how the feature affects upgrades, including new or changed database schemas and removed components. -->

{{upgradeConsiderations}}

## {{Platform}} - Public Cloud Cost Estimation
<!-- List of affected platforms, such as VC, VCD, AWS, Azure, AVS, SCVMM, VME, and GCVe. -->
<!-- Estimate public-cloud development costs in $500 increments to support planning and avoid unexpected charges. Include compute, storage, and other hidden costs; round a lower estimate up to the applicable $500 increment. -->

{{costEstimateInFiveHundredDollarIncrements}}

</details>

# Open Questions

<details>
<summary>Open Questions</summary>

<!-- List unresolved questions when applicable. -->

| **Question** | **Answer**  |
| --- | --- |
| {{unresolvedDecisionOrConflict}} |  |

</details>

# Detailed Design
<!-- Repeat the complete artifact block below once per independently reviewable implementation artifact, ordered by GUI/visual artifact, contract delta, low-level diagram, prototype finding, then research summary. Preserve source order within a type unless an existing design has a stable order. Remove this instruction and all child blocks when no artifacts apply. Supported content is a supplied GUI mockup, screenshot, or other visual; an API, GUI, database, resource, or other contract delta; an opt-in Class Diagram or implementation-level Sequence Diagram; an evidence-triggered Deployment View Delta; existing prototype findings; or an existing research summary. Embed repository images with useful alt text and repository-relative paths; link supplied non-image or external visuals. Contract and diagram producer skills own their complete artifact-specific output. Prototype content states the question, observed facts, resulting decision, and only the smallest decision-bearing code or configuration snippet, and links the throwaway branch or durable result. Research content states terse findings and consequences and links exactly once to the durable research Markdown artifact without copying its primary-source links. Remove the Artifact line when the block has no link. -->

## {{artifactTitle}}

<details>
<summary>{{artifactTitle}}</summary>

**Evidence summary:** {{conciseEvidenceSummary}}

**Artifact:** [{{artifactLinkLabel}}]({{artifactLink}})

{{artifactSpecificContent}}

</details>

# Checklists

<details>
<summary>Checklists</summary>

<!-- For each row, keep only the correct value (applicable / not applicable) and fill in details in the empty box if relevant. Remove a subsection only when the whole category is not applicable, and note that in Details. -->

## Main Workflows

| **Item** | **Applicable** | **Details** |
| --- | --- | --- |
| VPG Workflows | {{applicable / not applicable}} |  |
| VRA Workflows | {{applicable / not applicable}} |  |
| Undo | {{applicable / not applicable}} |  |

## Interfaces & Operations

| **Item** | **Applicable** | **Details** |
| --- | --- | --- |
| Alerts / Events / Tasks | {{applicable / not applicable}} |  |
| API | {{applicable / not applicable}} |  |

## Resiliency

| **Item** | **Applicable** | **Details** |
| --- | --- | --- |
| ZVM Restart | {{applicable / not applicable}} |  |
| VRA Restart | {{applicable / not applicable}} |  |
| Network Disconnections | {{applicable / not applicable}} |  |
| Locking, Synchronization | {{applicable / not applicable}} |  |

## Supportability

| **Item** | **Applicable** | **Details** |
| --- | --- | --- |
| Analytics (CallHome, Transmitter, Google Analytics) | {{applicable / not applicable}} |  |
| Tweaks | {{applicable / not applicable}} |  |
| Log Collection | {{applicable / not applicable}} |  |
| Log Parser | {{applicable / not applicable}} |  |

## Security

| **Item** | **Applicable** | **Details** |
| --- | --- | --- |
| STRIDE analysis, Passwords, Data Validations | {{applicable / not applicable}} |  |
| Authentication, Authorization | {{applicable / not applicable}} |  |
| New endpoints created and their security features | {{applicable / not applicable}} |  |
| Used unauthenticated endpoints | {{applicable / not applicable}} |  |
| Used unencrypted endpoints | {{applicable / not applicable}} |  |
| New server endpoints | {{applicable / not applicable}} |  |
| New secrets (incl. new places for existing secrets) | {{applicable / not applicable}} |  |
| FIPS compliance | {{applicable / not applicable}} |  |

## Containers \\ Appliance Changes

| **Item** | **Applicable** | **Details** |
| --- | --- | --- |
| Was new container added? [New Container Checklist](https://zerto.atlassian.net/wiki/spaces/ZA/pages/2241921025) | {{applicable / not applicable}} |  |
| New container expected resources (storage, CPU, Memory) | {{applicable / not applicable}} |  |
| Any other appliance related changes | {{applicable / not applicable}} |  |

## 3rd Party & Open Source Review & Deliverables

<!-- If a new third-party resource is used, list it here. You may exclude Microsoft and .NET default NuGets (System.* or Microsoft.*). Include relevant open-source projects even if already OSRB-approved elsewhere. -->

| **Component** | **Version** | **License** | **URL** | **Usage** |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## External Deliverables Change

<!-- If any of the below applies to your work, state it clearly and ensure everything is delivered, updated, and acknowledged, handing it over as necessary. -->

| **Item** | **Applicable** | **Details** |
| --- | --- | --- |
| Requires Change to Documentation? | {{applicable / not applicable}} |  |
| Requires or affects Swagger? Was this executed? | {{applicable / not applicable}} |  |
| New Permissions or change in policies? | {{applicable / not applicable}} |  |
| Involves scripts or anything that isn't part of the binaries of the application? | {{applicable / not applicable}} |  |

</details>
````
<!-- adf:ignore:start -->

# Source Material

<!-- Record each consumed source once. Use a repository-relative path or canonical issue URL. Update the matching row when reprocessing a source. Do not infer provenance for legacy content. -->

| **Source** | **Kind** | **Contribution** |
| --- | --- | --- |
| {{canonicalSource}} | {{sourceKind|Spec / GitHub issue / Wayfinder map / Wayfinder decision / Wayfinder evidence / Grill conversation}} | {{consumedEvidence}} |
<!-- adf:ignore:end -->

