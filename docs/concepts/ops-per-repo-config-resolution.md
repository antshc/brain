# Per-Repo Config Resolution

## Purpose

A skill installed into many repositories needs per-repository settings, and the moment two lookup paths exist the
failure mode stops being an error and becomes silent degradation — the skill finds nothing, reports nothing, and
runs with no conventions at all. This Concept fixes how such a file is located and how its contents are split.

## Rules

- A per-repo config file MUST declare exactly one resolution root, and that root MUST be the Harness Repo Path.
- A per-repo config file MUST be read at one fixed path under that root; a component MUST NOT search for it, and
  MUST NOT add a second lookup path as a fallback.
- Per-developer settings MUST live in one gitignored file per plugin, beside that plugin's repository-level skill,
  holding that plugin's keys at the top level; a plugin MUST NOT keep its settings in another plugin's file.
- A credential MUST live in its own plugin's settings file and MUST be read only by the script that uses it, on the
  branch that uses it; a resolver MUST NOT emit it.
- A setup skill MUST create a settings file only when it is missing and MUST NOT overwrite an existing one; the
  repository-level skill it copies from a template MAY be overwritten on every run.
- A config that exists once per variant MUST encode the variant in the filename, and an unsuffixed name MUST mean
  shared across variants.
- A missing variant file MUST be treated as absent; reading the unsuffixed name instead is the second lookup path
  under another spelling.
- A path supplied by a caller through a trusted channel MUST be used as given; a component MUST NOT re-derive,
  guess, or search for it.
- A supplied-but-invalid path MUST stop the caller as blocked rather than trigger a search.
- A repository checkout path MUST be derived from the Harness Repo Path and the repository's name —
  `workspace/<name>`, or the Harness Repo Path itself when the repository is the harness's `origin`; it MUST NOT
  be stored in, or looked up from, the per-developer settings.
- A config file holding a credential MUST be gitignored by its filename, never by the skill folder that holds it,
  because that folder's `SKILL.md` is committed.
- A config file holding a credential MUST NOT also hold committed team conventions, and vice versa.
- A skill reading a credential file MUST NOT print, quote, log, or commit its values.

## Design Guidance

Every file sits at a fixed path; the shape of the path follows what the file holds:

| Shape | Use when | Reference |
|----------|----------|-----------|
| Fixed path | a setup skill scaffolds the file, so its location is guaranteed | `$HARNESS_REPO_PATH/.crew/<FILE>` ([Crew agents own their workflows and use codebase instructions](../adr/crew-is-agnostic.md)) |
| Fixed path, variant-suffixed | the same config exists once per variant, and one root still holds them all | `$HARNESS_REPO_PATH/.crew/CHORE-<stack>.md` ([Crew agents own their workflows and use codebase instructions](../adr/crew-is-agnostic.md)) |
| Fixed path, beside the owning skill | per-developer settings and credentials for one plugin | `.github/skills/harness/.harness.json.user`, `.github/skills/preflight-atlassian/.atlassian.json.user` |

A script reads its plugin's file straight from disk with the standard library's parser, and sits beside that file
when it is copied into the repository; a skill with no script reads its resolver's output, which carries every key
except credentials. Each reader has exactly one path to a value.

A variant split belongs in the filename rather than a subfolder: the folder encodes the same fact while making
"shared by every variant" a position in a tree instead of a visible property of the name, and it tempts a reader
to treat the parent directory as a fallback.

Split by lifecycle, because the two halves have different readers and different homes:

| Content | Home | In git |
|---------|------|--------|
| Credentials | the owning plugin's settings file, beside its repository-level skill | no |
| Per-developer connection facts, working-set repos and pull branches | the owning plugin's settings file, beside its repository-level skill | no |
| Team conventions, field maps, item-type defaults | committed files or generated repo-level skills under `.github/skills/` | yes |

A skill that degrades when its config is absent states per field what it can still do — an unresolved field is
empty, not fatal — rather than refusing wholesale or inventing a discovery call the config exists to avoid.

## Exceptions

- The harness anchor: the repository-level `harness` skill, generated into the harness by `init-harness`, derives the
  Harness Repo Path from its own location — its folder's third ancestor (`.github/skills/harness/`) — with no
  search. It is the one path derived from a skill's location rather than read under a root, because it defines the
  root. A missing settings file beside it is an error that callers answer by using cwd; an unparseable one stops
  them.

## Violation signals

- A lookup that tries a second directory after the first misses.
- A variant file missing, and the unsuffixed file read in its place.
- Any search for a per-repo config file, including a cwd walk-up for the harness anchor.
- One plugin's keys or credentials in another plugin's settings file.
- An API token and a committed convention table in the same file.
- A credential value in resolver output, a log, or agent-visible stdout.
- A component calling a discovery API for a value its config file already carries.
