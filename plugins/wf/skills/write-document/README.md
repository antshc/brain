# Write document

Write or update specifications, high-level designs, Transfer of Information (TOI) documents, research reports, bottom lines and root-cause reports.

| Route | Result |
|---|---|
| `spec` | Specification |
| `hld` | High-level design |
| `toi` | TOI document |
| `research` | Full research report using the bottom-line procedure |
| `bottom-line` | Standalone finding, consequence and recommended action |
| `root-cause` | Root-cause report from confirmed evidence, printed inline |

Use `draft` for new content, `update` for existing content, or `normalize` to revise only behavioral requirements. Untyped requirements fragments use `write-document normalize`, applying the spec requirements rules.

Examples: `write-document spec`, `write-document hld update`, `write-document toi`, `write-document research`, `write-document bottom-line`, `write-document root-cause`.

[SKILL.md](SKILL.md) selects the route and directly discloses its resources. Playbooks own procedures; templates own output structure; local references own requirements and HLD update rules.

Callers retain discovery, decisions, decomposition, evidence dispatch, approvals, worktrees, integration and publication. This skill returns authored content, source conflicts and unresolved gaps. Report routes use supplied evidence without investigation or requirements normalization. Research reuses the loaded bottom-line playbook internally, without recursive skill calls. Root-cause rendering requires a confirmed hypothesis and never saves a report file.
