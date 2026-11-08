# Quality-attributes review

Follow the shared contract; return `AXIS: quality-attributes`. Review the complete change for non-defect quality concerns. Concrete incorrect behavior belongs to `bugs`; design smells belong to `code-smells`.

## Inspection

- Testability: specific changed high-risk behavior lacks an effective verification seam or scenario with a stated expected result. Missing tests alone are not a bug.
- Operability: changed behavior impairs diagnosis, observability, or recovery procedures with a demonstrated operational cost.
- Capacity: evidenced resource/scaling concerns without a demonstrated behavioral regression; state the workload and evidence, not hypothetical optimization.

Inspect implementation, usage, configuration and relevant tests. Report only introduced or materially worsened, actionable quality costs; omit preferences and speculative risks. For an already reported defect, include its test scenario in that finding rather than duplicating it here.

## Finding content

Supply evidenced quality impact, applicable conditions, symbols/path, and the smallest improvement to the shared conversation draft. Frame it as a suggestion, not a proven bug. Use shared JSON, five-finding limit, and explicit failure result.
