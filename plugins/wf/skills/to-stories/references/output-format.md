# Output Format

Write for Product Owners and QA — plain business language, no code, class names, or technical jargon. Each criterion is one clear, testable statement of expected behavior.

Each story is broken down by capability and carries four blocks in order: **Capability**, **Stakeholder Requirement**, **Functional Requirements**, then **Acceptance Criteria**. When a prior requirement set is in context, copy the first three blocks verbatim; otherwise derive them from the requirement text.

One story:
```
## <Capability title>

<capability title — behavior + entity, no surface or placement>

The <actor> needs to <behavior> <entity>, so <value>.

### Acceptance Criteria
Each criterion states one observable outcome bound to a condition (`<outcome> when/if <condition>`). Vary the opening to fit the behavior — do not force "The system" every time:
- <entity/outcome> <is/becomes/does> ... when <condition>.
- The <actor> <sees/receives/is prompted> ... when <condition>.
- The system <does observable outcome> when <condition>.
- If <failure condition>, <what the user/operator sees>.

**Functional Requirements:**
- <Behavior> when <condition>.
- ...


```

Multiple stories — repeat the block, one per capability, under a numbered heading:
```
## Story 1 — <Capability title>

<capability title — behavior + entity, no surface or placement>

The <actor> needs to <behavior> <entity>, so <value>.

### Acceptance Criteria
- ...

**Functional Requirements:**
- ...
```
