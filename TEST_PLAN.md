# Test Plan

## Overview

This document defines the test scenarios for the **ralph** AFK review service using Gherkin-style specifications. Each scenario is categorized by test type:

- **Unit** — tests a single domain class or utility function in isolation.
- **Integration** — tests a feature handler with mocked `GhCli` (via `FakeGhCli`) and a spy `AIAgent`.
- **Manual** — verified manually via CLI invocation.

Integration test boundary:
- `GhCli` → replaced with `FakeGhCli` (in-memory test double).
- `AIAgent` → replaced with a spy that records calls and verifies arguments.
- `ExecutionLog` → replaced with a mock/stub.

### Test ↔ Scenario Mapping Convention

Every test class and test method must be traceable back to a scenario in this plan:

- **Test class docstring** must contain the **Feature name** (e.g., `"Feature: Comment Label Detection"`).
- **Test method name** must match the **Scenario name** in snake_case (e.g., scenario `"Comment with 'fix!:' prefix is labeled FIX"` → `test_comment_with_fix_prefix_is_labeled_fix`).

Whenever a test or scenario is added, renamed, or removed, the mapping must be updated on both sides to stay in sync.

---

## Feature: Comment Label Detection

> Unit: `Comment.get_label()`

```gherkin
Scenario: Comment with "fix!:" prefix is labeled FIX
  Given a comment with body "fix!: broken null check"
  When get_label() is called
  Then the result is ThreadLabel.FIX

Scenario: Comment with "suggest!:" prefix is labeled SUGGEST_BANG
  Given a comment with body "suggest!: consider extracting"
  When get_label() is called
  Then the result is ThreadLabel.SUGGEST_BANG

Scenario: Comment with "suggest:" prefix is labeled SUGGEST
  Given a comment with body "suggest: could improve readability"
  When get_label() is called
  Then the result is ThreadLabel.SUGGEST

Scenario: Comment with "nit:" prefix is labeled NIT
  Given a comment with body "nit: minor style issue"
  When get_label() is called
  Then the result is ThreadLabel.NIT

Scenario: Comment with "good:" prefix is labeled GOOD
  Given a comment with body "good: nice approach"
  When get_label() is called
  Then the result is ThreadLabel.GOOD

Scenario: Comment with "question!:" prefix is labeled QUESTION
  Given a comment with body "question!: why is this needed?"
  When get_label() is called
  Then the result is ThreadLabel.QUESTION

Scenario: Comment containing "Fixed." is labeled FIXED
  Given a comment with body "Fixed."
  When get_label() is called
  Then the result is ThreadLabel.FIXED

Scenario: Comment with no recognized prefix returns None
  Given a comment with body "looks fine to me"
  When get_label() is called
  Then the result is None
```

**Coverage:** Unit test

---

## Feature: Comment Exclusion Detection

> Unit: `Comment.is_excluded()`

```gherkin
Scenario: Comment labeled QUESTION is excluded
  Given a comment with body "question!: why is this needed?"
  When is_excluded() is called
  Then the result is True

Scenario: Comment labeled FIXED is excluded
  Given a comment with body "Fixed."
  When is_excluded() is called
  Then the result is True

Scenario: Comment labeled FIX is not excluded
  Given a comment with body "fix!: broken null check"
  When is_excluded() is called
  Then the result is False

Scenario: Comment with no label is not excluded
  Given a comment with body "random text"
  When is_excluded() is called
  Then the result is False
```

**Coverage:** Unit test

---

## Feature: Thread Actionability

> Unit: `ReviewThread.is_actionable`

```gherkin
Scenario: Thread with fix! label is actionable
  Given an unresolved thread with a single comment "fix!: broken null check"
  When is_actionable is evaluated
  Then the result is True

Scenario: Thread with suggest! label is actionable
  Given an unresolved thread with a single comment "suggest!: extract method"
  When is_actionable is evaluated
  Then the result is True

Scenario: Thread with suggest label is NOT actionable
  Given an unresolved thread with a single comment "suggest: could improve"
  When is_actionable is evaluated
  Then the result is False

Scenario: Thread with nit label is NOT actionable
  Given an unresolved thread with a single comment "nit: minor style"
  When is_actionable is evaluated
  Then the result is False

Scenario: Thread with good label is NOT actionable
  Given an unresolved thread with a single comment "good: nice approach"
  When is_actionable is evaluated
  Then the result is False

Scenario: Resolved thread is never actionable
  Given a resolved thread with a single comment "fix!: broken null check"
  When is_actionable is evaluated
  Then the result is False

Scenario: Thread with no recognized label is NOT actionable
  Given an unresolved thread with a single comment "looks fine"
  When is_actionable is evaluated
  Then the result is False

Scenario: Last comment is excluded (question!) — thread not actionable
  Given an unresolved thread with comments:
    | body                       |
    | fix!: issue                |
    | question!: Clarification?  |
  When is_actionable is evaluated
  Then the result is False

Scenario: Last comment is excluded (Fixed.) — thread not actionable
  Given an unresolved thread with comments:
    | body              |
    | fix!: issue       |
    | Fixed.            |
  When is_actionable is evaluated
  Then the result is False

Scenario: Unlabeled comment after fix! — thread not actionable
  Given an unresolved thread with comments:
    | body                          |
    | fix!: broken null check       |
    | I think this is fine actually |
  When is_actionable is evaluated
  Then the result is False

Scenario: fix! after question! — last fix wins, thread actionable
  Given an unresolved thread with comments:
    | body                       |
    | fix!: original issue       |
    | question!: Clarification?  |
    | fix!: new fix              |
  When is_actionable is evaluated
  Then the result is True

Scenario: fix! after Fixed. — last fix wins, thread actionable
  Given an unresolved thread with comments:
    | body                       |
    | fix!: old issue            |
    | Fixed.                     |
    | fix!: actually not fixed   |
  When is_actionable is evaluated
  Then the result is True
```

**Coverage:** Unit test

---

## Feature: Actionable Comment Extraction

> Unit: `ReviewThread.actionable_comment`

```gherkin
Scenario: Single labeled comment is the actionable comment
  Given an unresolved thread with a single comment "fix!: broken null check"
  When actionable_comment is evaluated
  Then the result is "fix!: broken null check"

Scenario: Last labeled comment is used when multiple comments exist
  Given an unresolved thread with comments:
    | body                          |
    | LGTM overall                  |
    | fix!: but this part is wrong  |
  When actionable_comment is evaluated
  Then the result is "fix!: but this part is wrong"

Scenario: No labeled comment — actionable_comment is empty string
  Given an unresolved thread with comments:
    | body           |
    | looks fine     |
    | no issues      |
  When actionable_comment is evaluated
  Then the result is ""

Scenario: Empty comment list returns empty string
  Given an unresolved thread with no comments
  When actionable_comment is evaluated
  Then the result is ""
```

**Coverage:** Unit test

---

## Feature: Thread Filter

> Unit: `ThreadFilter.get_actionable_threads()`

```gherkin
Scenario: Only actionable threads are returned
  Given a list of threads:
    | id  | body                       | resolved |
    | T1  | fix!: broken null check    | false    |
    | T2  | nit: minor style           | false    |
    | T3  | suggest!: extract method   | false    |
    | T4  | fix!: issue                | true     |
  When get_actionable_threads() is called
  Then the result contains thread IDs ["T1", "T3"]

Scenario: All threads are non-actionable — empty list returned
  Given a list of threads:
    | id  | body              | resolved |
    | T1  | nit: minor style  | false    |
    | T2  | good: nice        | false    |
  When get_actionable_threads() is called
  Then the result is an empty list

Scenario: Empty input returns empty list
  Given an empty list of threads
  When get_actionable_threads() is called
  Then the result is an empty list
```

**Coverage:** Unit test

---

## Feature: Issue Actionability

> Unit: `Issue.is_actionable`

```gherkin
Scenario: Issue with ready label is actionable
  Given an issue labeled ["ready"]
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue with prd label is actionable
  Given an issue labeled ["prd"]
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue with ready and prd labels is actionable
  Given an issue labeled ["ready", "prd"]
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue with no actionable labels is not actionable
  Given an issue labeled ["enhancement"]
  When is_actionable is evaluated
  Then the result is False

Scenario: Issue with ready and blocked labels is not actionable
  Given an issue labeled ["ready", "blocked"]
  When is_actionable is evaluated
  Then the result is False

Scenario: Issue with prd and hitl labels is not actionable
  Given an issue labeled ["prd", "hitl"]
  When is_actionable is evaluated
  Then the result is False

Scenario: Issue with ready, prd, and blocking labels is not actionable
  Given an issue labeled ["ready", "prd", "blocked", "hitl"]
  When is_actionable is evaluated
  Then the result is False

Scenario: Issue with actionable and unrelated labels is actionable
  Given an issue labeled ["ready", "bug"]
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue comment fields are preserved
  Given an issue with one comment containing id, body, and created_at
  When the issue is created
  Then the issue exposes the same comment fields
```

**Coverage:** Unit test

---

## Feature: Issue Filter

> Unit: `IssueFilter.get_actionable_issues()`

```gherkin
Scenario: Only actionable issues are returned
  Given a list of issues with labels ["ready"], ["blocked"], ["prd"], and ["ready", "hitl"]
  When get_actionable_issues() is called
  Then the result contains issue numbers [1, 3]

Scenario: All issues are non-actionable — empty list returned
  Given a list of issues with labels ["bug"] and ["blocked"]
  When get_actionable_issues() is called
  Then the result is an empty list

Scenario: Empty input returns empty list
  Given an empty list of issues
  When get_actionable_issues() is called
  Then the result is an empty list
```

**Coverage:** Unit test

---

## Feature: ThreadLabel Actionability

> Unit: `ThreadLabel.is_actionable()`

```gherkin
Scenario: FIX label is actionable
  Given ThreadLabel.FIX
  When is_actionable() is called
  Then the result is True

Scenario: SUGGEST_BANG label is actionable
  Given ThreadLabel.SUGGEST_BANG
  When is_actionable() is called
  Then the result is True

Scenario: SUGGEST label is NOT actionable
  Given ThreadLabel.SUGGEST
  When is_actionable() is called
  Then the result is False

Scenario: NIT label is NOT actionable
  Given ThreadLabel.NIT
  When is_actionable() is called
  Then the result is False

Scenario: GOOD label is NOT actionable
  Given ThreadLabel.GOOD
  When is_actionable() is called
  Then the result is False

Scenario: QUESTION label is NOT actionable
  Given ThreadLabel.QUESTION
  When is_actionable() is called
  Then the result is False

Scenario: FIXED label is NOT actionable
  Given ThreadLabel.FIXED
  When is_actionable() is called
  Then the result is False
```

**Coverage:** Unit test

---

## Feature: VCS Client Thread Mapping

> Unit: `VCSClient._thread_from_raw()`

```gherkin
Scenario: Raw thread node is mapped to ReviewThread domain entity
  Given a raw thread dict with id "T1", path "src/foo.ts", startLine 10, line 15, isResolved false
    And one comment with author "reviewer" and body "fix!: issue"
  When _thread_from_raw() is called
  Then the result is a ReviewThread with:
    | field      | value      |
    | thread_id  | T1         |
    | path       | src/foo.ts |
    | lines      | 10-15      |
    | is_resolved| False      |
  And comments[0].author is "reviewer"
  And comments[0].body is "fix!: issue"

Scenario: Missing startLine falls back to line for both start and end
  Given a raw thread dict with id "T2", path "a.py", startLine null, line 5
  When _thread_from_raw() is called
  Then the ReviewThread lines field is "5-5"
```

**Coverage:** Unit test

---

## Feature: VCS Client Issue Mapping

> Unit: `VCSClient.fetch_issues()`

```gherkin
Scenario: Raw issue nodes are mapped to Issue domain entities
  Given GhCli returns one raw issue dict with number 13, title "Add fetch issues", body "Need issue + comment mapping"
    And url "https://github.com/owner/repo/issues/13"
    And labels ["ready", "bug"]
    And one comment with id "IC_1", body "Need more context", createdAt "2026-05-24T10:00:00Z"
  When fetch_issues() is called
  Then the result contains one Issue with number 13, title "Add fetch issues", and labels ["ready", "bug"]
  And comments[0] preserves id, body, and created_at

Scenario: Missing issue labels and comments map to empty lists
  Given GhCli returns one raw issue dict with number 21 and no labels or comments keys
  When fetch_issues() is called
  Then the result Issue has empty labels and empty comments lists
```

**Coverage:** Unit test

---

## Feature: VCS Client Milestone Mapping

> Unit: `VCSClient.list_milestones()`

```gherkin
Scenario: Raw milestone nodes are mapped to Milestone domain entities
  Given GhCli returns one raw milestone dict with id "M1", number 1, title "Sprint 1", and description "First delivery slice"
    And url "https://github.com/owner/repo/milestone/1"
  When list_milestones() is called
  Then the result contains one Milestone with the same id, number, title, description, and url

Scenario: Missing milestone description maps to empty string
  Given GhCli returns one raw milestone dict with id "M2", number 2, title "Backlog", and description null
  When list_milestones() is called
  Then the result Milestone description is ""
```

**Coverage:** Unit test

---

## Feature: GhCli Milestone Query Construction

> Unit: `GhCli.list_milestones_raw()`

```gherkin
Scenario: Open milestones query is built and nodes are returned
  Given gh api graphql returns one milestone node for owner "owner" and repo "repo"
  When list_milestones_raw() is called
  Then subprocess.run() is invoked with the open milestones GraphQL query and repository variables
  And the returned nodes are passed through unchanged
```

**Coverage:** Unit test

---

## Feature: Fetch Issues

> Integration: mocked `GhCli`

```gherkin
Scenario: Handler returns correctly shaped output for actionable issues
  Given the repository "owner/repo"
    And the VCS returns actionable issues 14 and 15 with labels and comments
  When fetch_issues() is called
  Then the result is a serialisable list with both actionable issues and comment created_at fields

Scenario: Handler returns empty list when no actionable issues exist
  Given the repository "owner/repo"
    And the VCS returns only non-actionable issues
  When fetch_issues() is called
  Then the result is []

Scenario: Handler excludes blocked and non-actionable issues
  Given the repository "owner/repo"
    And the VCS returns one ready issue, one blocked ready issue, and one unrelated issue
  When fetch_issues() is called
  Then only the ready issue is returned

Scenario: Milestone title is forwarded to GhCli
  Given the repository "owner/repo"
    And the VCS is backed by a mocked GhCli
  When fetch_issues() is called with milestone_title "Sprint 1"
  Then GhCli.fetch_issues_raw() is called with owner "owner", repo "repo", and milestone title "Sprint 1"
```

**Coverage:** Integration test

---

## Feature: Fetch Issues CLI

> Unit: `fetch_issues.py`

```gherkin
Scenario: CLI prints JSON array for valid repository
  Given fetch_issues() returns one serialisable issue for "owner/repo"
  When main() is called with ["owner/repo"]
  Then exit code is 0 and stdout is that JSON array

Scenario: Missing argument prints usage error and returns one
  Given no CLI arguments
  When main() is called
  Then exit code is 1 and stderr is the usage string

Scenario: Invalid repository format prints error and returns one
  Given the argument "owner-repo"
  When main() is called
  Then exit code is 1 and stderr reports invalid repository format

Scenario: No actionable issues prints empty JSON array
  Given fetch_issues() returns [] for "owner/repo"
  When main() is called with ["owner/repo"]
  Then exit code is 0 and stdout is []

Scenario: CLI passes milestone title when provided
  Given fetch_issues() is stubbed to capture its inputs
  When main() is called with ["owner/repo", "--milestone", "Sprint 1"]
  Then fetch_issues() receives repository "owner/repo" and milestone title "Sprint 1"
```

**Coverage:** Unit test

---

## Feature: Dev Milestone Loop

> Unit: `afk.features.dev.handler.dev()`

```gherkin
Scenario: No open milestones found — early exit
  Given list_milestones() returns no milestones for owner "owner" and repo "repo"
  When dev() is called
  Then no issues are fetched and the AI agent is not invoked

Scenario: Milestone with no actionable issues is skipped
  Given list_milestones() returns milestone "Sprint 3"
    And fetch_issues() returns only non-actionable issues for that milestone
  When dev() is called
  Then the milestone is skipped without updating the execution log

Scenario: Milestone at max executions is skipped
  Given list_milestones() returns milestone "Sprint 3"
    And fetch_issues() returns actionable issues for that milestone
    And the execution log count for the milestone URL equals the max executions limit
  When dev() is called
  Then the AI agent is not invoked and the milestone is skipped

Scenario: Actionable milestone invokes agent and updates execution log
  Given list_milestones() returns milestone number 3 titled "Sprint 3"
    And fetch_issues() returns at least one actionable issue for that milestone
    And the execution log count for the milestone URL is 0
  When dev() is called
  Then AIAgent is invoked with prompt "/ralph:dev #3"
    And the execution log is updated for the milestone URL with no thread ids
```

**Coverage:** Unit test

---

## Feature: Dev CLI

> Unit: `afk.features.dev.cli`

```gherkin
Scenario: Parser applies default arguments for valid repository
  Given the argument ["--github_repo", "owner/repo"]
  When the dev CLI parser parses arguments
  Then github_repo is "owner/repo" and defaults are applied for max_executions, agent, prompt, and log_dir

Scenario: Parser accepts custom arguments
  Given the arguments ["--github_repo", "owner/repo", "--max_executions", "7", "--agent", "other-agent", "--prompt", "/custom:dev", "--log-dir", "custom-logs"]
  When the dev CLI parser parses arguments
  Then the parsed values match the provided overrides

Scenario: Parser requires github_repo argument
  Given no CLI arguments
  When the dev CLI parser parses arguments
  Then argparse exits with code 2

Scenario: GitHub repo validator rejects invalid repository format
  Given the repository value "owner-repo"
  When _github_repo() is called
  Then an ArgumentTypeError is raised

Scenario: Repo dir validator rejects missing directory
  Given a path to a directory that does not exist
  When _repo_dir() is called
  Then an ArgumentTypeError is raised

Scenario: Main delegates to handler with info logging
  Given parsed arguments for repository "owner/repo" and custom execution settings
    And AFK_DEBUG is not set
  When main() is called
  Then logging is configured at INFO level with file and stderr handlers
    And dev() is called with owner "owner" and repo "repo"

Scenario: Main uses debug logging when AFK_DEBUG is set
  Given parsed arguments for repository "owner/repo"
    And AFK_DEBUG is set
  When main() is called
  Then logging is configured at DEBUG level
```

**Coverage:** Unit test

---

## Feature: PR URL Parsing

> Unit: `parse_pr_url()`

```gherkin
Scenario: Valid PR URL is parsed correctly
  Given a PR URL "https://github.com/owner/repo/pull/123"
  When parse_pr_url() is called
  Then the result is ("owner", "repo", 123)

Scenario: PR URL with numeric owner/repo
  Given a PR URL "https://github.com/user42/my-repo/pull/7"
  When parse_pr_url() is called
  Then the result is ("user42", "my-repo", 7)
```

**Coverage:** Unit test

---

## Feature: Execution Log

> Unit: `ExecutionLog`

```gherkin
Scenario: New PR has zero execution count
  Given a fresh execution log
  When get_count() is called for a PR URL that was never processed
  Then the result is 0

Scenario: Count increments after update
  Given a fresh execution log
  When update() is called for PR "https://github.com/o/r/pull/1" with thread_ids ["T1"]
  And get_count() is called for that PR
  Then the result is 1

Scenario: Multiple updates increment count
  Given a fresh execution log
  When update() is called twice for the same PR
  And get_count() is called
  Then the result is 2

Scenario: Reset clears execution count
  Given an execution log with count 3 for a PR
  When reset() is called for that PR
  And get_count() is called
  Then the result is 0

Scenario: Reset on non-existent PR does not error
  Given a fresh execution log
  When reset() is called for a PR that has no record
  Then no error is raised
```

**Coverage:** Unit test

---

## Feature: Review Single PR (review_pull_request handler)

> Integration: mocked `GhCli`, spy `AIAgent`, mocked `ExecutionLog`

```gherkin
Scenario: PR with actionable threads triggers the AI agent
  Given a PR URL "https://github.com/owner/repo/pull/1"
    And the VCS returns 2 unresolved threads with labels "fix!:" and "suggest!:"
    And the execution count for the PR is 0
    And max_executions is 5
  When review_pull_request() is called
  Then the VCS client checks out the PR branch
    And AIAgent.run() is called with the 2 actionable threads and the prompt
    And the execution log is updated with the PR URL and thread IDs

Scenario: PR with no actionable threads skips the AI agent
  Given a PR URL "https://github.com/owner/repo/pull/2"
    And the VCS returns 1 resolved thread and 1 thread with label "nit:"
    And the execution count for the PR is 0
  When review_pull_request() is called
  Then AIAgent.run() is NOT called
    And the execution log is NOT updated

Scenario: PR with no actionable threads resets execution count if previously processed
  Given a PR URL "https://github.com/owner/repo/pull/3"
    And the VCS returns no actionable threads
    And the execution count for the PR is 2
  When review_pull_request() is called
  Then AIAgent.run() is NOT called
    And the execution log reset() is called for the PR

Scenario: PR at max executions is skipped
  Given a PR URL "https://github.com/owner/repo/pull/4"
    And the VCS returns 1 thread with label "fix!:"
    And the execution count for the PR is 5
    And max_executions is 5
  When review_pull_request() is called
  Then AIAgent.run() is NOT called
    And the execution log is NOT updated

Scenario: Custom prompt is passed to the AI agent
  Given a PR URL "https://github.com/owner/repo/pull/5"
    And the VCS returns 1 thread with label "fix!:"
    And the execution count is 0
    And the prompt is "/custom-prompt"
  When review_pull_request() is called
  Then AIAgent.run() is called with prompt "/custom-prompt"
```

**Coverage:** Integration test

---

## Feature: Review Multiple PRs (review_pull_requests handler)

> Integration: mocked `GhCli`, spy `AIAgent`, mocked `ExecutionLog`

```gherkin
Scenario: Multiple PRs with actionable threads are all processed
  Given github_user "dev" and github_repo "owner/repo"
    And 2 open PRs exist for user "dev"
    And each PR has at least 1 actionable thread
    And execution counts are 0 for both PRs
  When review_pull_requests() is called
  Then AIAgent.run() is called twice (once per PR)
    And the execution log is updated for each PR

Scenario: No open PRs found — early exit
  Given github_user "dev" and github_repo "owner/repo"
    And no open PRs exist for user "dev"
  When review_pull_requests() is called
  Then AIAgent.run() is NOT called

Scenario: Mix of actionable and non-actionable PRs
  Given github_user "dev" and github_repo "owner/repo"
    And 3 open PRs exist for user "dev"
    And PR #1 has actionable threads
    And PR #2 has only non-actionable threads
    And PR #3 has actionable threads
  When review_pull_requests() is called
  Then AIAgent.run() is called for PR #1 and PR #3
    And AIAgent.run() is NOT called for PR #2

Scenario: PR at max executions is skipped while others are processed
  Given github_user "dev" and github_repo "owner/repo"
    And 2 open PRs exist
    And PR #1 has execution count 5 (at max)
    And PR #2 has execution count 0
    And both have actionable threads
    And max_executions is 5
  When review_pull_requests() is called
  Then AIAgent.run() is called only for PR #2

Scenario: PR with no actionable threads and prior count resets execution log
  Given github_user "dev" and github_repo "owner/repo"
    And 1 open PR with no actionable threads
    And execution count for that PR is 3
  When review_pull_requests() is called
  Then exec_log.reset() is called for that PR
```

**Coverage:** Integration test

---

## Feature: Fetch Threads

> Unit: `fetch_threads()` handler · Integration: mocked `GhCli`

```gherkin
Scenario: Handler returns correctly shaped output for actionable threads
  Given a PR URL "https://github.com/owner/repo/pull/1"
    And the VCS returns 2 unresolved threads with labels "fix!:" and "suggest!:"
  When fetch_threads() is called
  Then the result is a list of 2 dicts
    And each dict contains keys: thread_id, prefix, path, lines, actionable_comment, comments
    And the first dict has thread_id "T1" and prefix "fix!"

Scenario: Handler returns empty list when no actionable threads exist
  Given a PR URL "https://github.com/owner/repo/pull/2"
    And the VCS returns threads with only "nit:" and "good:" labels
  When fetch_threads() is called
  Then the result is an empty list

Scenario: Handler excludes resolved and non-actionable threads
  Given a PR URL "https://github.com/owner/repo/pull/3"
    And the VCS returns 3 threads:
      | id | body                    | resolved |
      | T1 | fix!: broken null check | false    |
      | T2 | fix!: another issue     | true     |
      | T3 | nit: minor style        | false    |
  When fetch_threads() is called
  Then the result contains only thread T1
```

**Coverage:** Unit test · Integration test

```gherkin
Scenario: CLI invocation outputs JSON array to stdout
  Given a valid PR URL is passed as a CLI argument
  When fetch_threads.py is executed
  Then it exits with code 0
    And stdout contains a JSON array of actionable thread objects

Scenario: CLI invocation with no arguments
  Given fetch_threads.py is invoked with no arguments
  When it is executed
  Then it exits with code 1 and prints usage to stderr

Scenario: CLI invocation with invalid PR URL
  Given fetch_threads.py is invoked with "not-a-url"
  When it is executed
  Then it exits with code 1 and prints an error message to stderr
```

**Coverage:** Manual test

---

## Feature: CLI Argument Parsing (main.py)

> Manual testing

```gherkin
Scenario: No subcommand provided
  Given the CLI is invoked with no arguments
  When main.py is executed
  Then it exits with code 1 and prints usage to stderr

Scenario: Invalid subcommand
  Given the CLI is invoked with "unknown-cmd"
  When main.py is executed
  Then it exits with code 1 and prints usage to stderr

Scenario: review-prs with missing required arguments
  Given the CLI is invoked with "review-prs /tmp"
  When main.py is executed
  Then it exits with code 1 and prints usage to stderr

Scenario: review-pr with invalid PR URL format
  Given the CLI is invoked with "review-pr /tmp not-a-url"
  When main.py is executed
  Then it exits with code 1 and prints an error message

Scenario: review-pr with non-existent repo-dir
  Given the CLI is invoked with "review-pr /nonexistent https://github.com/o/r/pull/1"
  When main.py is executed
  Then it exits with code 1 and prints "repo-dir does not exist"

Scenario: --prompt flag without value
  Given the CLI is invoked with "review-pr /tmp https://github.com/o/r/pull/1 --prompt"
  When main.py is executed
  Then it exits with code 1 and prints "--prompt requires a value"

Scenario: max-executions is not a valid integer
  Given the CLI is invoked with "review-pr /tmp https://github.com/o/r/pull/1 abc"
  When main.py is executed
  Then it exits with code 1 and prints "max-executions must be an integer"
```

**Coverage:** Manual test
