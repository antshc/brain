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
Scenario: Issue with no labels is actionable
  Given an issue labeled []
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue with unrelated label is actionable
  Given an issue labeled ["enhancement"]
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue with blocked label is actionable
  Given an issue labeled ["blocked"]
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue with ready and blocked labels is actionable
  Given an issue labeled ["ready", "blocked"]
  When is_actionable is evaluated
  Then the result is True

Scenario: Issue with hitl label is not actionable
  Given an issue labeled ["hitl"]
  When is_actionable is evaluated
  Then the result is False

Scenario: Issue with prd label is not actionable
  Given an issue labeled ["prd"]
  When is_actionable is evaluated
  Then the result is False

Scenario: Issue with ready and prd labels is not actionable
  Given an issue labeled ["ready", "prd"]
  When is_actionable is evaluated
  Then the result is False

Scenario: Issue with blocked and hitl labels is not actionable
  Given an issue labeled ["blocked", "hitl"]
  When is_actionable is evaluated
  Then the result is False

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
  Given a list of issues with labels [], ["blocked"], ["prd"], and ["bug", "hitl"]
  When get_actionable_issues() is called
  Then the result contains issue numbers [1, 2]

Scenario: All issues are non-actionable — empty list returned
  Given a list of issues with labels ["prd"] and ["hitl"]
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

## Feature: VCS Client Spec Mapping

> Unit: `VCSClient.list_specs()`

```gherkin
Scenario: Raw spec nodes are mapped to Issue domain entities
  Given GhCli returns one raw spec dict with number 1, a title, a metadata-block body, and labels "spec" and "repo:owner/repo"
  When list_specs() is called
  Then the result contains one Issue with the same number, title, body, and labels

Scenario: No spec nodes map to an empty list
  Given GhCli returns no raw spec dicts
  When list_specs() is called
  Then the result is []
```

**Coverage:** Unit test

---

## Feature: GhCli Spec Query Construction

> Unit: `GhCli.list_specs_raw()`

```gherkin
Scenario: Open spec issues query is built and nodes are returned
  Given gh api graphql returns one open issue node labelled "spec" for owner "owner" and repo "repo"
  When list_specs_raw() is called
  Then subprocess.run() is invoked with the paginated spec GraphQL query and repository variables
  And the returned nodes have flattened labels and comments
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

Scenario: Handler includes blocked issues and excludes prd and hitl issues
  Given the repository "owner/repo"
    And the VCS returns one blocked issue, one prd issue, one hitl issue, and one unlabeled issue
  When fetch_issues() is called
  Then only the blocked and unlabeled issues are returned

Scenario: Spec number is forwarded to GhCli
  Given the repository "owner/repo"
    And the VCS is backed by a mocked GhCli
  When fetch_issues() is called with spec_number 7
  Then GhCli.fetch_issues_raw() is called with owner "owner", repo "repo", and spec number 7
```

**Coverage:** Integration test

---

## Feature: Fetch Issues CLI

> Unit: `fetch_issues.py`

```gherkin
Scenario: CLI rejects invalid options without fetching
  Given a missing or non-numeric spec value, a duplicate spec, or an unknown option
  When the CLI runs
  Then it returns one without fetching

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

Scenario: CLI passes spec number when provided
  Given fetch_issues() is stubbed to capture its inputs
  When main() is called with ["owner/repo", "--spec", "14"]
  Then fetch_issues() receives repository "owner/repo" and spec number 14
```

**Coverage:** Unit test

---

## Feature: Dev Spec Loop

> Unit: `afk.features.dev.handler.dev()`

```gherkin
Scenario: No open specs found — early exit
  Given list_specs() returns no specs for owner "owner" and repo "repo"
  When dev() is called
  Then no issues are fetched and the AI agent is not invoked

Scenario: Spec with no actionable issues and prior count resets execution log
  Given list_specs() returns spec 3
    And fetch_issues() returns only non-actionable issues for that spec
    And the execution log count for the spec URL is greater than 0
  When dev() is called
  Then the execution count is reset and the AI agent is not invoked

Scenario: Spec with no actionable issues and zero count does not reset execution log
  Given list_specs() returns spec 3
    And fetch_issues() returns only non-actionable issues for that spec
    And the execution log count for the spec URL is 0
  When dev() is called
  Then the spec is skipped without updating or resetting the execution log

Scenario: Spec at max executions is skipped
  Given list_specs() returns spec 3
    And fetch_issues() returns actionable issues for that spec
    And the execution log count for the spec URL equals the max executions limit
  When dev() is called
  Then the AI agent is not invoked and the spec is skipped

Scenario: Actionable spec invokes agent and updates execution log
  Given list_specs() returns spec number 3
    And fetch_issues() returns at least one actionable issue for that spec
    And the execution log count for the spec URL is 0
  When dev() is called
  Then AIAgent is invoked with prompt "/ralph:dev 3"
    And the execution log is updated for the spec URL with type "spec"

Scenario: Continue with the next spec when the current spec's run ends early
  Given list_specs() returns two actionable specs
    And the AI agent returns without error for the first spec
  When dev() is called
  Then the AI agent is invoked once per spec
    And the execution log is updated for both spec URLs

Scenario: Default ExecutionLog is created with dev log name
  Given no execution log is supplied
  When dev() is called
  Then ExecutionLog is created with the log directory, repository, and name "dev"
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

## Feature: Main Harness

> Manual test — no resolver script; the `harness` skill runs inline Python copied from a template

```gherkin
Scenario: The harness skill derives its own repo path
  Given the generated `harness` skill installed at `<H>/.github/skills/harness/SKILL.md`
  When the skill runs
  Then it reports `harnessRepoPath` as `<H>`, derived from its own folder's location, with no filesystem search

Scenario: Settings are emitted verbatim
  Given a sibling `.harness.json.user` holding a `repos` key
  When the skill runs
  Then it reports every top-level key from that file unchanged, alongside `harnessRepoPath`

Scenario: A missing settings file is reported as missing
  Given no sibling `.harness.json.user`
  When the skill runs
  Then it exits with an error reporting `missing`, and the caller falls back to cwd as the Harness Repo Path

Scenario: An unparseable settings file is reported as invalid
  Given a sibling `.harness.json.user` that is not valid JSON, or not a JSON object
  When the skill runs
  Then it exits with an error reporting `invalid` and the parse detail, and the caller stops rather than falling back

Scenario: Setup copies the skill and the pull command, creating settings only when missing
  Given a harness root with no `.github/skills/harness/`
  When `/init-harness` runs
  Then `SKILL.md` and `pull-repos.py` are copied byte-identical to their sources, `.harness.json.user` is created holding `{}`, and the file (not the folder) is confirmed gitignored

Scenario: Rerunning setup refreshes the skill and script but never the settings
  Given an existing `.github/skills/harness/` with a `.harness.json.user` already holding values
  When `/init-harness` runs again
  Then `SKILL.md` and `pull-repos.py` are overwritten and the settings file is left untouched
```

## Feature: Pull Repos

> Script CLI unit test, using local bare git repositories as `origin`

```gherkin
Scenario: No repos configured succeeds
  Given a Harness user settings file with no `repos` entries, or none at all
  When the pull command runs
  Then it reports "no repos configured" and exits successfully

Scenario: Configuration errors abort before any repository is touched
  Given a malformed `repos` entry, a duplicated repository name, an entry equal to the harness's own origin, or an unknown name argument
  When the pull command runs
  Then it exits with an error before touching any repository

Scenario: A read repository is force-reset keeping untracked files
  Given a read repository with dirty tracked files and untracked files, and a newer commit on its remote branch
  When the pull command runs
  Then the tracked files match the remote branch and the untracked files are kept

Scenario: A write repository with dirty tracked changes fails naming the files
  Given a write repository with uncommitted tracked changes
  When the pull command runs
  Then that repository fails naming the dirty files and the command exits with an error

Scenario: A write repository fast-forwards when clean
  Given a clean write repository behind its configured branch
  When the pull command runs
  Then it switches to the configured branch and fast-forwards it

Scenario: A write repository that has diverged is skipped
  Given a write repository with a local commit not on the remote branch, and the remote branch has also moved
  When the pull command runs
  Then that repository is skipped naming the divergence and its local commit is kept

Scenario: A branch missing on the remote is skipped
  Given a repository whose configured branch does not exist on its remote
  When the pull command runs
  Then that repository is skipped naming the missing branch

Scenario: A missing checkout with no clone tool available is skipped
  Given a repository with no local checkout and no clone tool on PATH
  When the pull command runs
  Then that repository is skipped naming the missing clone tool
```

**Coverage:** Script CLI unit test

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

---

## Feature: Skill Invocation Resolution

> Unit: `modules.repo_consistency.skill_invocations.find_dangling_skill_invocations()`

```gherkin
Scenario: Skill invocation naming an existing skill is not reported
  Given a SKILL.md invoking `/target`, and a `target` skill folder exists
  When find_dangling_skill_invocations() is called
  Then the result has no violations

Scenario: Skill invocation naming a nonexistent skill is reported
  Given a SKILL.md invoking `/ghost-skill`, and no such skill folder exists
  When find_dangling_skill_invocations() is called
  Then the result names the offending file and the unresolved skill name

Scenario: Skill invocation naming a generated skill template is not reported
  Given a skill invoking `/generated`, and a bundled `*.SKILL.template.md` declaring `name: generated`
  When find_dangling_skill_invocations() is called
  Then the result has no violations

Scenario: Template body text does not declare a generated skill
  Given a skill invoking `/ghost`, and a template containing `name: ghost` only outside frontmatter
  When find_dangling_skill_invocations() is called
  Then the result reports the unresolved skill name

Scenario: Current repository has no dangling skill invocations
  Given this repository's actual `plugins/`/`skills/` trees
  When find_dangling_skill_invocations() is called against the repo root
  Then the result has no violations
```

**Coverage:** Unit test

---

## Feature: Agent And Skill Frontmatter Completeness

> Unit: `modules.repo_consistency.required_frontmatter.find_frontmatter_violations()`

```gherkin
Scenario: File with all required frontmatter fields is not reported
  Given a SKILL.md with `name` and `description` frontmatter fields
  When find_frontmatter_violations() is called
  Then the result has no violations

Scenario: File missing a required frontmatter field is reported
  Given a SKILL.md with only a `name` frontmatter field
  When find_frontmatter_violations() is called
  Then the result names the offending file and the missing field

Scenario: Current repository's agents and skills carry required frontmatter
  Given this repository's actual `plugins/`/`skills/` trees
  When find_frontmatter_violations() is called against the repo root
  Then the result has no violations
```

**Coverage:** Unit test

---

## Feature: Architecture Index Consistency

> Unit: `modules.repo_consistency.architecture_index.find_architecture_index_violations()`

```gherkin
Scenario: Index row matching its record's heading is not reported
  Given an ARCHITECTURE.md ADR row whose title matches its linked record's heading
  When find_architecture_index_violations() is called
  Then the result has no violations

Scenario: Index row with a stale title is reported
  Given an ARCHITECTURE.md ADR row whose title no longer matches its linked record's heading
  When find_architecture_index_violations() is called
  Then the result names the mismatched row

Scenario: Current repository's architecture index matches its records
  Given this repository's actual ARCHITECTURE.md and docs/adr, docs/concepts records
  When find_architecture_index_violations() is called against the repo root
  Then the result has no violations
```

**Coverage:** Unit test


## Feature: GhCli Issue Pagination

```gherkin
Scenario: All sub-issue pages are collected and closed ones dropped
  Given multiple GitHub sub-issue pages of a spec, the first containing only a closed issue
  When fetch_issues_raw is called for that spec
  Then all pages are fetched and only open sub-issues are returned with flattened labels and comments

Scenario: All open issue pages are returned without a spec number
  Given multiple GitHub open issue pages
  When fetch_issues_raw is called without a spec number
  Then all pages are fetched and every issue is returned
```

**Coverage:** Unit test


## Feature: Proof Surface Selection

> Script unit test (`init-proof` `scaffold.py`)

```gherkin
Scenario: Surface choice is normalised to canonical order
  Given a surface choice of web, api, both, a comma list, or mixed case with spaces
  When the choice is parsed
  Then the surfaces are returned as web then api without duplicates

Scenario: Unknown or empty surface choice is refused
  Given an empty choice or a surface that is neither web nor api
  When the choice is parsed
  Then scaffolding is refused with an error
```

**Coverage:** Unit test


## Feature: Proof Repository Gate

```gherkin
Scenario: Repo without package json is refused
  Given a folder with no package.json
  When scaffold runs
  Then it is refused as not a pnpm repository

Scenario: Npm repo is refused and untouched
  Given a repository with package-lock.json only
  When scaffold runs
  Then it is refused pointing at the python language and no proof folder exists

Scenario: Package manager field marks a pnpm repo
  Given a package.json with packageManager pnpm
  When the repository is checked
  Then it is a pnpm repository

Scenario: Cli exits 2 with error for non pnpm repo
  Given a non-pnpm repository
  When the scaffold command runs
  Then it exits 2 and prints a JSON error
```

**Coverage:** Unit test


## Feature: Proof Kit Independence

```gherkin
Scenario: Kit imports only its own files
  Given the kit templates of a language
  When their imports are read
  Then none reaches the app, the mole, the commands or the runtime

Scenario: Kit names no runner command
  Given the kit templates of a language
  When their text is read
  Then no pnpm mole, python3 -m mole or other runner command appears

Scenario: Mole uses the kit
  Given the mole templates of a language
  When their imports are read
  Then they import the kit
```

**Coverage:** Unit test


## Feature: Proof Scaffold Output

```gherkin
Scenario: Both surfaces create both adapters
  Given a pnpm repository and surfaces web and api
  When scaffold runs
  Then both adapters, the proof kit, the mole and the verify-mole skill are created and there is no proof/engine

Scenario: Web only has no api adapter or api config
  Given surfaces web only
  When scaffold runs
  Then there is no api adapter, no api config in app.ts and no apiSurface in the adapter index

Scenario: Api only has no web adapter or web config
  Given surfaces api only
  When scaffold runs
  Then there is no web adapter, no web config, and the skill mentions HTTP and no screenshot

Scenario: No marker or placeholder is left in any file
  Given any surface choice
  When scaffold runs
  Then no surface marker or placeholder remains in a created file

Scenario: Both surfaces skill explains cross surface driving
  Given surfaces web and api
  When scaffold runs
  Then the verify-mole skill explains --surface web|api and screenshots

Scenario: App name is json escaped in app ts and plain in the skill
  Given an app name containing quotes
  When scaffold runs
  Then app.ts holds it as a JSON string and the skill heading holds it as text

Scenario: Example map lists exactly the chosen surfaces
  Given surfaces api only
  When scaffold runs
  Then the example map's frontmatter lists api and its driving section mentions the api command

Scenario: Kit and mole are copied byte for byte
  Given any surface choice
  When scaffold runs
  Then every proof/kit file and every mole file equals its template

Scenario: Unresolved todo markers remain for the research step
  Given any surface choice
  When scaffold runs
  Then app.ts keeps TODO(proof) markers for the researcher
```

**Coverage:** Unit test


## Feature: Proof Scaffold No Overwrite

```gherkin
Scenario: Existing files are kept and reported as skipped
  Given a repository that already has proof/app.ts
  When scaffold runs
  Then the file is unchanged and reported as skipped, not created

Scenario: Second run creates nothing
  Given a repository scaffolded once
  When scaffold runs again
  Then nothing is created and everything from the first run is skipped
```

**Coverage:** Unit test


## Feature: Proof Package Setup

```gherkin
Scenario: Scripts are added and indent is preserved
  Given a package.json with its own scripts
  When scaffold runs
  Then mole, prove, test:proof and typecheck:proof are added and the file's indent and scripts are preserved

Scenario: Conflicting script is kept and reported
  Given a package.json whose mole script differs
  When scaffold runs
  Then the script is kept and reported as conflicting

Scenario: Declared dev dependencies are not reinstalled
  Given some required devDependencies already declared
  When scaffold runs without installing
  Then only the missing ones are reported and install is skipped

Scenario: Workspace root installs with dash w
  Given a pnpm-workspace.yaml at the repository root
  When the missing packages are installed
  Then pnpm add -D -w is used

Scenario: Ignored build scripts are approved
  Given pnpm refusing an install with ignored build scripts
  When the packages are installed
  Then the blocked packages are approved and the install is reported as installed
```

**Coverage:** Unit test


## Feature: Proof Gitignore

```gherkin
Scenario: Missing gitignore is created
  Given a repository without .gitignore
  When scaffold runs
  Then .gitignore holds /proof/.runs/

Scenario: Line is appended once to an existing file
  Given an existing .gitignore without the entry
  When scaffold runs twice
  Then the entry is appended once, and the second run finds it present

Scenario: Equivalent existing entry is respected
  Given a .gitignore with proof/.runs/
  When scaffold runs
  Then it is reported present and not changed
```

**Coverage:** Unit test


## Feature: Proof Surface Markers

```gherkin
Scenario: Ts block markers
  Given a TypeScript block guarded by an api marker
  When it is rendered for web only and for api
  Then the block is dropped or kept without markers

Scenario: Markdown inline and block markers
  Given Markdown guarded inline by web+api and as a block by web-only
  When it is rendered for both surfaces and for web
  Then only the sections whose expression holds remain

Scenario: Unknown marker expression is an error
  Given a marker naming an unknown surface
  When it is rendered
  Then rendering fails

Scenario: Unresolved placeholder is an error
  Given a template with an unknown placeholder
  When it is rendered
  Then rendering fails
```

**Coverage:** Unit test


## Feature: Proof Plugin Layout

```gherkin
Scenario: Only the four skills carry a skill md
  Given the proof plugin folder
  When SKILL.md files are listed
  Then only init-proof, maintain-proof, create-verification-skill and playwright-cli have one

Scenario: Plugin manifest points at the skills folder
  Given the proof plugin manifest
  When it is read
  Then it names proof and ./skills

Scenario: Marketplace lists the plugin
  Given the marketplace file
  When the proof entry is read
  Then it points at ./plugins/proof

Scenario: Template skill is renamed on scaffold
  Given a scaffolded repository
  When the verify-mole folder is listed
  Then it holds SKILL.md and no template-named file

Scenario: Every skill has name and description frontmatter
  Given each proof skill
  When its frontmatter is read
  Then it has the skill's name and a description
```

**Coverage:** Unit test


## Feature: Proof Language Selection

> Script unit test (`init-proof` `scaffold.py`, `--language`)

```gherkin
Scenario: Language choice is normalised
  Given a language of typescript, ts, python or py in any case with spaces
  When the choice is parsed
  Then typescript or python is returned

Scenario: Unknown language is refused
  Given an empty language or one that is neither typescript nor python
  When the choice is parsed
  Then scaffolding is refused saying to use typescript or python

Scenario: Language defaults to typescript on the command line
  Given the scaffold command without --language in a non-pnpm folder
  When it runs
  Then it exits 2 with the pnpm repository error

Scenario: Python language is accepted on the command line
  Given the scaffold command with --language python
  When it runs
  Then it exits 0 and reports the language python
```

**Coverage:** Unit test


## Feature: Proof Python Kit Gate

```gherkin
Scenario: Any folder without package json is accepted
  Given a folder with no package.json
  When scaffold runs for python
  Then the kit is created and no package.json exists

Scenario: Old python is refused and untouched
  Given Python older than 3.10
  When scaffold runs for python
  Then it is refused naming Python 3.10 and no proof folder exists
```

**Coverage:** Unit test


## Feature: Proof Python Kit Scaffold Output

```gherkin
Scenario: Both surfaces create the kit, mole, adapters and skill
  Given a repository and surfaces web and api
  When scaffold runs for python
  Then the python kit, mole, app config, both adapters, requirements, tests and the verify-mole skill are created and no TypeScript file is

Scenario: Web only has no api adapter or api config
  Given surfaces web only
  When scaffold runs for python
  Then there is no api adapter, no ApiConfig in app.py and no api_surface in the adapter index

Scenario: Api only has no web adapter or web config
  Given surfaces api only
  When scaffold runs for python
  Then there is no web adapter, no WebConfig in app.py and the skill speaks of HTTP without screenshots

Scenario: No marker or placeholder is left in any file
  Given each surface choice
  When scaffold runs for python
  Then no surface marker or {{PLACEHOLDER}} remains in any file

Scenario: Every scaffolded python file is valid python
  Given each surface choice
  When scaffold runs for python
  Then every scaffolded .py file parses

Scenario: Verify mole skill and maps use the python commands
  Given a python scaffold
  When the verify-mole files are read
  Then they name python3 -m mole and proof/app.py and never pnpm

Scenario: Kit and mole are copied byte for byte
  Given a python scaffold
  When the files in proof/kit and mole are compared with the templates
  Then they are identical and there is no proof/engine

Scenario: App name is json escaped in app py and plain in the skill
  Given an app name with quotes
  When scaffold runs for python
  Then app.py holds it as a valid string literal and the skill holds it plain

Scenario: Example map lists exactly the chosen surfaces
  Given surfaces api only
  When scaffold runs for python
  Then the example map frontmatter lists api and not web

Scenario: Unresolved todo markers remain for the research step
  Given a python scaffold
  When app.py is read
  Then it still holds TODO(proof) markers

Scenario: Typescript scaffold is unchanged by the python templates
  Given a pnpm repository
  When scaffold runs for typescript
  Then no python file is created and the skill uses pnpm mole
```

**Coverage:** Unit test


## Feature: Proof Python Kit No Overwrite

```gherkin
Scenario: Existing files are kept and reported as skipped
  Given a repository that already has proof/app.py
  When scaffold runs for python
  Then app.py is untouched and reported as skipped

Scenario: Second run creates nothing
  Given a repository scaffolded for python
  When scaffold runs again
  Then nothing is created
```

**Coverage:** Unit test


## Feature: Proof Python Kit Install

```gherkin
Scenario: Requirements list the kit dependencies
  Given a python scaffold
  When proof/requirements.txt is read
  Then it lists playwright, pytest and mypy

Scenario: Install is skipped on request and never touches package json
  Given scaffold runs for python with install off
  When the result is read
  Then install is skipped, no scripts were added and no package.json exists

Scenario: Install runs pip with the requirements file
  Given scaffold runs for python with install on
  When it installs
  Then it runs python -m pip install -r proof/requirements.txt and reports installed

Scenario: Failed install is reported not raised
  Given pip fails
  When scaffold runs for python
  Then the result says the install failed with the last output line and the files are still created
```

**Coverage:** Unit test


## Feature: Proof Python Kit Gitignore

```gherkin
Scenario: Runs folder and bytecode are ignored
  Given a repository without .gitignore
  When scaffold runs for python
  Then .gitignore holds /proof/.runs/ and __pycache__/

Scenario: Existing entries are respected and missing ones appended
  Given a .gitignore with an equivalent __pycache__ entry
  When scaffold runs for python
  Then only /proof/.runs/ is appended
```

**Coverage:** Unit test


## Feature: Proof Python Kit Engine

> Runs the scaffolded kit; needs playwright installed

```gherkin
Scenario: Scaffolded selftest passes
  Given a python scaffold for web, api or both
  When proof/test_features.py runs
  Then it passes

Scenario: Selftest catches a map that drifted from the registry
  Given a map with no feature
  When proof/test_features.py runs
  Then it fails on the map and feature pairing

Scenario: Deep equality does not treat true as one
  Given the kit's equality helper
  When it compares True with 1, lists of different length and different keys
  Then only equal values match

Scenario: Help lists commands with the python invocation
  Given a python scaffold
  When mole help runs
  Then it prints usage with python3 -m mole

Scenario: Unknown command exits 2 with a next step
  Given a python scaffold
  When mole runs an unknown command
  Then it exits 2 and the JSON error names the help command

Scenario: Commands that need a session say nothing is running
  Given no mole session
  When mole snapshot runs
  Then it exits 2 with "Nothing is running."
```

**Coverage:** Unit test


## Feature: Proof Python Kit End To End

> Needs playwright and its Chromium

```gherkin
Scenario: Up start doctor prove stale and down
  Given a python scaffold in a git repo with a small HTTP app
  When mole up --start runs, then doctor, prove, prove --surface api, snapshot and api get
  Then doctor is ok, the proof is PASS with a screenshot and no page errors, the api-only run says web did not run, and snapshot and api get show the app
  And after the source changes, prove refuses and doctor reports STALE
  And down stops mole and removes the session

Scenario: A failing check is a fail receipt with its hint
  Given a feature whose check expects the wrong value
  When mole prove runs
  Then it exits 1 with verdict FAIL and the check's hint as the first next step
```

**Coverage:** Integration test

## Feature: Durable Evidence Evaluation

**Coverage:** `tests/proof/init-proof/test_evidence.py` — offline unit/integration tests.

- Subset matching is typed and order independent: extra fields/reordering survive; missing/null and boolean/numeric distinctions remain strict.
- Saved evidence passes with original receipt: no receipt schema additions or browser runtime imports.
- Gaps error and observed mismatch fails: tampering, missing/duplicate checks, manifest mismatch and traversal never pass.
- Required logs are scoped and complete: historical events do not satisfy the current run; malformed logs error.
- Test reports normalize failures skips and namespaces: TRX/JUnit identities and counters remain consistent.
- Provenance gaps never pass: wrong build/revision/contract, dirty state and missing run/environment are ERROR.
- Invalid capture never passes: incomplete, stale, wrong-scope or corrupt artifacts are ERROR.
- Test report gates: failed/unexpected skipped tests FAIL; zero discovery, missing IDs, malformed/stale/untrusted reports ERROR.
- CLI VPG example is offline and preserves history: API/task/reloaded UI/request/console/log/test evidence passes with live I/O blocked, each evaluation persists, changed contract refuses before import.
- Log adapters and matchers: JSONL/Serilog, OTLP typed attributes, text scopes, event fields/counts and reviewed regex.
- Duplicate retries and invalid XML are rejected: ambiguous IDs, reruns, DTD, runner failures and invalid JSON outcomes cannot pass.
- Capture is immutable and project tools survive scaffold: no overwrites after capture/finalization or scaffold reruns.
