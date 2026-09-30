# Publish Page

All configuration lives in `.atlassian.json.user`, beside `/preflight-atlassian`'s `SKILL.md` — located and parsed by `/preflight-atlassian` skill, whose `configPath` is passed to `run` as `--config`; created by `/init-atl`. See `SKILL.md` for the full workflow this drives.

## Configuration

| Key | Required | Default | Purpose |
|---|---|---|---|
| `site` | Yes, for any REST call | none — missing keys fail fast, naming each one | Confluence site host, e.g. `example.atlassian.net` |
| `email` | Yes, for any REST call | none | Account email for basic auth |
| `apiToken` | Yes, for any REST call | none | API token for basic auth; never printed, logged, or published |
| `diagramRenderer` | No | `png` | Selects `png`, `drawio`, or `mermaid` as the diagram output; unknown values fail before any page is touched |
| `drawioExtensionKey` | Only with `diagramRenderer=drawio` | none — no usable default, the app id and environment id differ per site | Draw.io Forge extension key, format `<appId>/<envId>/static/drawio` |
| `swimlaneDrawio` | No | `true` (falsy only when set to `0`/`false`/`no`) | Opts a `swimlane-beta` diagram into the native Mermaid-to-draw.io converter instead of falling back to a static PNG |

