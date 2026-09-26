# Per-Repo Config Resolution

## Purpose

A skill installed into many repositories needs per-repository settings, and the moment two lookup paths exist the
failure mode stops being an error and becomes silent degradation — the skill finds nothing, reports nothing, and
runs with no conventions at all. This Concept fixes how such a file is located and how its contents are split.

## Rules

- A per-repo config file MUST declare exactly one resolution root, and that root MUST be the Harness Repo Path.
- A per-repo config file MUST be read at one fixed path under that root; a component MUST NOT search for it, and
  MUST NOT add a second lookup path as a fallback.
- Per-developer settings MUST live in one gitignored file holding one section per plugin; a section MUST exist only
  when its plugin owns a key.
- A credential MUST live in that file's dedicated credentials section, keyed by plugin, and MUST be read only by the
  script that uses it, on the branch that uses it; a resolver MUST NOT emit the credentials section.
- A config that exists once per variant MUST encode the variant in the filename, and an unsuffixed name MUST mean
  shared across variants.
- A missing variant file MUST be treated as absent; reading the unsuffixed name instead is the second lookup path
  under another spelling.
- A path supplied by a caller through a trusted channel MUST be used as given; a component MUST NOT re-derive,
  guess, or search for it.
- A supplied-but-invalid path MUST stop the caller as blocked rather than trigger a search.
- A config file holding a credential MUST be gitignored.
- A config file holding a credential MUST NOT also hold committed team conventions, and vice versa.
- A skill reading a credential file MUST NOT print, quote, log, or commit its values.

## Design Guidance

Every file sits at a fixed path; the shape of the path follows what the file holds:

| Shape | Use when | Reference |
|----------|----------|-----------|
| Fixed path | a setup skill scaffolds the file, so its location is guaranteed | `$HARNESS_REPO_PATH/.crew/<FILE>` ([0002](../adr/0002-crew-is-agnostic.md)) |
| Fixed path, variant-suffixed | the same config exists once per variant, and one root still holds them all | `$HARNESS_REPO_PATH/.crew/CODE-<stack>.md` ([0002](../adr/0002-crew-is-agnostic.md)) |
| Fixed path, one section per plugin | per-developer settings and credentials for every plugin a harness uses | `$HARNESS_REPO_PATH/.harness.json.user` — top-level `harness`, `atl`, …, plus `credentials.<plugin>` |

A script reads its plugin's section straight from the file with the standard library's parser; a skill with no
script reads the resolver's output, which carries every section except `credentials`. Each reader has exactly one
path to a value.

A variant split belongs in the filename rather than a subfolder: the folder encodes the same fact while making
"shared by every variant" a position in a tree instead of a visible property of the name, and it tempts a reader
to treat the parent directory as a fallback.

Split by lifecycle, because the two halves have different readers and different homes:

| Content | Home | In git |
|---------|------|--------|
| Credentials | the `credentials.<plugin>` section of `.harness.json.user` | no |
| Per-developer connection facts, working-set repos and pull branches | the `<plugin>` section of `.harness.json.user` | no |
| Team conventions, field maps, item-type defaults | committed files or generated repo-level skills under `.github/skills/` | yes |

A skill that degrades when its config is absent states per field what it can still do — an unresolved field is
empty, not fatal — rather than refusing wholesale or inventing a discovery call the config exists to avoid.

## Exceptions

- The harness anchor: `resolve-harness` walks up from cwd to the nearest `.harness.json.user`, and that file's
  directory is the Harness Repo Path. It is the one search allowed to run above a root, because it is the lookup
  that defines the root; every other setting is then read at a fixed path under it.

## Violation signals

- A lookup that tries a second directory after the first misses.
- A variant file missing, and the unsuffixed file read in its place.
- Any search for a per-repo config file other than the harness anchor walk.
- An API token and a committed convention table in the same file.
- A credential value in resolver output, a log, or agent-visible stdout.
- A component calling a discovery API for a value its config file already carries.
