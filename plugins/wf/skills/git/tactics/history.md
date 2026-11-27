# History

Read-only file and line archaeology: who changed what, when, and in which commit. Branch-range listing belongs to Commits.

## Execute

Run against an explicit checkout; pin `<rev>` to a SHA when the answer depends on it. Never check out, reset, or write.

| Need | Command |
|---|---|
| File history through renames | `git -C <checkout> log --follow --format='%H %ad %an %s' --date=short -- <file>` |
| Commits adding or removing exact text | `git -C <checkout> log -S '<text>' --format='%H %ad %an %s' --date=short [-- <file>]` |
| Commits whose diff matches a regex | `git -C <checkout> log -G '<regex>' --format='%H %ad %an %s' --date=short [-- <file>]` |
| Line authorship | `git -C <checkout> blame -L <start>,<end> [<rev>] -- <file>` |
| Authorship before a known commit | `git -C <checkout> blame -L <start>,<end> <sha>^ -- <file>` |
| One commit | `git -C <checkout> show --stat --format=fuller <sha>` then `git -C <checkout> show <sha> -- <file>` |
| File changes in a range | `git -C <checkout> log -p <old>..<new> -- <file>` |
| Co-changed files | `git -C <checkout> show --name-only --format= <sha>` |
| Commits naming a work item or PR | `git -C <checkout> log --grep='<KEY-123>' --format='%H %ad %an %s' --date=short` |

- **Recency bias.** The latest commit is rarely the origin; follow `blame <sha>^` back to the change that introduced the shape.
- **Moved code.** Blame stops at moves and reformatting; add `-w -C` or rerun `log -S` on the moved text.
- **Squash and merge.** A squash commit hides intermediate history; take PR numbers from subjects and read the PR through the `github` skill.

Return SHAs, dates, authors, subjects, and the exact command for each finding; an empty result is a finding.
