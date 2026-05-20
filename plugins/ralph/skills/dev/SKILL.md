---
name: dev
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
---

# ORCHESTRATOR LOOP

Repeat the following loop until no tasks remain.

## 1. Read state

Run the following commands and print their output so it is available as context.

```bash
echo "=== COMMITS ==="; 
echo "$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found.")"; 
echo ""
echo "=== TASKS ==="; echo "$(gh issue list --state open --label "ready" --json number,labels,title,body,comments 2>/dev/null | jq '[.[] | select(.labels | map(.name) | (contains(["blocked"]) or contains(["hitl"])) | not)]' 2>/dev/null || echo "[]")" | jq 'if length == 0 then "No issues found." else . end'
```

Parse the `TASKS` json array. Review `COMMITS` to understand what work has already been done.

## 2. Exit conditions

- If no tasks are available, **exit**.
- If all `ready` tasks are complete, close the PRD task and **exit**.

## 3. Select next task

Pick the next task. Prioritize in this order (first match wins):

1. Critical bugfixes
2. Development infrastructure — tests, types, dev scripts are precursors to features
3. Tracer bullets — tiny end-to-end slices that validate the approach early
4. Polish and quick wins
5. Refactors

## 4. Invoke implementation agent

Invoke the `ralph-impl` agent via `runSubagent` with the following prompt (substitute actual values):

```
Implement the following GitHub issue.

## TASK
- Issue: #<number>
- Title: <title>
- Body: <body>
- Comments: <comments>

## RECENT COMMITS
<last 5 commits from step 1>
```

## 5. Handle result

Read the agent's status report:

- **complete**: Loop back to step 1 (re-read fresh state).
- **partial**: Loop back to step 1 (agent already commented on issue).
- **blocked**: Add `blocked` label to the issue with `gh issue edit <number> --add-label "blocked"`, then loop back to step 1 to pick the next task.

# RULES

- ONE TASK AT A TIME. The agent handles one task per invocation.
- ALWAYS re-read state before selecting the next task — context changes after each commit.
- IF NO TASKS ARE AVAILABLE, EXIT.
