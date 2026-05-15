---
name: dev
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
---
# TASK SELECTION
## Read state

Run the following commands and print their output so it is available as context. 

```bash
echo "=== COMMITS ===/n"; 
echo "$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found.")"; 
echo "/n"
echo "=== TASKS ===/n"; echo "$(gh issue list --state open --label "afk" --label "ready" --json number,labels,title,body,comments | jq '[.[] | select(.labels | map(.name) | contains(["blocked"]) | not)]' 2>/dev/null || echo "[]")" | jq 'if length == 0 then "No issues found." else . end'
```

The `TASK` is the Github issue. 
Each `TASK` has `number`, `labels`, `title`, `body`, and `comments`.

Parse the `TASKS` output json array from **TASKS**. 
Review the `COMMITS` output from **COMMITS** to understand what work has already been done.

If all `afk` tasks are complete close the PRD task.

## Next task selection

Pick the next task. Prioritize tasks in this order. If a task falls into multiple categories, prioritize the one listed first.

1. Critical bugfixes
2. Development infrastructure

Getting development infrastructure like tests and types and dev scripts ready is an important precursor to building features.

3. Tracer bullets for new features

Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development.

TL;DR - build a tiny, end-to-end slice of the feature first, then expand it out.

4. Polish and quick wins
5. Refactors

# TASK IMPLEMENTATION WORKFLOW

## EXPLORATION

Explore the repo.

## IMPLEMENTATION

Implement the task using the `/tdd`, `/wf:tdd` skill.

## FEEDBACK LOOPS

Before committing, run the feedback loops:

- Build the project with changed files
- Run only specific tests for changed files

## COMMIT

Make a git commit. The commit message must:

1. Include key decisions made
2. Include files changed
3. Blockers or notes for next iteration

## THE ISSUE

If the task is complete, close the original GitHub issue.

If the task is not complete, leave a comment on the GitHub issue with what was done.

# FINAL RULES

WORK ON ONE TASK AT A TIME. DO NOT START A NEW TASK UNTIL THE CURRENT ONE IS COMPLETE.
WHEN THE CURRENT TASK IS COMPLETE, PICK THE NEXT ELIGIBLE TASK.
IF THE CURRENT TASK IS BLOCKED, LEAVE A COMMENT ON THE GITHUB ISSUE WITH WHAT WAS DONE AND WHAT THE BLOCKER IS, ADD `blocked` LABEL.
IF NO TASKS ARE AVAILABLE, EXIT.
