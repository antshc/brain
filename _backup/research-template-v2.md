# Research: <Topic>

**Date:** YYYY-MM-DD  
**Author:** <name>  
**Status:** Draft | In Progress | Completed  
**Tags:** <architecture, .NET, Kubernetes, performance, etc.>

---

## 1. Research Question

What are we trying to understand or decide?

> <clear question>

Example:
> What is the best way to process 100k concurrent jobs in .NET while limiting concurrency to 1,000?

---

## 2. Context

Why is this research needed?

- Current system:
- Problem:
- Constraints:
- Expected scale:
- Relevant components:

---

## 3. Goals

- <goal>
- <goal>
- <goal>

### Non-Goals

- <what is intentionally out of scope>

---

## 4. Requirements / Constraints

| Constraint | Description |
|---|---|
| Performance | |
| Scalability | |
| Compatibility | |
| Security | |
| Maintainability | |
| Cost | |
| Operational complexity | |

---

## 5. Options Investigated

### Option A — <name>

**Description**

<how it works>

**Pros**
- 
- 

**Cons**
- 
- 

**Notes**
- 

---

### Option B — <name>

**Description**

<how it works>

**Pros**
- 
- 

**Cons**
- 
- 

**Notes**
- 

---

## 6. Comparison

| Criteria | Option A | Option B | Option C |
|---|---|---|---|
| Complexity | | | |
| Performance | | | |
| Scalability | | | |
| Reliability | | | |
| Maintainability | | | |
| Ecosystem maturity | | | |
| Operational effort | | | |

---

## 7. Experiments / Validation

### Experiment 1 — <name>

**Hypothesis**

> <what you expect>

**Setup**

```text
Environment:
Data:
Configuration:
Load:
````

**Steps**

1.
2.
3.

**Result**

```text
<measurements / observations>
```

**Conclusion**

<what the result means>

---

## 8. Findings

### Finding 1 — <short title>

<description>

**Evidence**

* <source / benchmark / code>
* <source>

### Finding 2 — <short title>

<description>

---

## 9. Gotchas / Limitations

* ⚠️ <important limitation>
* ⚠️ <unexpected behavior>
* ⚠️ <version-specific behavior>
* ⚠️ <operational consideration>

---

## 10. Decision

**Selected option:** `<option>`

### Why

*
*
*

### Trade-offs Accepted

*
*

### Rejected Alternatives

| Alternative | Reason |
| ----------- | ------ |
|             |        |
|             |        |

---

## 11. Implementation Notes

```text
Components affected:
Configuration changes:
Dependencies:
Migration:
Deployment:
Monitoring:
```

Potential implementation:

```text
<code / pseudocode / configuration>
```

---

## 12. Open Questions

* [ ] <question>
* [ ] <question>
* [ ] <question>

---

## 13. Follow-up Tasks

* [ ] <task>
* [ ] <task>
* [ ] <task>

---

## 14. Sources

### Official Documentation

* <URL>

### Articles / Papers

* <URL>

### GitHub / Source Code

* <URL>

### Discussions / Issues

* <URL>

---

## 15. Summary

**Problem:**
<1–2 sentences>

**Key finding:**
<1–2 sentences>

**Decision:**
<1 sentence>

**Main trade-off:**
<1 sentence>

```

For engineering work, I’d keep **Research Question → Options → Experiments → Findings → Decision → Gotchas** as the mandatory core and treat the other sections as optional. This makes the document useful later as both research history and an ADR-style decision record.

