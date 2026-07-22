# Output Format

Write for Product Owners and QA — plain business language, no code, class names, or technical jargon. Each criterion is one clear, testable statement of expected behavior.

Each story is broken down by capability and carries four blocks in order: **Capability**, **Stakeholder Requirement**, **Functional Requirements**, then **Acceptance Criteria**. When a prior requirement set is in context, copy the first three blocks verbatim; otherwise derive them from the requirement text.

One story:
```
## {{capabilityTitle}}

{{capabilityTitle|behavior + entity, no surface or placement}}

The {{actor}} needs to {{behavior}} {{entity}}, so {{value}}.

### Acceptance Criteria
- {{outcome}} when {{condition}}.
- If {{condition}}, {{actor}} must {{outcome}}.

**Functional Requirements:**
- {{behavior}} when {{condition}}.
- ...


```

Multiple stories — repeat the block, one per capability, under a numbered heading:
```
## Story 1 — {{capabilityTitle}}

{{capabilityTitle|behavior + entity, no surface or placement}}

The {{actor}} needs to {{behavior}} {{entity}}, so {{value}}.

### Acceptance Criteria
- ...

**Functional Requirements:**
- ...
```
