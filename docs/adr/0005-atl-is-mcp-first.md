# atl is MCP-first with Python-owned conversion

`atl` and `atlm` were two plugins over one vendor, and the split produced three copies of the ADF converter, two
auth stacks (acli env vars versus MCP OAuth), and two setup flows a user had to know the difference between. They
are merged into a single `atl` whose backend rule is a boundary rather than a preference: the MCP moves bytes,
Python shapes them, and the API token exists only to reach the one thing the MCP cannot do.

## Considered Options

- **Keep `atl` on acli and `atlm` on the MCP** (status quo) — rejected: two auth stacks over one vendor forced
  every caller to know which half of Atlassian it was talking to, and `acli` is an extra binary plus `~/.profile`
  and `HKEY_CURRENT_USER` mutation that the MCP's OAuth makes unnecessary.
- **Python/REST for everything, token mandatory** — rejected: it makes `.atlassian` and a personal API token a
  precondition for reading a page, when the MCP already authenticates without either.
- **MCP for everything, drop mermaid rendering** — rejected: it would delete working, tested diagram publishing
  to buy a dependency reduction the token-gated branch already achieves.
- **`publish-diagram` as a separate skill** — rejected: splitting one document-publishing operation across two
  skills by rendering backend exposes an implementation detail as a naming decision.
- **Repository overrides as data files read by one skill** — rejected in favour of generated wrapper skills, which
  surface each item type in the agent's own skill list instead of hiding it in a table.
- **Item-type skills shipped in the plugin** (status quo `create-jira-bug`, which hardcoded one project's
  mandatory Bug fields) — rejected: a file living in the plugin is shared by every repo that installs it, which is
  the opposite of a per-repository override.

## Consequences

- `plugins/atlm/` and `plugins/wf/skills/pub-zdesign/` are deleted; `marketplace.json` drops the `atlm` entry.
- `publish-page` carries two backends, so a repo that publishes mermaid needs Node's `mmdc` on PATH and
  `atlassian-python-api>=4.0,<5` — pinned because 5.x removed `Confluence.attach_file()`.
- With `cloudId` frequently unresolved under soft mode, the standing prohibition on
  `getAccessibleAtlassianResources` becomes a cache rule: it is forbidden only once `cloudId` is known.
