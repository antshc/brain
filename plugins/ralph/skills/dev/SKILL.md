---
name: dev
description: AFK autonomous development loop — picks the next open issue, implements it, and commits the result.
---

# Setup

Run the following commands and print their output so it is available as context:

```bash
commits=$(git log -n 5 --format="%H%n%ad%n%B---" --date=short 2>/dev/null || echo "No commits found")
issues=$(gh issue list --state open --json number,title,body,comments)
echo "=== COMMITS ==="; echo "$commits"
echo "=== ISSUES ==="; echo "$issues"
```

# ISSUES

Parse the `ISSUES` output from Setup. Each issue has `number`, `title`, `body`, and `comments`.

You will work on the AFK issues only, not the HITL ones.

Review the `COMMITS` output from Setup to understand what work has already been done.

If all AFK tasks are complete, output <promise>NO MORE TASKS</promise>.

# TASK SELECTION

Pick the next task. Prioritize tasks in this order:

1. Critical bugfixes
2. Development infrastructure

Getting development infrastructure like tests and types and dev scripts ready is an important precursor to building features.

3. Tracer bullets for new features

Tracer bullets are small slices of functionality that go through all layers of the system, allowing you to test and validate your approach early. This helps in identifying potential issues and ensures that the overall architecture is sound before investing significant time in development.

TL;DR - build a tiny, end-to-end slice of the feature first, then expand it out.

4. Polish and quick wins
5. Refactors

# EXPLORATION

Explore the repo.

# IMPLEMENTATION

Complete the task.

# FEEDBACK LOOPS

Before committing, run the feedback loops:

- Build the project with changed files
- Run only specific tests for changed files

# COMMIT

Make a git commit. The commit message must:

1. Include key decisions made
2. Include files changed
3. Blockers or notes for next iteration

# THE ISSUE

If the task is complete, close the original GitHub issue.

If the task is not complete, leave a comment on the GitHub issue with what was done.

# FINAL RULES

ONLY WORK ON A SINGLE TASK.

