---
id: "0005"
title: atl is MCP-first with Python-owned conversion
trigger: >-
  merging or splitting the Atlassian plugins, adding an `atl` skill, choosing between the Atlassian MCP and a
  Python/REST backend for a Jira or Confluence operation, Markdown-to-ADF or ADF-to-Markdown conversion,
  `ATLASSIAN_API_TOKEN` or `.atlassian` handling, acli usage, Confluence attachment or mermaid-diagram upload,
  per-repository Jira field or Confluence space overrides, naming a Jira or Confluence access skill
summary: >-
  The Atlassian surface is one plugin, `atl`, built on the Rovo MCP for transport and Python for conversion:
  `map-markdown-adf` owns the only ADF implementation in both directions and every sibling skill invokes it as a
  skill rather than importing its code. A token is required only for what the MCP cannot do — Confluence
  attachment upload, and therefore `publish-page`'s mermaid branch — so all seven skills degrade to MCP-only when
  `.atlassian` is absent. Per-repository specialisation is expressed as `init-atl`-generated wrapper skills under
  `.github/skills/`, never as item-type skills shipped inside the plugin. acli, `markdown`, and `markdownify` are
  dropped.
default: >-
  Route a new Atlassian operation through the Rovo MCP and put any content conversion in `map-markdown-adf`;
  reach for `atlassian-python-api` and a token only when the MCP has no endpoint for the operation.
owns:
  - "Atlassian transport backend selection"
  - "Atlassian content conversion ownership"
  - "Atlassian per-repository override mechanism"
  - "atl skill roster"
applies_to:
  - plugins/atl/**
  - .atlassian
related: ["0008", "0009"]
---

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
