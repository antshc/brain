# Skill bootstrap template

Used in workflow step 8 only when no existing skill's `manifest.json` already covers the derived/overridden prefix(es).

**`.github/skills/search-nuget-<slug>/SKILL.md`**:
```markdown
---
name: search-nuget-<slug>
description: <prefix> (matches `<prefix>.*`) local decompiled-source lookup — answers questions about the real implementation of packages whose id starts with <prefix> (currently: <Id>) from this skill's own `references/<Id>.<version>.md` decompiled source (no live GitHub routing — source repository is provenance only, tracked per-package in manifest.json). Trigger automatically whenever the source, implementation, API, or behaviour of a package matching `<prefix>.*` needs inspecting. Generated and maintained by `.github/skills/ingest-nuget-package` — never hand-edited directly; `manifest.json` tracks which packages/versions/prefixes are covered.
---

Answer strictly from the local decompiled source in this skill's own `references/<PackageId>.<version>.md` — never a live GitHub lookup. List `references/` to see which package(s)/version(s) are available, then read the matching `.md` file for the requested package (and version, if specified; otherwise the only/most relevant one present).

## Covered packages

| Package | Versions | References |
|---|---|---|
| <Id> | <version> | `references/<Id>.<version>.md` |
```

**`.github/skills/search-nuget-<slug>/manifest.json`**:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "Packages decompiled/documented by ingest-nuget-package that match the <prefix> package-id prefix(es). codebases[].patterns (including the <prefix>.* wildcard) discover which package references belong here; packages[].versions is every distinct ingested version; each package's own repository field is provenance only and plays no part in grouping.",
  "prefixes": ["<prefix>"],
  "codebases": [
    { "name": "<slug>", "path": "<repository path supplied this run>", "patterns": ["<Id>", "<prefix>.*"] }
  ],
  "packages": [
    { "id": "<Id>", "versions": ["<version>"], "skip": false, "repository": "<owner/repo or null>" }
  ]
}
```
