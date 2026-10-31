# atl is twg-first with REST-owned ADF content

`atl` needs one Atlassian access path that an agent session can always reach and that keeps `map-markdown-adf` the single Markdown/ADF boundary. Every Jira/Confluence search, lookup, and other operation runs through the `twg` CLI, credentialed from `.atlassian.json.user` (`email` + `apiToken`, the same credentials the REST scripts use); only the four content skills (`fetch-page`, `publish-page`, `fetch-work`, `publish-work`) move bodies themselves, as ADF over REST converted by `map-markdown-adf`, because twg's own Markdown/HTML conversion drops the special constructs (`<details>`, panels, status, TOC, wide tables, inline-comment anchors, diagrams, attachments). Applies only to the `atl` plugin.

## Considered Options

- **MCP-first with Python-owned conversion** (previous decision) — rejected: the Rovo MCP never returned real ADF for Jira descriptions, dropped Confluence annotation marks, could not upload attachments, was missing in subagent sessions, and forced every content skill to carry an MCP handback plus a REST fallback.
- **twg for everything, content included** — rejected: twg converts bodies itself (Markdown or HTML), so `map-markdown-adf` constructs and comment anchors would not round-trip.
- **REST for everything** — rejected: search, people, spaces, field metadata, and identity would each need bespoke scripts that twg already provides.
- **Separate twg login (OAuth) instead of the config token** — rejected: a second credential store and an interactive login an agent must not run; one `apiToken` serves both twg and REST.
- **`publish-diagram` as a separate skill** — rejected: splitting one document-publishing operation across two skills by rendering backend exposes an implementation detail as a naming decision.
- **Repository overrides as data files read by one skill** — rejected in favour of generated wrapper skills, which surface each item type in the agent's own skill list instead of hiding it in a table.

## Consequences

- `apiToken` is mandatory: no `atl` content skill reads or publishes without it, and twg uses it via `TWG_USER`/`TWG_TOKEN`/`TWG_SITE` injected by `preflight-atlassian`'s `scripts/twg.py`, which redacts the credentials from output.
- `plugins/atl/.mcp.json` is deleted; `publish-page` drops its MCP handback, `--threshold-bytes`, and `notify-comments`.
- twg commands request Markdown, never HTML.
- `publish-page` keeps `mmdc` and `atlassian-python-api>=4.0,<5` — pinned because 5.x removed `Confluence.attach_file()`.
