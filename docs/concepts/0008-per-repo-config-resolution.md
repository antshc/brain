---
id: "0008"
title: Per-Repo Config Resolution
status: Accepted
trigger: >-
  a skill or agent reading per-repository configuration, adding a dotfile or convention folder under the Harness
  Repo Path, choosing between a fixed config path and a search, config lookup falling back to a second location,
  a config file holding a secret, deciding whether config is committed or gitignored, a component re-deriving a
  caller-supplied path
summary: >-
  Per-repository configuration is resolved from exactly one declared root — the Harness Repo Path — using exactly
  one strategy, either a fixed path or a search bounded to that root; a second fallback location is never added,
  because its failure mode is silent degradation rather than an error. Configuration is split by lifecycle rather
  than by topic: secrets are gitignored and per-developer, team conventions are committed, and the two never share
  a file.
default: >-
  Resolve a per-repo config file at a fixed path under the Harness Repo Path; use a search bounded to that root
  only when the file is user-authored and may legitimately live in a nested workspace folder.
owns:
  - "per-repository config file resolution"
  - "config secret versus committed-convention placement"
applies_to:
  - plugins/**
  - .crew/**
  - .atlassian
related: ["0002", "0005"]
---

# Per-Repo Config Resolution

## Purpose

A skill installed into many repositories needs per-repository settings, and the moment two lookup paths exist the
failure mode stops being an error and becomes silent degradation — the skill finds nothing, reports nothing, and
runs with no conventions at all. This Concept fixes how such a file is located and how its contents are split.

## Rules

- A per-repo config file MUST declare exactly one resolution root, and that root MUST be the Harness Repo Path.
- A resolution strategy MUST NOT search above its declared root, and MUST NOT reach the filesystem root.
- A record MUST name exactly one strategy — fixed path or bounded search — and MUST NOT add a second lookup path
  as a fallback to the first.
- A path supplied by a caller through a trusted channel MUST be used as given; a component MUST NOT re-derive,
  guess, or search for it.
- A supplied-but-invalid path MUST stop the caller as blocked rather than trigger a search.
- A config file holding a credential MUST be gitignored.
- A config file holding a credential MUST NOT also hold committed team conventions, and vice versa.
- A skill reading a credential file MUST NOT print, quote, log, or commit its values.

## Design Guidance

Choose the strategy from where the file comes from, not from convenience:

| Strategy | Use when | Reference |
|----------|----------|-----------|
| Fixed path | a setup skill scaffolds the file, so its location is guaranteed | `$HARNESS_REPO_PATH/.crew/<FILE>` ([0002](../adr/0002-crew-is-agnostic.md)) |
| Bounded search | the file is user-authored and may sit in a nested workspace folder | `.atlassian`, searched from the Harness Repo Path downward ([0005](../adr/0005-atl-is-mcp-first.md)) |

Split by lifecycle, because the two halves have different readers and different homes:

| Content | Home | In git |
|---------|------|--------|
| Credentials, per-developer connection facts | a single dotfile, e.g. `.atlassian` | no |
| Team conventions, field maps, item-type defaults | committed files or generated repo-level skills under `.github/skills/` | yes |

A skill that degrades when its config is absent states per field what it can still do — an unresolved field is
empty, not fatal — rather than refusing wholesale or inventing a discovery call the config exists to avoid.

## Violation signals

- A lookup that tries a second directory after the first misses.
- A search whose termination condition is the filesystem root rather than a declared root.
- An API token and a committed convention table in the same file.
- A component calling a discovery API for a value its config file already carries.
