# Help

**Trigger:** invocation args start with `help`. `help` alone → print the block below verbatim, then stop. `help <request>` → name the tactic the Tactics table selects for `<request>`, its reference, and the `<atl>` (`atl.py`) command it would run; run nothing. Never preflight, call Atlassian, or edit files.

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
 Copy page              clone one page into another; required attachments; automatic verification
  /atlassian copy page <source> to page <target>
 Rename page            title-only update with safe snapshot and read-back
  /atlassian rename page <id> to <title>
 Address page comments  edit a page in place, reply to every open review thread
  /atlassian address page comments on <page id or URL>
 Install                set up Atlassian in this repo: skill check, deps, preflight-atlassian, config, pub-* wrappers
  /atlassian install
 Doctor                 inspect Python packages, interpreter, and required CLIs
  /atlassian doctor
 Map Markdown           Markdown ↔ ADF, ADF-only construct check; offline
  /atlassian convert docs/story.md to ADF
 Query or operate (twg) search, JQL/CQL, transitions, people, spaces, comments
  /atlassian find open bugs in PROJ assigned to me
  /atlassian move PROJ-123 to In Progress

CLI: <atl> = python3 <skillDir>/scripts/atl.py --config C   (Preflight; single entry point)
 <atl> <any twg command>   runs on twg with config credentials, output redacted; --native = raw twg
 Markdown bodies (default format) route to the commands below:
  confluence content get <ref> --output-file P                         → fetch-page
  confluence content create --content-type page --body-file F ...     → publish-page run
  confluence content update <ref> --body-file F [--title T]           → publish-page run
  jira workitem get <KEY|URL> --output-file P                          → fetch-work
  jira workitem create|update --description-file F [--attach F ...]   → publish-work
 <atl> <command> --help; --config is appended to these:
 fetch-work      --issue-key K --md-path P [--assets-dir D] [--attachments embedded|all] [--site S]
 publish-work    create   --project P --issue-type T --summary S (--markdown F | --adf F) [--parent K] [--fields-json F] [--attach F ...]
                 update   --key K [--summary S] [--markdown F | --adf F] [--fields-json F] [--attach F ...]
                 read-adf --key K --out F
 fetch-page      <ID|URL> --md-path P [--assets-dir D] [--attachments auto|skip|required] [--comments auto|skip] [--site S]
                 --page-id ID is the equivalent legacy flag
 publish-page    run           --md-path P (--page-id ID | --space-id ID) [--title T] [--assets-dir D] [--out F] [--verify]
                 verify        --page-id ID --expect-anchors N [--present F] [--absent F] [--verify-dir D]
                 check-anchors --original F --md-path F            offline
                 extract | render-attach | substitute-media | replace-markers | publish-adf | combine   step utilities
 copy-page       <source> --to-page <target> [--title T] [--work-dir D]
 rename-page     <page> --title T --yes
 doctor
 map-markdown    md-to-adf | adf-to-md | detect-adf-only           stdin → stdout, offline

OTHER SCRIPTS
 python3 <skillDir>/scripts/comment_state.py --comments F [F ...] --html F --account-id ID --site S [--pretty]
 python3 <skillDir>/scripts/install_drawio.py [version] [--prefix D] [--bindir D]

ELSEWHERE
 /daily-briefing [period]             blocked items and @mentions (engineering skill)
```

Conversion validation: [guard policy](references/conversion-guards.md). `publish-page verify --expected-manifest <manifestPath>` adds raw-ADF fidelity checks.
