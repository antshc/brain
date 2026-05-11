# ralph

AFK automated PR review service. Finds open GitHub PRs, fetches unresolved review threads, and drives the Copilot CLI agent to address them.

---

## Installation

```bash
sudo apt install python3-pip        # if pip is not installed
python3 -m pip install git+https://github.com/antshc/ralph.git
```

This installs two CLI entry points: `ralph` and `ralph-fetch-threads`.

### Dependencies

**Runtime (must be on your `PATH`):**

| Tool | Purpose | Install |
|---|---|---|
| `gh` | GitHub CLI — fetches PRs and review threads | https://cli.github.com |
| `copilot` | GitHub Copilot CLI — drives the AI agent | `gh extension install github/gh-copilot` |
| `git` | Repository operations | https://git-scm.com |

**Python:** 3.10 or newer.

**Dev/test extras:**

```bash
python3 -m pip install "ralph-tools[dev]"  # installs pytest
```

---

## Running

### Review PRs

Process all open PRs for a user in a repository:

```bash
ralph review-prs <repo-dir> <github-user> <owner/repo> [max-executions] [--prompt <text>]
```

Process a single PR by URL:

```bash
ralph review-pr <repo-dir> <pr-url> [max-executions] [--prompt <text>]
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
ralph review-prs /path/to/repo alice owner/my-repo

# Single PR with a custom prompt and max 3 attempts
ralph review-pr /path/to/repo https://github.com/owner/my-repo/pull/42 3 --prompt /fix
```

---

### Fetch Threads

Fetch actionable review threads for a PR and print them as JSON to stdout. Useful for inspecting threads or piping into other tools (drop-in replacement for `fetch-threads.sh`).

```bash
ralph-fetch-threads <pr-url>
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
ralph-fetch-threads https://github.com/owner/my-repo/pull/42
```

---

## Running Tests

```bash
# All tests
python3 -m pytest tools/ -v

# Unit tests only
python3 -m pytest tools/tests/unit/ -v
```

---

## Troubleshooting

### `Cannot import 'setuptools.backends.legacy'`

The `pyproject.toml` uses a non-existent build backend. Fix it before installing:

```bash
git clone https://github.com/antshc/ralph.git
cd ralph
# Fix the build backend
sed -i 's|build-backend = "setuptools.backends.legacy:build"|build-backend = "setuptools.build_meta"|' pyproject.toml
python3 -m pip install .
```

Or install directly from the local directory after cloning.

---

### `ralph: command not found`

The pip scripts directory is not on your `PATH`. Add it:

```bash
# Find where pip installs scripts
python3 -m pip show ralph-tools | grep Location
# Typically add ~/.local/bin (Linux/WSL) or the venv's bin/
export PATH="$HOME/.local/bin:$PATH"
```

Add the `export` line to your `~/.bashrc` or `~/.zshrc` to make it permanent.

---

### `gh: command not found` / `copilot: command not found`

Install the missing tools:

```bash
# GitHub CLI
sudo apt install gh             # Ubuntu/Debian/WSL
# or: https://cli.github.com/manual/installation

# GitHub Copilot CLI extension
gh auth login                   # if not already authenticated
gh extension install github/gh-copilot
```

---

### `gh auth` / API rate limit errors

Ensure you are authenticated with the GitHub CLI:

```bash
gh auth status
gh auth login   # if not authenticated
```

---

### WSL: slow performance or path issues

Use Linux-native paths inside WSL (e.g. `/home/user/project`) rather than Windows UNC paths (`\\wsl.localhost\...`). Run all commands from within the WSL terminal.