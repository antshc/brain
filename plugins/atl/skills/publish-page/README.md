# Publish Page

All configuration lives in a `.atlassian` file, found by walking up from the resolved repo root — see `SKILL.md` for the full workflow this drives.

## Configuration

| Key | Required | Default | Purpose |
|---|---|---|---|
| `ATLASSIAN_SITE` | Yes, for any REST call | none — missing keys fail fast, naming each one | Confluence site host, e.g. `example.atlassian.net` |
| `ATLASSIAN_EMAIL` | Yes, for any REST call | none | Account email for basic auth |
| `ATLASSIAN_API_TOKEN` | Yes, for any REST call | none | API token for basic auth; never printed, logged, or published |
| `ATLASSIAN_DIAGRAM_RENDERER` | No | `png` | Selects `png`, `drawio`, or `mermaid` as the diagram output; unknown values fail before any page is touched |
| `ATLASSIAN_DRAWIO_EXTENSION_KEY` | Only with `ATLASSIAN_DIAGRAM_RENDERER=drawio` | none — no usable default, the app id and environment id differ per site | Draw.io Forge extension key, format `<appId>/<envId>/static/drawio` |
| `ATLASSIAN_SWIMLANE_DRAWIO` | No | `true` (falsy only when set to `0`/`false`/`no`) | Opts a `swimlane-beta` diagram into the native Mermaid-to-draw.io converter instead of falling back to a static PNG |
