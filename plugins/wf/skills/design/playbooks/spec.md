<!-- Prompt XML and literal placeholders are intentional. -->
<!-- markdownlint-disable MD033 -->

# Spec

Synthesize the conversation and codebase context into a spec (PRD). Ask only for missing publication inputs.

An **Initiative** is a coordinated product change tracked as one planning effort and may encompass multiple Capabilities and Features. A **Requirements** is a set of one Stakeholder requirement together with its Functional requirements, Business rules, Edge cases. A **Spec** packages one or more Requirements sets for planning and handoff.

Load [Spec publication](../references/github.md#spec-publication) for GitHub repository resolution, labels, duplicate prevention, and publication.

Explicit offline publishing or a reported GitHub/tool/authentication failure → save the spec to `docs/specs/{{initiativeIdSlug}}.md` as Markdown, following [Offline spec publishing](../references/github.md#offline-spec-publishing). Local output is not a published GitHub issue.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any Concepts and ADRs in the area you're touching.

2. Prepare the authoring context: requirements, resolved decisions, source context and accepted design package when present.

   Ask the user: *"What is the target branch and Initiative ID? (e.g. `release/1.1.10`, `PROJ-1234`)"* if not provided as arguments to this skill.

   Resolve `{{repository}}` (`owner/name`): a `workspace/` folder holding exactly one checkout → that checkout's own `origin` remote. More than one checkout → ask which. No `workspace/` folder → the current repository's `origin` remote. Never ask for it when exactly one candidate exists.

3. Design sketch — apply only when `design architect` or `design sketch` produced a completed, accepted `synthesis/` package in this conversation; otherwise skip and omit the **Design sketch** decision. Follow **Design sketch handoff** below.

4. *Load and follow the `write-document` skill to write and update specifications* using `spec` draft or update. Pass current source context, requirements, decisions, accepted rationale and prepared sketch manifest; receive the title, checked body and gaps. Return missing decisions/evidence to their owner before publication. Before publishing, check the entire rendered topic body: **no skill references** — no skill names, skill paths, invocation instructions, or template directives, including in inlined contract output. **Contracts Delta present ⇔ authoring identified touched contract kinds**; each kind's block has a `Legend:` line, `#### header` + `<details>` per resource or surface, and delta lines prefixed `+`, `-`, `%`, or `~`. Missing or hand-written → return to Write document's `spec` route for correction; do not publish. Only the **Design sketch** `{{artifactUrl}}` placeholders may remain; attaching fills them. Skills guide authoring internally; publish only their substantive decisions and content. Derive `{{specTitle}}` as a short title naming the Spec's outcome. Present the title, labels and checked body per Work item approval; end the turn awaiting explicit approval, and re-present after any change. After approval, follow [Publish spec](../references/github.md#publish-spec) with the checked body (no Initiative, branch, or repository metadata — publication adds them as title prefix and labels), `{{initiativeId}}`, `{{specTitle}}`, `{{targetBranch}}`, and `{{repository}}` — no additional triage.

5. Completed design package → after the issue is verified, follow [Attach design artifacts](../references/github.md#attach-design-artifacts) with the issue number and bundle manifest. Offline → follow its offline branch instead.

## Design sketch handoff

Classify the run's outputs by role, never by file name. Both `design architect` and standalone `design sketch` use `<repo-root>/tmp/design-<slug>/synthesis/` with `rationale.md`, `module-map.md`, and `sketch/`. Architect additionally has grounding and local or Arena candidate packages.

- **Selected design** — `synthesis/`: its `rationale.md`, `module-map.md`, and `sketch/` are the final package. For Architect, the synthesis decision names the local or Arena base candidate. Correction re-runs: the `arena-r<k>/synthesis/` the user picked.
- **Excluded** — every local or Arena candidate package (including the base candidate), `synthesis-note.md`, task statement, rubric, grounding notes, run scratch. Never attach or quote them.

Wrap only the selected `synthesis/` sketch and its module map into artifacts. Resolve the script path from the installed `design/` skill directory:

```text
python3 "<installed design directory>/scripts/bundle_artifacts.py" --sketch <synthesis/sketch path> --module-map <synthesis/module-map.md path> --out-dir <new empty temp dir outside the repository>
```

Exit 2 → report stderr and stop before publishing; never drop a sketch file to make it pass. The printed manifest lists each artifact's `name`, `type`, and `file`; the first is the **Sketch index** mapping each file to its artifact names. Pass the manifest to Write document's `spec` route for the binding Design sketch decision; publication fills its `{{artifactUrl}}` placeholders.
