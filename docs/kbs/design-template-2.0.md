<!-- Source: https://zerto.atlassian.net/wiki/spaces/ZE/pages/1418002466/Design+Template+2.0 -->
<!-- Fetched from Confluence. Images are placeholders (not the originals). -->

![image-20250827-073613.png](images/image-20250827-073613.png)

*Created from Design Template 2.0* | [Template Link](https://zerto.atlassian.net/wiki/spaces/ZE/pages/1418002466) | [Template Change Log](https://zerto.atlassian.net/wiki/spaces/ZE/pages/2624585829)

# Feature name

*This should contain the feature name and* ***epic link (JIRA)****.*

| **Role** | **Name** |
| --- | --- |
| Author (Feature Lead) |  |
| Reviewers (Architect \ TL) |  |
| PO |  |

| **Documents Links** (If Applicable) | **Link** |
| --- | --- |
| Feature Review Document Link |  |
| Solution Direction Document Link |  |

| **Version** | **Author** |
| --- | --- |
| Detailed change history, including dates, is available under **View Changes** in the right-hand menu. This table is used to record author-maintained version checkpoints. | |
| 1.0 | [Placeholder] |

# Table of Contents

# Problem Statement and Goals

*This should detail the reason for the change request (Motivation), including the issue we want to address or the motivation for this enhancement, as well as the business context for this feature.*  
This should be reviewed and approved by PO.

# Requirements

*This should be fully synced with the PO.*

*Each requirement must be clear and self-explanatory. Use the “Extra Details” box for further clarification if needed.*

*Requirement sources should distinguish between product and technical requirements. Requirements from the development team must be approved by the PO.*

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **#** | **Requirement** | **Priority** | **Details** | **Source** |
| 1 | *Top Level Requirement #1* | MVP / Should have / nice to have |  | PO / Dev team |
| 1.1 | *Sub-Requirement* | MVP / Should have / nice to have |  | PO / Dev team |
|  | | | |  |
| 2 | *Top Level Requirement #2* | MVP / Should have / nice to have |  | PO / Dev team |

# Assumptions and Limitations

*Limitations are requirements that you cannot meet due to constraints or drawbacks of the solution, such as high memory consumption or uncovered use cases.*

*Assumptions: The basis for your solution assumes the criteria are fully met.*

# Out of Scope

*If applicable, list items that your proposed solution does not address but that POs or others might assume are included.*

# Glossary and Abbreviations

|  |  |
| --- | --- |
| Term | Description |
|  |  |
|  |  |

# Current State

*Include a diagram of the current state of the application, component, or code area before the change (if* *applicable**). Mark components that can change in this solution with a different color for clarity.*

# Solution Overview

*This section outlines how to plan a solution for the problem presented in the epic. It serves as the main content for the design meeting and should not exceed 8 pages by best practice.*

## Use cases

*Where the* *user* *interacts with the feature (Install VRA, Create VPG, Upgrade ZVM, Undo) and under what circumstances.*

## Component / Architecture / System Diagram

*This should include a diagram illustrating the various parts of the solution. The boxes can represent specific entities, code areas, or other elements to demonstrate the solution's* *architecture**.*   
*Mention IDesign components if applicable. This section**is* *mandatory* *when multiple components and teams are involved across the organization.*

![image-20250827-125621.png](images/image-20250827-125621.png)

## Flow Diagram [Edit Title To Describe Which Flow]

*Flow diagrams are suitable when you need to visualize the step‑by‑step flow of a process. They help clarify workflows and decisions. Use several diagrams if needed.*

![image-20250827-125314.png](images/image-20250827-125314.png)

## Sequence Diagram [Edit Title To Describe Which Sequence]

*Sequence diagrams are suitable when you need to describe how different components, services, or objects interact over time to complete a scenario. Use several diagrams if needed. Include main important actors to avoid overwhelming the audience with micro details, which belong in the “For Developers” section below.*

![image-20250827-125741.png](images/image-20250827-125741.png)

# Testing Guidelines

## Testing by Dev

*Please describe the testing by dev team (manual + automation) - supporting unit, integration, and E2E tests.*

## QA Testing Focus Areas

*Please specify the areas that QA should focus on, including regression areas.*  
If testing can be done incrementally and gradually using mocks, integrations, or other methods, please explain the testing stages.

## Scale

*Please describe the requirements for scale testing. Can it affect memory consumption? Can it impact RPO/RTO? Can it slow down the system?*  
*Include specific scenarios, numbers needed for testing, and types of scale testing, such as:*

- *Scale of VMs (Protected, Unprotrected)*
- Scale of Hosts
- *Scale of Volumes*
- *I/O rate (performance)*

*Please mention that QA scale testing is required for the feature:*

1. *QA scale regression*
2. *specific scale testing for the feature.*

# Backward Compatibility

*This should include backward compatibility information about the feature. Should it be tested against previous versions? Are there any special considerations regarding backward compatibility?*

# Upgrade Considerations

*This should include information on how the feature affects upgrade, such as new database schemas, changes to existing schemas, and removal of components.*

# Platforms

VC / VCD / AWS / Azure / AVS / SCVMM / VME / GCVe

### Public Cloud Cost Estimation

*Include a rough estimate of the public cloud costs for developing the feature. This will help us avoid surprises, such as a $10,000 bill at the end of the month, and allow for better planning.*

- *The estimate should be in increments of $500.*
- *For example, if we anticipate using two VMs (one ZCA and one protected VM) in public clouds for 10 days at 10 hours per day (assuming $1 per hour per VM), the total cost would be $200. Since this is a rough estimate and there are hidden costs in public clouds, such as storage, we can consider the development cost for this feature to be "up to $500."*

# Feature Flag

*Yes (With Tweak Name) / No (And Why)*

# Open Questions

*This section should include open questions, if applicable.*

# Detailed Design: Implementation Appendix

***This*** ***part is hidden and not required to be presented on the design meeting.***  
***However, this part should be approved by the team and design approver.***

*You can refer to this section when a question arises.*

*The main purpose of this section is to provide detailed design specifications for the squad’s developers and ensure the design complies with all mandatory checklist items.*

*Please include detailed design information here, such as class references and insights on complex or lower-level topics from the design process that may not be relevant to the main content.*

