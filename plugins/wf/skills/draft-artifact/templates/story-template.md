# User story template


Write the body for Product Owners and QA in plain business language, without code, class names, or technical jargon; each criterion is a clear, testable statement of expected behavior. The optional appendices are technical and live inside the collapsed **Technical notes** block.

- **Implementation Decisions** — omit unless the story requires a specific implementation decision. Class, type, object, and endpoint names are allowed for navigation; omit file paths and line numbers.
- **Contracts Delta** — omit unless this User story changes an API, GUI, Database, Resource, or other contract. Order its blocks API → Database → Resource → other → GUI.

```text
**Title:** {{[initiativeTag]|optional}}{{deployableKind|[FE] or [BE]}} {{stakeholderRequirement|verbatim Stakeholder requirement}}

**Requirements:**
- {{functionalRequirement|verbatim reference or statement}}
- {{functionalRequirement|verbatim reference or statement}}

**Acceptance Criteria**
- {{outcome}} when {{condition}}.
- If {{condition}}, {{actor}} must {{outcome}}.
- ...

---
<details>
<summary>Technical notes</summary>

**Implementation Decisions** 
<!-- Omit this section unless an implementation decision is required. -->
- {{implementationDecision}}

**Contracts Delta**
<!-- Omit this section unless a contract changes. -->
{{contractsDeltaOutput|sections}}

</details>
```
