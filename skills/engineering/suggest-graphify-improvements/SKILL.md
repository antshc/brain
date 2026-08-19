---
name: suggest-graphify-improvements
description: "Audit an existing Graphify knowledge graph in any project and generate evidence-backed suggestions to improve its corpus, extraction, retrieval, paths, skill workflow, and repository instructions. Use when the user asks to evaluate, test, benchmark, review, or improve Graphify/graphy/graph quality, query relevance, graph coverage, or Graphify instructions."
argument-hint: "Optional focus, symbols, questions, or graphify-out path"
user-invocable: true
---

# Suggest Graphify Improvements

Evaluate how well an existing Graphify graph answers representative questions, identify the layer responsible for each failure, and propose prioritized, testable improvements.

This is an analysis workflow by default. Do not rebuild/update the graph, edit Graphify code or customization files, or apply recommendations unless the user explicitly requests implementation.

## Inputs

Accept any combination of:

- A `graphify-out/` path. Otherwise use the nearest workspace root containing `graphify-out/graph.json`; if several workspace roots contain one, ask the user which graph to audit.
- User-supplied benchmark questions, symbols, paths, or known failures.
- A requested focus such as corpus quality, language-specific extraction, ranking, path finding, architecture coverage, or instructions.

When no benchmark cases are supplied, derive a small representative suite from authoritative documentation and current source as described below. Do not ask the user for cases unless no authoritative material or source is available.

## Required Boundaries

- Treat Graphify as a discovery index, not an authoritative source.
- Establish expected answers from authoritative documentation, live source, or tests before running the matching graph query.
- Do not use Graphify's answer as its own ground truth.
- Do not run `graphify update`, `cluster-only`, a full build, `save-result`, or any graph-mutating command during the benchmark.
- `graphify reflect --if-stale` is permitted because it deterministically refreshes lessons, but report when it writes output.
- Do not install or upgrade Graphify during an audit. Report a missing CLI as an environment finding.
- Do not modify product source or run product builds/tests; this skill evaluates graph behavior.
- Preserve query output needed as evidence, but do not add large raw outputs to the final response.

## Procedure

### 1. Load Local Policy

Follow the active workspace and repository instructions. In particular, honor their source-of-truth hierarchy, navigation rules, Git safety checks, generated-file exclusions, and restrictions on builds or external access.

- If a companion `graphify` skill is available, load it and its query guidance through the environment's skill-discovery mechanism; do not assume a filesystem location.
- If no companion skill is available, use the installed CLI's `query`, `explain`, and `path` help/output as the interface contract.
- Discover authoritative material from the current project, such as architecture documentation, API contracts, decision records, tests, and live source. Do not assume specific filenames or directory names.

The non-mutation boundaries in this skill take precedence during the benchmark even when a companion workflow normally writes query memories or updates the graph.

### 2. Audit Graph Health

Check for:

- `graphify-out/graph.json`
- `graphify-out/GRAPH_REPORT.md`
- `graphify-out/manifest.json`
- `graphify-out/.graphify_root`
- `graphify-out/.graphify_python`
- `graphify-out/reflections/LESSONS.md`

Record:

- Graph node, edge, community, and confidence counts.
- Node counts by `file_type` and top-level `source_file` prefix.
- Unique source-file count.
- Recorded corpus root and build commit, when available.
- Current commit of each represented Git repository, correlated to its corpus paths rather than assumed from the current working directory.
- Missing expected source or documentation roots.
- Generated, build, vendored, snapshot, or duplicate inputs.
- Duplicate exact labels that point to live source and generated/snapshot copies.

Before running a Git command, honor any active repository-target guard. Use read-only Git operations and confirm the repository root associated with each represented corpus path; do not assume a single-root workspace.

Classify health explicitly:

- **Freshness:** `current`, `stale`, or `unknown`.
- **Coverage:** `sufficient`, `partial`, or `missing` for each benchmark intent.
- **Noise:** `low`, `material`, or `dominant`.
- **Provenance:** `known` or `unknown`.

Do not rebuild automatically when health is poor. A stale or incomplete graph is itself evidence.

### 3. Build the Benchmark Suite

Use user-supplied cases first. Otherwise choose three to five cases that cover different retrieval shapes:

1. **Broad architecture:** a component/module/data-flow question whose answer is stated in authoritative docs.
2. **Focused behavior:** a known method or class with a small, falsifiable behavior visible in live source or a focused test.
3. **Exact symbol:** explain a class or method and inspect its immediate meaningful dependencies.
4. **Directed path:** trace a relationship between two unambiguous symbols that should have a meaningful directed route.
5. **Negative control, when useful:** ask about a concept absent from the intended corpus and verify that Graphify reports insufficient coverage rather than returning noise.

Keep the suite small enough to diagnose failures rather than merely collect outputs. For each case, write the expected facts and source references before querying the graph.

### 4. Execute Queries

Follow the health and intent preflight in the Graphify query policy.

- Use `graphify explain` with an exact symbol first for symbol and behavior cases.
- Resolve ambiguity with a repo-relative path or full node ID.
- Use BFS only for broad relationship discovery.
- Use DFS or `graphify path` only for a specific chain.
- Keep vocabulary expansion to the smallest discriminating set allowed by the Graphify policy.
- If a result exceeds 100 nodes or is truncated, retry once with fewer terms or exact-node explanation. Do not hide the explosion by increasing the budget.
- Keep directed path traversal as the default. Use `--undirected` only as a diagnostic and reject paths bridged solely by generic framework contracts, test bases, generated files, or snapshots.

Capture for each case:

- Query and expansion terms.
- Selected start nodes and whether they were ambiguous.
- Returned/truncated node count.
- Relevant nodes and edges.
- Missing expected facts or controlling edges.
- Test/generated/snapshot contamination.
- Whether source verification confirmed or contradicted the graph.

### 5. Score Each Case

Score each dimension from 0 to 3:

| Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Grounded accuracy | Wrong/misleading | Mostly unsupported | Correct but incomplete | Correct and evidenced |
| Precision | Dominated by noise | Much irrelevant output | Minor noise | Focused |
| Coverage | Expected facts absent | Major gaps | Small gaps | Complete for intent |
| Disambiguation | Wrong silent match | Ambiguous and awkward | Recoverable | Exact/automatic |
| Efficiency | Unusable/explosive | Multiple broad retries | One refinement | Direct result |

Do not average away a critical failure. A misleading path or unsupported behavior claim is a failed case even if other dimensions score well.

### 6. Attribute Root Cause

Assign each finding to one primary improvement surface:

- **Corpus/build:** wrong roots, missing docs, stale graph, generated inputs, duplicate snapshots, bad exclusions.
- **Extraction:** missing symbols, method calls, constants, direction, data flow, source locations, or confidence metadata.
- **Retrieval/ranking:** generic token expansion, poor start-node ranking, test/generated nodes outranking production, uncontrolled traversal size.
- **Path semantics:** ambiguous endpoints, direction loss, high-degree generic bridges, semantically meaningless shortest paths.
- **Graphify skill:** unsafe fast path, missing health checks, weak retry/stop rules, misleading answer synthesis, contaminated feedback.
- **Repository instructions/configuration:** unclear graph authority, intended corpus, exclusions, source verification, or tool routing.
- **Documentation/source:** missing authoritative explanation or code structure that no graph improvement can infer reliably.

Choose the narrowest root cause supported by evidence. Do not recommend a skill prompt change for an extraction defect, or a graph-engine change for a corpus-selection defect.

### 7. Generate Suggestions

Prioritize by impact, recurrence, and implementation cost:

- **P0:** Can produce incorrect or misleading answers.
- **P1:** Materially harms common query quality or coverage.
- **P2:** Improves ergonomics, reporting, or efficiency.

Every suggestion must include:

- **Evidence:** benchmark observation and relevant source/graph facts.
- **Root cause:** one improvement surface from Step 6.
- **Change:** concrete behavior or policy to implement.
- **Owner:** Graphify package, Graphify skill, repository instructions/configuration, corpus rebuild, or documentation.
- **Expected impact:** what query behavior improves.
- **Validation:** a specific rerun and measurable pass condition.
- **Effort:** `small`, `medium`, or `large`.

Prefer a few high-confidence suggestions over a long speculative list. Separate recommendations that can be implemented in this repository from changes requiring the external Graphify package.

## Output Format

Return these sections:

1. **Verdict** — two or three sentences stating where Graphify is useful and where it is unsafe or incomplete.
2. **Graph Health** — freshness, coverage, noise, provenance, and key counts.
3. **Benchmark Results** — compact table with case, mode, score, and decisive observation.
4. **Prioritized Suggestions** — findings ordered P0, P1, P2 using the required suggestion fields.
5. **What Not To Change** — behaviors that worked and should be preserved.
6. **Next Validation** — the smallest benchmark rerun that would prove the top recommendation worked.

Use clickable repository-relative links for local evidence. Clearly label facts derived from the graph versus facts verified in source/docs. State when a recommendation cannot be implemented in the current repository.

## Invocation Examples

```text
/suggest-graphify-improvements
/suggest-graphify-improvements focus on call extraction
/suggest-graphify-improvements test architecture queries and path quality
/suggest-graphify-improvements benchmark OrderService and suggest fixes
```