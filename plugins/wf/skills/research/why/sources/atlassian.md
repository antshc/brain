# Atlassian: Jira Work Items and Confluence Designs

Use this playbook in **two separate investigators**: Jira owns the issue / ticket tracker category; Confluence owns long-form documents. Search both products independently, even if one already contains an answer. Return source-specific evidence to the synthesizer.

## Access and scope (both investigators)

1. Use the `preflight-atlassian` skill's **Resolve** result passed by the coordinator: `site`, `tokenAvailable`, and the credentialed `twg` launcher. The coordinator resolves it once for both investigators. Use that launcher for every `twg` command, not bare `twg`.
2. Missing skill, site, token, or launcher → report the specific evidence gap and stop this source. Do not inspect `.atlassian.json.user`, print credentials, use another identity, or run login/setup.
3. Follow the installed `twg` skill and the product-specific references. Live help owns unfamiliar command syntax. Use the supplied site's scope; preserve a different site explicitly identified by an anchor URL.
4. Search using the code anchor's ticket IDs, PR references, feature names, symbols, and business terms. Try several distinct phrasings, record exact queries and scope, and bound results. Search hits are candidates, not proof.

## Jira investigator — work items and decisions

1. **Known tickets first.** Read linked Jira keys/URLs via `fetch-work` for the full description when that skill is available; otherwise use the credentialed `twg jira workitem get <KEY> --full`, noting possible body conversion loss. Use `twg jira workitem get <KEY> --full` for comments, links, and fields in either case. Check parents, related work items, and changelogs when they explain scope or a decision. Use `twg context` for cross-product relationships when relevant.
2. **Rovo discovery.** Run `<twg> rovo search "<feature or design decision>" --app jira --limit 10` with varied terms. Identify Jira candidates relevant to the code's time window and question.
3. **JQL fallback.** If Rovo is unavailable, returns no relevant work items, or leaves a material search gap, use the `twg` Jira querying route: `<twg> jira workitem search "<terms>" --limit 10` (JQL-backed), or `<twg> jira workitem query --jql '<JQL>'` for known project, time, label, or other exact constraints. Stop on authorization or policy denial; never treat a Rovo failure as evidence that Jira has no records.
4. **Hydrate.** Fetch selected work items' complete descriptions and comments; inspect changes, parent/child relationships, and linked PRs/designs when relevant. Record Confluence links under Additional Leads for the Confluence investigator; do not read Confluence in this category.
5. **Return.** Cite ticket key and URL, exact statement and comment location, author/date, decision, any conflicting revisions, and queries with null results.

## Confluence investigator — feature designs and ADRs

1. **Known designs first.** Read supplied Confluence page URLs/IDs and design links in the code anchor with `fetch-page` (full Markdown, attachments, and comments). Use the `twg` Confluence read fallback only when `fetch-page` is unavailable or fails, noting possible conversion loss.
2. **Rovo discovery.** Run `<twg> rovo search "<feature or design decision>" --limit 10` with varied terms; keep Confluence results about designs, architecture, ADRs, HLDs, tradeoffs, and revisions. Scope with product filters only if supported by live `twg` help.
3. **CQL fallback.** If Rovo is unavailable, finds no relevant designs, or leaves a material search gap, use `<twg> confluence search query --cql '<CQL>'` with known title, space, label, or modification-time constraints. Use `<twg> confluence search text "<terms>"` for wider text discovery when the title is unknown. Stop on authorization or policy denial. A search snippet is not a substitute for the page body.
4. **Hydrate.** Read the full selected pages with `fetch-page`; inspect comments and revisions when they affect the rationale. Record linked Jira keys under Additional Leads for the Jira investigator; do not read Jira in this category.
5. **Return.** Cite page URL/title, section or comment, author/date, stated motivation and alternatives, later changes, and queries with null results.

## Cross-product handoff and evidence rules

- After both initial searches, each investigator reads only the relevant cross-links handed off from the other category by the coordinator. Preserve separate Jira and Confluence evidence lists, without duplicate findings.
- Check dates against the code anchor; an old proposal may have been superseded by a later ticket or design. Quote explicit intent; label inference and contradictions separately.
- Missing credentials, access denial, Rovo error, empty JQL/CQL, and result truncation are distinct gaps. Never claim a comprehensive search when a source was unavailable.
- Do not create or update Jira work items, Confluence pages, tokens, or local configuration.
