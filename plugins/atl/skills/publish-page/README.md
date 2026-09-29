# Publish Page

All configuration lives in `atl` + `credentials.atl` inside `.harness.json.user`, resolved via `/resolve-harness` — see `SKILL.md` for the full workflow this drives.

## Configuration

| Key | Section | Required | Default | Purpose |
|---|---|---|---|---|
| `site` | `atl` | Yes, for any REST call | none — missing keys fail fast, naming each one | Confluence site host, e.g. `example.atlassian.net` |
| `email` | `credentials.atl` | Yes, for any REST call | none | Account email for basic auth |
| `api_token` | `credentials.atl` | Yes, for any REST call | none | API token for basic auth; never printed, logged, or published |
| `diagram_renderer` | `atl` | No | `png` | Selects `png`, `drawio`, or `mermaid` as the diagram output; unknown values fail before any page is touched |
| `drawio_extension_key` | `atl` | Only with `diagram_renderer=drawio` | none — no usable default, the app id and environment id differ per site | Draw.io Forge extension key, format `<appId>/<envId>/static/drawio` |
| `swimlane_drawio` | `atl` | No | `true` (falsy only when set to `0`/`false`/`no`) | Opts a `swimlane-beta` diagram into the native Mermaid-to-draw.io converter instead of falling back to a static PNG |
