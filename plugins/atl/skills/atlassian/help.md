# Help

**Trigger:** invocation args start with `help`. `help` alone → print the block below verbatim, then stop. `help <request>` → name the tactic the Tactics table selects for `<request>`, its reference, and the `atl.py` command it would run; run nothing. Never preflight, call Atlassian, or edit files.

```text
/atlassian <request>                 pick a tactic, preflight once, run it
/atlassian help                      this help
/atlassian help <request>            which tactic and command <request> would use; runs nothing

TACTICS: chosen from the request
 Fetch work             Jira key/URL → work.md + attachments + comments sidecar
  /atlassian fetch PROJ-123
  /atlassian summarize https://<site>.atlassian.net/browse/PROJ-123
 Publish work           create or update a Jira item from Markdown
  /atlassian create a Story in PROJ from docs/story.md
  /atlassian update PROJ-123 description from docs/story.md
 Fetch page             Confluence ID/URL/tiny link → page.md + anchors + assets + comments
  /atlassian read https://<site>.atlassian.net/wiki/spaces/<space>/pages/<id>/<title>
 Publish page           publish Markdown to Confluence; edit a page without replies
  /atlassian publish docs/design.md to space <key>
  /atlassian update page <id> from docs/design.md
  /atlassian fix the wording in page <id> section <name>
 Address page comments  edit a page in place, reply to every open review thread
  /atlassian address page comments on <page id or URL>
 Install                set up ATL in this repo: plugin check, deps, preflight-atlassian, config, pub-* wrappers
  /atlassian install
 Map Markdown           Markdown ↔ ADF, ADF-only construct check; offline
  /atlassian convert docs/story.md to ADF
 Query or operate (twg) search, JQL/CQL, transitions, people, spaces, comments
  /atlassian find open bugs in PROJ assigned to me
  /atlassian move PROJ-123 to In Progress

CLI: python3 <skillDir>/scripts/atl.py <command> --help
 fetch-work      --issue-key K --config C --md-path P [--assets-dir D] [--attachments embedded|all] [--site S]
 publish-work    create   --project P --issue-type T --summary S (--markdown F | --adf F) [--parent K] [--fields-json F] [--attach F ...] --config C
                 update   --key K [--summary S] [--markdown F | --adf F] [--fields-json F] [--attach F ...] --config C
                 read-adf --key K --out F --config C
 fetch-page      --page-id ID --config C --md-path P [--assets-dir D] [--attachments auto|skip|required] [--comments auto|skip] [--site S]
 publish-page    run           --md-path P (--page-id ID | --space-id ID) [--title T] --config C [--assets-dir D] [--out F]
                 verify        --page-id ID --config C --expect-anchors N [--present F] [--absent F] [--verify-dir D]
                 check-anchors --original F --md-path F            offline
                 extract | render-attach | substitute-media | replace-markers | publish-adf | combine   step utilities
 map-markdown    md-to-adf | adf-to-md | detect-adf-only           stdin → stdout, offline

OTHER SCRIPTS
 python3 <skillDir>/scripts/comment_state.py --comments F [F ...] --html F --account-id ID --site S [--pretty]
 python3 <skillDir>/scripts/install_drawio.py [version] [--prefix D] [--bindir D]

ELSEWHERE
 /daily-briefing [period]             blocked items and @mentions (engineering skill)
```
