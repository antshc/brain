# Software Engineering Research Process

For software-engineering research, a good approach is to move in **short evidence-driven loops**, not just read everything you find.

## 1. Frame the Question

Define exactly what you need to decide.

**Bad:**
> Research Kafka.

**Better:**
> Can Kafka replace Azure Service Bus for our workload of 20M events/day with simpler operations?

---

## 2. Set Constraints First

Define the boundaries before researching solutions:

- Scale
- Latency
- Cost
- Deployment environment
- Team skills
- Security/compliance
- Compatibility

This prevents spending time on irrelevant options.

---

## 3. Start Broad — Map the Space

Use a breadth-first pass:

- What approaches exist?
- What are the 3–5 realistic options?
- What terminology should I know?
- What are common failure modes?

Do not go deep yet.

---

## 4. Create Hypotheses

Turn assumptions into things you can verify.

Examples:

- `Channel<T>` will use less memory than TPL Dataflow.
- DynamoDB is sufficient without adding Redis.
- This API supports idempotent retries.

---

## 5. Rank Unknowns by Risk

Research the things that could invalidate the solution first.

Recommended order:

1. Feasibility
2. Hard limitations
3. Performance / scalability
4. Reliability
5. Security
6. Operational complexity
7. Developer ergonomics

Avoid spending hours studying syntax before discovering that the technology cannot support a critical requirement.

---

## 6. Use an Evidence Ladder

Prefer stronger evidence:

```text
Source code / experiment
        ↓
Official documentation
        ↓
Official issues / design documents
        ↓
Maintainer discussions
        ↓
Good technical articles
        ↓
Stack Overflow / Reddit / blogs
        ↓
AI-generated explanation
```

AI is useful for discovering directions and summarizing, but important conclusions should normally be verified.

---

## 7. Go Deep Only Where Needed

After the broad pass, choose the important branches.

Think of the research as a tree:

```text
Question
├── Option A
│   ├── architecture
│   ├── limitations
│   └── performance
├── Option B
│   ├── architecture
│   └── limitations
└── Option C
    └── rejected early
```

If Option C violates a hard constraint, stop researching it.

---

## 8. Run a Spike When Documentation Is Insufficient

A small engineering experiment is often more valuable than more reading.

Example:

```text
Hypothesis:
Parallel.ForEachAsync can sustain 1,000 concurrent requests.

Experiment:
- 100,000 requests
- concurrency: 1,000
- simulated latency: 300 ms

Measure:
- total duration
- memory
- CPU
- errors
```

---

## 9. Record Findings Immediately

Do not wait until the end.

Example:

```markdown
### Finding: DeleteSnapshot API is rate-limited

Evidence:
- AWS documentation: <link>
- Local test: ~4–5 requests/sec before throttling

Impact:
Snapshot deletion must use bounded concurrency + retry/backoff.
```

---

## 10. Separate Facts, Assumptions, Unknowns, and Conclusions

This is especially useful when AI participates in the research.

```text
FACT
AWS SDK retries throttling errors by default.

ASSUMPTION
Default retries are sufficient for our workload.

UNKNOWN
Behavior with 300 simultaneous snapshot deletions.

CONCLUSION
Requires a load experiment.
```

---

## 11. Continuously Prune

Research is a tree. Delete branches.

After every significant finding ask:

> Does this change what I need to investigate next?

Example:

```text
5 options
    ↓
discover hard requirements
    ↓
3 options
    ↓
check technical limitations
    ↓
2 options
    ↓
benchmark
    ↓
1 recommended option
```

---

## 12. Use Explicit Stopping Criteria

Otherwise research can continue indefinitely.

Stop when:

- critical unknowns are resolved;
- options can be compared;
- major risks are understood;
- evidence is sufficient to make the decision;
- further research is unlikely to change that decision.

---

## Compact Research Flow

```text
QUESTION
   ↓
CONSTRAINTS
   ↓
MAP OPTIONS
   ↓
IDENTIFY UNKNOWNS
   ↓
HYPOTHESES
   ↓
VERIFY
 docs → source → experiment
   ↓
FINDINGS
   ↓
PRUNE OPTIONS
   ↓
REPEAT
   ↓
DECISION
```

## Core Principle

The most important technique is **risk-first research**:

> Investigate the unknown most likely to invalidate your approach before polishing the details.

For software engineering, this usually makes research much faster and more decision-oriented.
