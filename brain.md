# Brain

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
