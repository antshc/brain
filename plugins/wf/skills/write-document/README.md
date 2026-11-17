# Write document

Write or update specifications, high-level designs, Transfer of Information (TOI) documents, research reports, bottom lines, root-cause reports and standalone Markdown documentation.

| Route | Result |
|---|---|
| `spec` | Specification |
| `hld` | High-level design |
| `toi` | TOI document |
| `research` | Full research report using the bottom-line procedure |
| `bottom-line` | Standalone finding, consequence and recommended action |
| `root-cause` | Root-cause report from confirmed evidence, printed inline |
| `documentation` | README, tutorial, how-to, runbook, reference page or explanation |

Use `draft` for new content, `update` for existing content, or `normalize` to revise only behavioral requirements. Untyped requirements fragments use `write-document normalize`, applying the spec requirements rules.

Examples: `write-document spec`, `write-document hld update`, `write-document toi`, `write-document research`, `write-document bottom-line`, `write-document root-cause`.

## General documentation

Use `write-document documentation how-to: add a research route`, `write-document documentation reference: configuration options`, or `write-document documentation update: docs/getting-started.md`. Modes are task context, not additional routes. Explicit modes win; otherwise the reader's goal determines tutorial, how-to, reference or explanation. Existing specialized artifacts retain their routes and templates.

The [Documentation template](templates/documentation-template.md) selects one mode block. Tutorials contain a learning result and walkthrough with checkpoints; how-tos contain task actions; reference pages contain organized facts; explanations answer a why question. README entry pages provide purpose and links to getting started and detailed docs within the chosen mode.

| Section | Required or optional |
|---|---|
| Title and opening | Required for a standalone page; fragments preserve their owner's format |
| Main content | Required; one selected mode |
| Verification | Required content for tutorial/how-to; separate heading optional when checks appear in steps |
| Audience | Optional when required expertise is unclear |
| Table of contents | Optional for long pages needing an inline TOC; GitHub supplies an outline |
| Prerequisites | Optional when actual dependencies exist |
| Examples | Optional when they clarify use or facts |
| Limitations | Optional when verified boundaries affect use |
| Troubleshooting | Optional when supported failure cases exist |
| Related documentation | Optional when useful links exist |

Troubleshooting follows the main content and verification, before related documentation. Each case uses a recognizable symptom or exact error, diagnostic checks, a conditional resolution and a success check. Causes and fixes need evidence; optional sections never justify invented content. Extensive cases can move to a linked page within caller scope. TOI keeps its existing mandatory Troubleshooting section.

The document writer owns structure. It invokes `write guide` for whole-page prose and `write how-to` for procedural blocks, including troubleshooting actions. Those routes own writing rules: clear sentences and headings, stable terminology, concise commands, conditions before actions and a final unslop pass. Direct prose requests remain available through `write`; callbacks for refinement never redirect to the document writer again.

## Ownership

[SKILL.md](SKILL.md) selects the route and directly discloses its resources. Playbooks own procedures; templates own output structure; local references own requirements and HLD update rules.

Callers retain discovery, decisions, decomposition, evidence dispatch, approvals, worktrees, integration and publication. This skill returns authored content, source conflicts and unresolved gaps. Report routes use supplied evidence without investigation or requirements normalization. Research reuses the loaded bottom-line playbook internally, without recursive skill calls. Root-cause rendering requires a confirmed hypothesis and never saves a report file.
