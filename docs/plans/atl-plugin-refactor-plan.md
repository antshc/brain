# Refactor the ATL plugin

**Status** — Proposed. Reviewed `antshc/brain` main. Scope is skill routing, Python consolidation, and caller migration.

## Findings

- `atl` currently spreads the operations being consolidated across eight skills. The four body scripts use REST and ADF. Three call the same Markdown mapper through relative subprocess paths, and the Jira fetch/publish scripts carry nearly identical credential and client code.
- `fix-confluence-comments` wraps page fetch/publish for edits without thread replies. `address-page-comments` is a separate targeted-edit and reply workflow. The page publisher independently checks inline-comment anchors and reports detachments.
- Removing the old skill names affects more than `atl`. The ATL installer generates per-repo `pub-<issue-type>` wrappers, the preflight template names old skills, and `wf` research and diagram skills invoke them.

## 1. Add the `atlassian` entry skill

Treat the repeated `publish-work` as one tactic. Include `fetch-page` and `map-markdown-adf` as tactics so all five CLI capabilities have an agent entry route.

Keep the body to routing, shared constraints, and these trigger-driven tactics. Load only the selected reference. Re-evaluate after each result when the next action changes, such as a search hit becoming a page read. Multiple operations can share one preflight result for the same site.

| Tactic | Trigger | Result |
|---|---|---|
| Brief daily | User asks for a Jira daily briefing, blockers, or unanswered mentions | Existing period, blocker and mention buckets, with incomplete results called out |
| Fetch work | Jira key/URL or selected Jira search result needs a full body | Markdown, attachments, and linked Jira comments sidecar or failure note |
| Publish work | User asks to create or update a Jira item from Markdown | Work-item key, URL, attachment outcomes, and conditional read-back |
| Fetch page | Confluence page ID/URL/tiny link or selected result needs a full body | Markdown with anchors, assets and comments according to the requested modes |
| Publish page | User asks to publish local Markdown to Confluence | Page URL, diagram/attachment and anchor outcomes, and read-back |
| Address page comments | User asks to address Confluence review threads or reply to them | Verified targeted edits when needed, thread replies or an orphaned-thread footer reply, and a report of pending threads |
| Map Markdown | Convert Markdown/ADF or detect ADF-only constructs | ADF JSON, Markdown, or a construct report. Runs offline |
| Query or operate with TWG | Discovery, metadata, people, links, transitions, or other non-body operations | Credentialed `twg` result, using the relevant product reference and live help as needed |

Proposed plugin layout:

```text
plugins/atl/
  plugin.json
  skills/
    atlassian/
      SKILL.md
      references/
        address-page-comments.md
        brief-daily.md
        fetch-page.md
        fetch-work.md
        map-markdown-adf.md
        publish-page.md
        publish-work.md
        twg.md
        twg/                 Existing command and product references
      scripts/
        atl.py               Five-command Python CLI
        atl_cli/             Commands, shared config/clients, converter
        brief_daily/         Existing blocker and mention helpers
        comment_state.py     Existing review-thread state helper
        install_drawio.py
  install/
    install.md
    requirements.txt
    assets/
      preflight-atlassian/
        preflight-atlassian.SKILL.template.md
        scripts/twg_cred.py
```

Keep `install/install.md` for setup and its generated `preflight-atlassian` as the shared credential resolver. Move the standalone `address-page-comments` workflow to `references/address-page-comments.md` and relocate `comment_state.py` under `atlassian/scripts/`. Preserve its pending-thread rerun gate, snapshot-token retry, annotation read-back before replies, and thread versus footer reply routing. The helper stays bundled with this tactic. The shared CLI keeps its five command groups.

Route explicit edits without thread replies through Fetch page and Publish page. Preserve inline anchors and the publisher's existing detached-comment notice behavior. Drop the standalone `fix-confluence-comments` workflow and its `shared_anchors.py` command. Before publishing a fetched edit, compare the original and edited anchors. Keep all spans for a shared ID or remove all when removing the highlighted text on purpose. Reuse the retired helper's fixture to cover this rule. Keep the publisher's existing warning behavior for ordinary direct publishes. Plain page-edit requests must never implicitly run the reply tactic.

Preserve the ADR boundary. Discovery, metadata, and Jira comment retrieval use the preflight-provided `twg` launcher. Full bodies use REST with ADF. Keep the existing per-caller lossy read fallbacks and warnings, and stop on auth or policy denial. Scope the existing TWG HTML exception to the Address page comments tactic's targeted edits.

## 2. Consolidate the Python CLI

Call `python3 <atlassian-skill-dir>/scripts/atl.py` from any working directory. Use one `argparse` entry point with internal modules. Keep the package in the owning skill so a marketplace install can run it directly. Avoid requiring a second package installation or a global command. Continue using the dependency installed by the ATL installer.

| CLI command | Current code to move | Contract to preserve |
|---|---|---|
| `fetch-work` | `assemble_work.py`, `fetch_attachments.py` and helpers | Jira REST v3 description, metadata header, assets, media sizing and ZIP behavior. Tactic still gets Jira comments through TWG and links the unchanged sidecar |
| `publish-work create\|update\|read-adf` | `publish_work.py` and helpers | Explicit create/update, caller-supplied fields and parent, per-file attachment outcomes, read-only ADF verification. Accept Markdown for create/update and preserve the existing `--adf` input for migrated low-level callers |
| `fetch-page` | `assemble_page.py`, `comments.py`, `fetch_diagrams.py` and helpers | Confluence REST v2 ADF, page title, attachment/comment modes, inline anchors and diagram round-tripping |
| `publish-page run\|verify` | `publish_page_diagrams.py`, `page_diagrams/`, `verify_publish.py` | Create/update and title rules, render/upload pipeline, comment guard, JSON outcome and read-only verification. Keep existing utility subcommands under `publish-page`, including its legacy marker alias |
| `map-markdown md-to-adf\|adf-to-md\|detect-adf-only` | `map_markdown_adf.py` and `converter/` | Same stdin/stdout formats and exit behavior. No config, network, or Atlassian dependency needed for offline conversion |

- Move existing behavior first. Switch converter subprocesses and page verification to direct calls inside the package. Share config parsing, site normalization, library version checks and client construction where equivalent. Preserve product-specific URL handling and per-command diagnostics, exit codes, JSON fields and artifact paths.
- Keep URL/tiny-link resolution, project/space choice, field discovery, and report composition in tactics. Keep daily briefing on TWG with its existing Python post-processors. Keep the Draw.io installer beside the publisher as a setup utility.
- Carry the created Jira key or Confluence page ID through any failure after creation. Retry attachments or resume by ID, and report uncertain remote state before any create retry. Keep Confluence guard warnings and verification output visible and retain working artifacts when verification fails.

## 3. Migrate callers before removing old skills

1. Add the CLI and port the existing offline fixtures and command tests. Compare old and new outputs before changing callers.
2. Add the entry skill and move the former workflow prose into references. Replace nested skill calls with explicit tactic handoffs. Move the TWG reference tree and update relative links and body-routing examples. Move the comment-state helper and retarget its unit tests and the `tests/atl/address-page-comments/regression/` harness. Reuse preflight within a request for the same site when the required facts are present.
3. Update `install/install.md`, its bundled preflight asset and the checked-in `.github/skills/preflight-atlassian/SKILL.md`. Generate new Jira wrappers that call the **Publish work** tactic. Document how to update existing wrappers while preserving their required fields and local edits. Refresh generated preflight instructions through the ATL installer without changing `.atlassian.json.user`.
4. Update `wf/research/why` Atlassian source and coordinator handoff plus the `doc-diagram` skill’s architecture, behavior, and code tactics. Keep their Rovo/JQL/CQL fallbacks and publish intent. Update README, architecture, glossary, current ADR terminology, active how-to links and regression prompts. Search active paths for more invocations, script paths and CLI entry points before cutover.
5. Remove the absorbed skill directories, including `address-page-comments`, and `fix-confluence-comments` in the same release as the in-repo caller changes. Update test imports, subprocess targets, and any CI path filters. Document the new Address page comments route alongside migration for old slash commands and external wrappers.

## Acceptance

- Discovery exposes `atlassian`. Setup runs through the explicit ATL installer. Every former task routes to the expected tactic or setup workflow. Search-to-fetch uses the full body path and read-only intents issue no mutations.
- `python3 -m pytest tests/atl` passes. Smoke the new CLI from an unrelated working directory, including `--help` and offline conversion without credentials or Atlassian dependencies.
- Re-run existing Jira create/update, field and attachment cases. Verify comments sidecar success/failure, partial attachment reporting, and read-only ADF verification. Cover post-create failures without duplicate creates.
- Re-run the Confluence round-trip suite for ADF-only constructs, media dimensions, attachments, PNG/Draw.io sidecars, shared anchors, intended detachment, and phrase verification. Through `atlassian`, exercise targeted edits and replies for anchored and orphaned comments, repeat runs, stale snapshots, and ordinary page edits without thread replies. Run live suites only with a designated test project/space.
- Exercise briefing defaults, missing identity, fallback query, pagination and partial-comment reporting. Verify a generated Jira wrapper and one research and diagram handoff use the new routing. Check active docs and tests for broken references.

## Sources

- [ATL plugin](https://github.com/antshc/brain/tree/main/plugins/atl) and [transport ADR](https://github.com/antshc/brain/blob/main/docs/adr/atl-is-twg-first-with-rest-adf-content.md)
- [Skill-owned code convention](https://github.com/antshc/brain/blob/main/docs/concepts/structure-skill-owned-code.md) and [ATL regression suite](https://github.com/antshc/brain/tree/main/tests/atl)
