---
name: write
description: >-
  Tighten, write or edit prose, work items and documents. Guides, steps, PR text, messages; user stories, implementation tasks, bug reports; specs, HLDs, TOIs, research, bottom-line and root-cause reports, docs pages; sharpen or rephrase prompts. Use for 'unslop this', 'tighten this prose', 'write a user story', 'write a bug report', 'write the spec', 'sharpen this prompt'. Not for code or tests; design decisions → `design`; ADRs → `architecture-records`; skills → `skill-author`.
argument-hint: "tighten · guide|steps|findings|github|message · sharpen|rephrase · story|task|bug · spec|hld|toi|research|bottom-line|root-cause|doc [draft|update|normalize]"
---

# Write

Router for three route families: prose, work items and documents. Select one route, read each resource it lists fully (no previews), then execute it. Load nothing the route does not list. Resolve paths from this skill's base directory.

## Top rules

- **Cut words that add no information.**
- **Prefer everyday words.** Use a longer word when it is more precise.
- **When a rule makes a sentence worse, fix the sentence another way or leave it alone.** A sentence that follows every rule and sounds machine-written has failed.
- **The codebase is the word list.** Write the real symbol, file, flag, or command name, not a synonym or a description.
- **Describe the operation in plain language.** Define named patterns on first use.
- **Protected text.** Keep code, commands, citations, identifiers, quotations, captured output, and caller-required structure, subjects, and markers exactly as supplied.

## Prose routes

| Route | Text kind | Read, in order | Output |
|---|---|---|---|
| `guide` | README, RFC, guide, explanation, spec or HLD prose | [modes-diataxis.md](references/modes-diataxis.md) (whole documents only), [sentences-google.md](references/sentences-google.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [rhythm.md](references/rhythm.md), [tighten.md](references/tighten.md) | Pipeline |
| `steps` | Instructions, procedures, runbooks, reproduction steps, troubleshooting actions | [sentences-google.md](references/sentences-google.md), [steps-ste.md](references/steps-ste.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [tighten.md](references/tighten.md) | Pipeline |
| `github` | PR title and body, commit message body, review finding or reply | [github-text.md](references/github-text.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [tighten.md](references/tighten.md) | Pipeline; caller format wins |
| `findings` | Existing review, blast-radius, investigation, or status report text | [ambiguity-global-english.md](references/ambiguity-global-english.md), [rhythm.md](references/rhythm.md), [tighten.md](references/tighten.md) | Pipeline; keep findings, proof status, and risk judgments |
| `message` | Chat, Slack, Teams, email, Jira or issue comment | [messages.md](references/messages.md), [ambiguity-global-english.md](references/ambiguity-global-english.md), [tighten.md](references/tighten.md) | Pipeline |
| `tighten` | Any text; make it shorter, more concise, or free of AI tells | [tighten.md](references/tighten.md) | Pipeline; same facts and structure, word counts before and after |
| `sharpen` | Task prompt to deepen | [sharpen.md](references/sharpen.md) | The four answers, then the rewritten prompt |
| `rephrase` | Task prompt to restate in your own words | [rephrase.md](references/rephrase.md) | The restated goals and problem |

Prose routes own wording only. Preserve the owner's structure, evidence, and confidence.

## Artifact routes

Every work item and document route first reads [artifacts.md](references/artifacts.md), then its playbook, then its Artifact resources.

| Family | Route | Select for | Playbook | Output |
|---|---|---|---|---|
| Work item | `story` | One atomic user story | [Story](playbooks/story.md) | Title and story body |
| Work item | `task` | One implementation work item with supplied scope | [Task](playbooks/task.md) | Complete task body |
| Work item | `bug` | One defect report from observed behavior | [Bug](playbooks/bug.md) | Reproduction, actual and expected results |
| Document | `spec` | A specification or PRD from supplied requirements and decisions | [Spec](playbooks/spec.md) | Specification body |
| Document | `hld` | A high-level design from supplied evidence and resolved decisions | [HLD](playbooks/hld.md) | New or incrementally updated HLD |
| Document | `toi` | A developed feature's technical Transfer of Information (TOI) | [TOI](playbooks/toi.md) | TOI document |
| Document | `research` | A full research report from supplied findings and evidence | [Research](playbooks/research.md) | Research report with a bottom line |
| Document | `bottom-line` | A standalone conclusion, key finding or recommended action | [Bottom line](playbooks/bottom-line.md) | One decision-oriented bullet per subject |
| Document | `root-cause` | A root-cause report from a supplied diagnosis log and confirmed evidence | [Root cause](playbooks/root-cause.md) | Root-cause report printed inline |
| Document | `doc` | A standalone README, tutorial, how-to, runbook, reference page or explanation; requests to structure such a page | [Doc](playbooks/doc.md) | Markdown page with applicable sections |

Operations: `draft` (new), `update` (existing) or `normalize` (requirements wording only); see Execution in artifacts.md.

**Doc mode policy.** Specialized artifact routes take precedence over `doc`. Within `doc`, honor an explicit mode (`tutorial`, `how-to`, `reference`, `explanation`); otherwise infer from the reader's goal. Unknown explicit mode → report it and list the four modes. Ask only when missing purpose or audience changes the structure. A README is an entry page within its selected mode, not another route. Continue the active mode on replies; split substantial mixed purposes into linked pages only within caller scope.

## Selection

Pick the first rule that matches:

1. **Explicit route.** The user or caller names a valid route (`/write story`, `/write hld update`) → use it. `unslop` is an alias of `tighten`. Unknown route → report it and list the routes by family. `/write normalize` without a route → `spec normalize`.
2. **Active route.** A reply continues the active route unless redirected. An artifact route stays active while it applies a prose route internally.
3. **Prompt work.** Deepen, sharpen, or rewrite a prompt → `sharpen`. Restate, rephrase, or say in your own words → `rephrase`. Both → `rephrase`, then `sharpen`.
4. **Tighten only.** Tighten, shorten, cut down, make concise, unslop or remove AI tells with no other ask → `tighten`.
5. **Redirect.** Request kind in Redirects → invoke that skill.
6. **Named artifact.** The request names a work item or document → its artifact route. Tie-breaks: "report" with findings or evidence to render → `research`; existing report text to refine → `findings`; "task prompt" → `sharpen`; "task" or work item → `task`; page structure, template or sections → `doc`; prose inside an existing page → `guide`, or `steps` for procedures.
7. **Text kind.** Match the text kind to the Prose routes table.
8. **Unclear.** Ambiguous artifact type → ask and wait. Supplied text of unclear kind → `tighten`; state the assumed kind in the hand-back.

Combined requests → author artifacts in dependency order, then request order for independent artifacts; complete each route before selecting the next.

## Redirects

| Request kind | Action |
|---|---|
| Code or tests | Out of scope; report it and return. |
| Design decisions, task breakdown or approval | *Load and follow the `design` skill to resolve design decisions or break work into tasks; select the applicable route.* |
| New investigation | *Load and follow the `research` skill to investigate the question and return cited findings; select the applicable route.* |
| New diagnosis | *Load and follow the `diagnosing-bugs` skill to reproduce and isolate the failure's root cause.* |
| ADR, Concept, or glossary term | *Load and follow the `architecture-records` skill to record the architecture decision, Concept, or term; select the applicable route.* |
| `SKILL.md`, agent, or instructions file | *Load and follow the `skill-author` skill to apply authoring rules to the agent-facing document, using route `guidance`.* |
| Product UI strings | Report that the product's copy guidelines own them. |

## Internal hand-offs

An artifact route that needs prose refinement applies a prose route in this session: `guide` for page prose and whole-document mode rules, `steps` for procedural blocks including troubleshooting actions.

**Tighten pass.** Every artifact `draft` or `update` **MUST** apply `tighten` to its authored prose before returning; `normalize` skips it. Text already refined by `guide` or `steps` has had this pass. Keep the document formatting and verbatim sources, evidence, citations and code unchanged.

For any hand-off, read that prose route's references, then run Pipeline on the targeted text only. Keep the artifact template, selected mode and protected text. **MUST NOT** reload this skill or redirect back; the artifact route stays active and owns the output.

## Artifact resources

Load each resource when its trigger applies; `normalize` loads only the requirements resources.

| Trigger | Resource |
|---|---|
| `story`, `task`, `bug`, `spec`, `hld`, `toi` with requirements wording, including `normalize` | [Requirements](references/requirements.md), [Requirements terms](references/requirements-terms.md) |
| `story` draft/update | [Story template](templates/story-template.md) |
| `task` draft/update | [Task template](templates/task-template.md) |
| `bug` draft/update | [Bug template](templates/bug-template.md) |
| `spec` draft/update | [Spec template](templates/spec-template.md) |
| `hld` draft/update, including evolving drafts | [HLD template](templates/hld-template.md), [Decision bullets](references/decision-bullet.md), [HLD updates](references/hld-updates.md) |
| `toi` draft/update | [TOI template](templates/toi-template.md) |
| `research` draft/update | [Research template](templates/research-template.md), [Bottom line procedure](playbooks/bottom-line.md), [Bottom line template](templates/bottom-line-template.md), [Report language](references/report-language.md) |
| `bottom-line` draft/update | [Bottom line template](templates/bottom-line-template.md), [Report language](references/report-language.md) |
| `root-cause` draft/update | [Root-cause template](templates/root-cause-template.md) |
| `doc` draft/update | [Doc template](templates/doc-template.md) |

**Contracts producer.** Changed contracts in `story`, `task`, `spec`, `hld` or `toi` → *Load and follow the `doc-contracts` skill to write an API, database, resource, or GUI contract delta* using the route's listed kinds and inputs. Missing contract facts return as gaps; never hand-write a delta.

**Diagrams.** Required diagrams in an artifact route → *Load and follow the `doc-diagram` skill to create Mermaid architecture or behavior diagrams* using the selected route's view and source facts. Missing decisions or evidence return as gaps.

**Confluence formatting.** When Confluence is the target, *Load and follow the `atlassian` skill to determine supported Markdown code-fence languages, using the Map Markdown tactic.* Use supported tags. For an unsupported language, use a `text` fence and name the original language in the preceding prose. Preserve the code content exactly. Keep `mermaid` diagram fences for the Publish page pipeline; offline Map Markdown does not handle diagrams or attachments. Other destinations keep their existing language tags.

## Pipeline

Prose routes and internal hand-offs run this pipeline.

1. **Write or edit.** No text supplied → write it with the route's references. Text supplied → edit it with the same references. *Done when* every listed reference has been applied.
2. **Tighten last.** Apply `tighten.md` last. Preserve meaning, tone, confidence, and protected text. *Done when* a read against the input shows no change to facts, scope, or confidence.
3. **Hand back.** Return the text. For an edit, list each fix with the heading of the reference rule it applies. Nothing to fix → return "No changes."

Artifact routes return per Output contract in artifacts.md.
