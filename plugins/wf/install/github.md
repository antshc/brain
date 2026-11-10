# GitHub setup

## Setup labels

Run from the tracker repository: the current repository for a single repo, the docs/harness root for a wrapping repo. GitHub issues are the only backlog backend for this workflow; local documents are not a tracker.

1. Resolve the sibling `../skills/github/scripts/github.py` from this installer's absolute directory as `GH_TOOL`. This needs a local copy of this installer: the installed `wf` plugin directory or a Brain checkout. If the installer was only read from the online repository, install `wf@brain` first (see [install.md](./install.md)) and use the installed copy; stop if `GH_TOOL` is not on disk. Do not fetch the script remotely. Use the `git` Repository tactic to resolve the tracker checkout. Labels-only mode can run from the WF source tree. Stop on missing tooling or ambiguous routing.
2. Resolve `github-labels.json` from this installer directory. Run `GH_TOOL label ensure --repo TRACKER --manifest FILE` using the Issues tactic.
3. Require verified presence of all manifest labels. Preserve existing label colors and descriptions. Report incomplete setup with confirmed labels and blockers.
