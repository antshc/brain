---
name: verify-instructions
description: Run when need to verify agent, skill, promt instructions and identify gaps waht can be improved
---

## Rules
- DO NOT modify any files. This skill is read-only — analysis and reporting only.
- You MUST print every finding. Do not summarize silently or collapse issues.
- For every issue found, you MUST output all three fields: Issue, Reasoning, and Suggested Change.

## Verify checklist
- [ ] Is the steps, instructions ambiguous, explicit, clear enough to not be skipped during processing by the agent
- [ ] Check if the steps, instructions can be collapsed silently during processing by the agent
- [ ] Check if the steps, instructions leaving room for agent to skip them
- [ ] Does the instruction specify when or how to handle, locate the commands and files ( eg.. locate the .csproj to build)

## Output format

For each issue found, print a block in this exact format:

---
**Issue:** <short description of the problem>
**Reasoning:** <why this is a problem — what agent behavior it enables or prevents>
**Suggested change:**
```
<exact replacement text or diff showing the proposed wording>
```
---

If no issues are found, print: `No issues found.`
