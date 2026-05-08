# ralph

AFK automated PR review service. Finds open GitHub PRs, fetches unresolved review threads, and drives the Copilot CLI agent to address them.

---

## Running

### Review PRs

Process all open PRs for a user in a repository:

```bash
python3 app/main.py review-prs <repo-dir> <github-user> <owner/repo> [max-executions] [--prompt <text>]
```

Process a single PR by URL:

```bash
python3 app/main.py review-pr <repo-dir> <pr-url> [max-executions] [--prompt <text>]
```

| Argument | Description |
|---|---|
| `repo-dir` | Path to the local repository clone |
| `github-user` | GitHub username to filter open PRs by author (`review-prs` only) |
| `owner/repo` | GitHub repository in `owner/repo` format (`review-prs` only) |
| `pr-url` | Full GitHub PR URL, e.g. `https://github.com/owner/repo/pull/123` (`review-pr` only) |
| `max-executions` | Max processing attempts per PR before skipping (default: `5`) |
| `--prompt` | Prompt text passed to the AI agent (default: `/review`) |

**Examples:**

```bash
# All open PRs for user "alice" in owner/my-repo
python3 app/main.py review-prs /path/to/repo alice owner/my-repo

# Single PR with a custom prompt and max 3 attempts
python3 app/main.py review-pr /path/to/repo https://github.com/owner/my-repo/pull/42 3 --prompt /fix
```

---

### Fetch Threads

Fetch actionable review threads for a PR and print them as JSON to stdout. Useful for inspecting threads or piping into other tools (drop-in replacement for `fetch-threads.sh`).

```bash
python3 app/fetch_threads.py <pr-url>
```

| Argument | Description |
|---|---|
| `pr-url` | Full GitHub PR URL, e.g. `https://github.com/owner/repo/pull/123` |

Output is a JSON array of actionable thread objects:

```json
[
  {
    "thread_id": "PRRT_...",
    "prefix": "fix!",
    "path": "src/foo.py",
    "lines": "10-15",
    "actionable_comment": "fix!: broken null check",
    "comments": [
      { "author": "reviewer", "body": "fix!: broken null check" }
    ]
  }
]
```

**Example:**

```bash
python3 app/fetch_threads.py https://github.com/owner/my-repo/pull/42
```

---

## Running Tests

```bash
# All tests
python3 -m pytest unit_tests/ integration_tests/ -v

# Unit tests only
python3 -m pytest unit_tests/ -v

# Integration tests against live GitHub API and Copilot CLI
python3 -m pytest integration_tests/ --real -v
```