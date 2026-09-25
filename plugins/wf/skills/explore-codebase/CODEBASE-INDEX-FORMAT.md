# Codebase Index Format
<!-- A codebase index is the only map of the repositories an exploration may need: they sit outside the harness, at paths nothing on disk advertises. One file per codebase family, named `{{family}}-codebase-index.md`, anywhere under `$HARNESS_REPO_PATH`. It maps a name — or a trigger signal a question would carry — to a local path, a GitHub repository URL, a package owner, or a boundary where tracing stops. Keep it about *where things live*, not what they do. -->

## Structure

```md
## Local deployables and repositories

<!-- One row per independently deployed unit or standalone repository. Local path: absolute, `~`-rooted; several comma-separated paths when one deployable spans folders of one checkout. GitHub repository URL: the `origin` remote, repeated on every row that shares a checkout. Trigger signals: comma-separated words a question would actually use — names, domain nouns, folder names, symbols — matched semantically, never a description. -->

| Deployable name | Responsibility | Local path | GitHub repository URL | Trigger signals |
|---|---|---|---|---|
| {{deployableName}} | {{oneLineResponsibility}} | `{{absoluteLocalPath}}` | `{{repositoryUrl}}` | {{triggerSignals}} |

## Shared package ownership *(optional)*

<!-- One row per package family consumed from a feed rather than built here, so a type absent from local source resolves to an owner instead of a disk-wide search. Trailing `*` marks a family prefix. Local path is `-` unless that repository is checked out. Close with a catch-all row for the unlisted rest of the namespace. -->

| Package family | Owning repository | Local path |
|---|---|---|
| `{{packageFamily}}` | `{{owningRepository}}` | {{absoluteLocalPathOrDash}} |
| Unlisted `{{namespace}}*` | Unresolved; search `{{organization}}` by exact package ID | - |

## Terminal infrastructure boundaries

Stop source tracing at these boundaries after recording the operation, protocol, authentication,
errors, and configuration binding relevant to the question.

<!-- One row per managed service, registry, feed, external API, proxy, or runtime whose internals are not this codebase's source. Navigation anchor: the last artifact on our side of the line — the calling accessor, the configuration file, the compose folder — optionally naming the skill that owns the far side. -->

| Boundary | Responsibility | Navigation anchor |
|---|---|---|
| {{boundaryName}} | {{whatItOwns}} | {{lastArtifactOnOurSide}} |

## Refreshing the map

<!-- One line per source that regenerates a section above, so the index is rebuilt from the codebase rather than from memory. -->

- {{whatItRefreshes}}: `{{pathOrCommand}}`.
- Local repository URL: that checkout's `.git/config` or `git remote get-url origin`.

{{routingNotes}}
<!-- Optional short paragraphs: where a cross-cutting flow starts and which downstream deployables it must follow; where to search a repository whose layout is non-obvious; when to fall back to a package or source-inspection skill. -->

## Gotchas

<!-- One line per correction that has already cost an exploration a wrong turn: a path that looks like another, a boundary that is a separate repository, a map that is not source of truth, a search that must not widen. -->

- {{mistakenAssumption}} — {{correction}}.
```

## Rules

- **Only what the disk hides.** A row earns its place when a name, path, owner, or boundary cannot be discovered from the harness checkout itself. Responsibilities, designs, and flows belong in `ARCHITECTURE.md` and the service docs.
- **Paths are verified, never inferred.** Every local path is one that exists at authoring time, and every repository URL comes from that checkout's `origin`. A neighbouring path is not a substitute for a missing one.
- **Trigger signals are the question's words.** Write the terms a caller would type — product names, domain nouns, symbols, file globs — not a restatement of the responsibility column. An empty cell never matches.
- **One row per deployed unit.** Scripts, playbooks, manifests, and compose files are artifacts of the unit that owns them unless source proves they ship independently.
- **Boundaries end tracing.** Anything listed under terminal boundaries is where exploration stops; give the anchor on our side so the stop is navigable rather than a dead end.
- **Keep it refreshable.** Every section names the source it is derived from, so the index can be regenerated instead of hand-maintained.
- **Gotchas are earned.** Add a line only after a real wrong turn; drop it once the layout it warns about is gone.
