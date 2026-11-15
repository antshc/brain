# Graphify search: query, path, explain

How tactic (`hunty`) for searching an existing `graphify-out/` graph; searching only, never building. The graph root is always the harness root (`git rev-parse --show-toplevel` from the launch folder): the only graph is `<root>/graphify-out/`. Run from there, never from a `workspace/<repo>` checkout or a git worktree, and never probe those for their own `graphify-out/`; indexed repositories sit under `<root>/workspace/<repo>`. Default to the focused search script; the `graphify query` CLI and inline NetworkX traversal are fallbacks.

Building, updating, or exporting a graph is project-owned: `GRAPHIFY.md` names the build entry point. Never build, `--update`, or re-cluster from here.

## Contents

- Query health and intent preflight
- Focused search (default)
- CLI fallback: constrained query expansion and traversal
- Path between two nodes
- Explain one node
- Gotchas

Two traversal modes - choose based on the question:

| Mode | Flag | Best for |
|------|------|----------|
| BFS (default) | *(none)* | "What is X connected to?" - broad context, nearest neighbors first |
| DFS | `--dfs` | "How does X reach Y?" - trace a specific chain or dependency path |

## Query health and intent preflight

Set `$GRAPH` as in Focused search (default) first.

Run this preflight before every query, path, or explain operation against an existing graph:

0. Read `<graph root>/GRAPHIFY.md` in full when present. Its corpus, exclusion, health preflight, search vocabulary, and degraded-mode rules override the generic steps below.
1. Run `graphify reflect --if-stale` and read `graphify-out/reflections/LESSONS.md`. Do not repeat a known dead end unless the graph or source has changed.
2. Read `graphify-out/.graphify_root` when present and the recorded commit: `built_at_commit` in `graphify-out/graph.json`. If the root is a Git checkout, compare the recorded commit with its current `HEAD`. A missing root or commit makes freshness unknown; a mismatch makes the graph stale.
3. Inspect node `source_file` prefixes and `file_type` counts in `graphify-out/graph.json`. Report material generated/snapshot inputs such as `.artifacts/`, `bin/`, `obj/`, `TestResults/`, or `review_diff/`, and whether the source or documentation needed by the question is represented.
4. Print one concise health line before the query: corpus roots/coverage, freshness (`current`, `stale`, or `unknown`), and material noise. Do not rebuild automatically. When coverage is missing or freshness is stale, use the graph only for candidate discovery and verify against current source or authoritative documentation.

Classify the query before choosing traversal:

- **Exact symbol, file, or node:** `$GRAPH query <Symbol> --anchor` (add `--both` for callers), or `graphify explain` with the exact name. If it is ambiguous, retry with the repo-relative path or full node ID. Use broad traversal only if the exact node's neighborhood is insufficient.
- **Behavior of a known symbol:** explain the exact class and controlling method first. If the method node omits the calls or data flow that determine the result, state that the graph is insufficient and verify the behavior in live source; do not infer it from nearby type edges.
- **Broad architecture or relationship:** confirm that architecture/document nodes and the relevant source roots exist in the corpus before BFS. A code-only graph cannot authoritatively answer a documentation-level architecture question.
- **Path between concepts:** `resolve` both endpoints to exact class labels before path traversal and apply the path-quality rules below.

Run the health check; it covers steps 2-3 and exits `1` when the graph is missing:

```bash
$GRAPH check
```

If it fails, report the missing graph and the build entry point named in `GRAPHIFY.md` (if any), then continue without the graph.

## Focused search (default)

`scripts/graph.py` (research skill base directory) is the single read-only entry point for every graph operation below; it writes nothing. Run it from the graph root with the graphify interpreter:

```bash
GRAPH="$(cat graphify-out/.graphify_python 2>/dev/null || echo python3) <research>/scripts/graph.py"
$GRAPH --help
```

`--graph PATH` selects another graph. Focused commands (`terms`, `query`, `resolve`, `path`) need the `graphify` module; they drop nodes that are never the answer to a code question: tests, folders named `*deprecated*`, generated/build output, `graphify-out/`, `mocks/`/`mocker/` servers, project/package manifests, namespace and solution-project nodes, and sourceless external types. Pass `--keep test` (comma list) when the question is about tests. Fallback commands (`check`, `contexts`, `vocab`, `slice`, `traverse`, `raw-path`, `explain`) need only the stdlib.

| Command | Use |
|---|---|
| `terms "<question>"` | Candidate terms: adjacent question words joined into compounds the graph contains (`memberaccounthealth`), longest first, then rare single words, with label hit counts. |
| `query <T1> [<T2>]` | BFS depth 2 from the best match of each term. `--anchor` seeds only the top match; `--both --anchor` lists 1-hop callers and callees; `--context call` filters edges. |
| `resolve "<Label or phrase>"` | Exact class label first, then best compound match; returns `label file:line` to pick path endpoints. |
| `path <A> <B>` | Shortest path on the focused graph, both directions, import edges dropped. |

Search-term rules:

- **MUST** search with 1-2 identifier-shaped terms per query, never the raw question. Run several small queries rather than one long one; every extra term buys its own seed and floods the output.
- Translate question words into how code names things: CamelCase compounds of domain + role (`OrderJanitor`, `InvoicePaid`, `LicenseValidation`, `DanglingVolume`), using `GRAPHIFY.md` search vocabulary when present and role suffixes such as `Controller`, `Manager`, `Task`, `HostedService`, `BackgroundService`, `Middleware`, `Repository`, `Converter`, `Facade`, `Validator`, `Invoker`, `Events`, `Accessor`.
- Run `terms` first; keep a suggestion only when its hit count is small (roughly under 50) and it names the concept. Add your own code-shaped guesses and check them with `terms`/`resolve`.
- Drop words that only describe the question (`how`, `flow`, `explain`, `each`, `old`, `request`) and generic singles (`service`, `manager`, `api`, `task`, `status`, `configuration`); alone they seed unrelated nodes.
- Known symbol → `query <Symbol> --anchor` (add `--both` for callers); unknown names → `terms`, then `query` with the top 1-2.
- Flow between two parts → `resolve` both ends to exact class labels, then `path`. Interface hops (`IFoo` between `Foo` and its caller) are the real dependency; a hop through a shared parameter/DTO type is a shortcut, so confirm the call chain in source.
- Truncated output (`[!] TRUNCATED`) → narrow the term or add `--anchor`; do not raise `--budget` first.

The fallback below applies only when the focused commands cannot run (`graph.py` exits `3`: no `graphify` module for the interpreter).

## CLI fallback: constrained query expansion and traversal

### Step 0 — Constrained query expansion (REQUIRED before broad traversal)

graphify's `query` CLI matches nodes via case-folded substring + IDF — there is **no stemming, no synonyms, no cross-language match** inside the binary, and the inline fallback below matches the same way. If the user's question uses different language or different domain vocabulary than the graph's labels (user says "обработчик" / graph says "handler"; user says "authentication" / graph says "Guardian"), the literal matcher returns 0 hits and the answer collapses to noise.

Fix this **without inventing tokens** by expanding the query against the actual graph vocabulary first:

1. Print the token vocabulary from node labels (read-only; nothing is written):

   ```bash
   $GRAPH vocab
   ```

2. From the `vocab` output, for the user's question, select **up to 5 tokens from this exact list** that semantically match the query intent. For a symbol-oriented query that still needs traversal, use at most 3 discriminating tokens. Hard constraints:
   - You MUST pick only tokens present in the `vocab` output. Do NOT invent tokens.
   - Prefer tokens from the exact symbol or path over generic terms such as `service`, `manager`, `result`, `configuration`, or `test`.
   - Do not add both singular and plural forms unless they identify genuinely different graph labels.
   - If a query concept has no plausible token in the vocab, skip it — do not substitute a near-synonym from training memory.
   - If **no** vocab tokens match the query at all, output an empty list and tell the user the corpus has no relevant vocabulary for this question. Do not fabricate a search.
   - Translate cross-language: Russian "аутентификация" → look for `auth`, `credential`, `token`, `security` IFF present in vocab.
   - Morphology: "handlers" maps to `handler` IFF present; "todos" maps to `todo` IFF present.

3. Print the selection explicitly to the user before running the query, so the expansion is auditable:

```text
Query expanded to (from graph vocab, N tokens): [token1, token2, ...]
```

If the list is empty, say so plainly and stop — do not proceed to traversal.

### Step 1 — Traversal

Build the **expanded query string** by joining the selected tokens with spaces. Use this string as `QUESTION` below — NOT the original user question. (The original question is preserved only for `save-result` at the end.)

Prefer the CLI when it is installed:

```bash
graphify query "QUESTION"
# or: graphify query "QUESTION" --dfs --budget 3000
```

Treat a broad query as discovery, not as the answer subgraph. Apply this precision ladder:

1. Run the expanded query once to discover candidate anchors.
2. Select one exact live-source symbol with `graphify explain`. Prefer an exact label containing all discriminating terms, then production source over tests, generated artifacts, review snapshots, and duplicate copies.
3. Rerun from that exact label. Add repeatable `--context` filters only when the question needs a specific edge context. `--context` matches the edge's `context` field, not its relation; for example, `call` filters `calls` edges, while `field`, `parameter_type`, and `return_type` select different kinds of `references` edges.
4. Derive valid contexts from the current graph instead of guessing them. A context filter does not cross uncontextualized containment or class-to-method edges, so anchor on the relevant method before applying `--context call`.

```bash
$GRAPH contexts
graphify explain "EXACT_SYMBOL"
graphify query "EXACT_SYMBOL" --context call --budget 2000
```

If the discovery query reports more than 100 nodes or truncates, do not raise its budget. Move down the precision ladder. After anchoring and filtering, a result under 100 nodes may use a larger budget once to avoid output truncation. If the filtered retry still exceeds 100 nodes, or no context preserves the needed relationship, report that the neighborhood is too broad and use another authoritative navigation tool rather than presenting a truncated traversal as an answer.

The CLI query depth is fixed at 2. When the second hop fans out through a shared dependency, use a direction-aware raw-edge slice instead. Set `SOURCE_CONTAINS` when an exact label has multiple definitions. Keep `MAX_DEPTH=1` for direct dependencies; increase it only when the question explicitly requires a transitive relationship.

```bash
$GRAPH slice EXACT_SYMBOL --context field --relation references --direction out --depth 1
# duplicate labels: add --source-contains <path fragment>; --direction in|both for callers
```

If the CLI is unavailable, load `graphify-out/graph.json` and run the traversal inline:

1. Find the 1-3 nodes whose label best matches the expanded tokens.
2. Run the appropriate traversal from each starting node.
3. Read the subgraph - node labels, edge relations, confidence tags, source locations.
4. Answer using **only** what the graph contains. Quote `source_location` when citing a specific fact.
5. If the graph lacks enough information, say so - do not hallucinate edges.

```bash
$GRAPH traverse QUESTION                       # BFS, depth 2
$GRAPH traverse QUESTION --dfs --budget 3000   # DFS, depth 6
$GRAPH traverse QUESTION --context call --relation calls
```

Replace `QUESTION`

Replace `QUESTION` with the **expanded** query string. `--context`/`--relation` take observed edge contexts and graph relations (repeatable or comma lists); `--budget` defaults to `2000`. Then answer based on the subgraph output above, using only what the graph contains.

After writing the answer, save it back into the graph so it improves future queries. Include the expanded tokens inside the `--answer` text (e.g. `"Expanded from original query via vocab: [tokens]. Then traversed..."`) so the next `--update` extracts the expansion history as a graph node:

```bash
$(cat graphify-out/.graphify_python) -m graphify save-result --question "ORIGINAL_QUESTION" --answer "ANSWER" --type query --nodes NODE1 NODE2
```

Replace `ORIGINAL_QUESTION` with the user's verbatim question, `ANSWER` with your full answer text (containing the expanded-token trace), `NODE1 NODE2` with the list of node labels you cited. This closes the feedback loop: the next `--update` will extract this Q&A as a node in the graph.

**Work memory (self-improving loop).** Add an `--outcome` so future sessions learn from this one — append `--outcome useful|dead_end|corrected` to the `save-result` command (and `--correction "the right answer"` when correcting):

- `useful` — the cited nodes answered the question well (they become *preferred sources*).
- `dead_end` — the question/path led nowhere; don't re-derive it next time.
- `corrected` — the saved answer was wrong; `--correction` records what was right.

Judge the outcome against the user's intent, not incidental utility. For example, locating a class is still `dead_end` when the question asked for behavior and the graph omitted the controlling method calls. Prefix the saved answer with `Intent: architecture|symbol_location|behavior|dependency_path` so later reflection can distinguish why the same node succeeded or failed. Do not save a separate `useful` localization result when localization was only an unsuccessful substep of a behavior query.

At the **start** of graph work, refresh and read the lessons: run `graphify reflect --if-stale` (cheap, deterministic, no LLM; `--if-stale` makes it a no-op when `LESSONS.md` is already newer than every input, e.g. when the git hook just refreshed it), then read `graphify-out/reflections/LESSONS.md`. It lists **preferred sources** (start there), **known dead ends** (skip them), and prior **corrections**. Running `reflect` yourself keeps the lessons current even without the git hook installed; if the post-commit hook *is* installed, `--if-stale` means your session-start run costs almost nothing.

---

## Path between two nodes

Default: `resolve` both endpoints to exact class labels, then run `$GRAPH path <A> <B>` (see Focused search (default)). The CLI path is directed; across interface edges (`Caller → IFoo ← Foo`) it finds no path, and phrase endpoints resolve to namespaces or generic nodes. Fallback when the script cannot run: first run `graphify explain` for both endpoints. Resolve every ambiguity with a repo-relative path or full node ID before asking for a path. Prefer the CLI when installed:

```bash
graphify path "NODE_A" "NODE_B"
```

If the CLI is unavailable:

```bash
$GRAPH raw-path "NODE_A" "NODE_B"   # add --undirected only when direction is irrelevant
```

Replace `NODE_A` and `NODE_B` with the actual concept names from the user. Then explain the path in plain language - what each hop means, why it's significant.

Use directed traversal by default. Retry with `--undirected` only when direction is irrelevant to the user's question. Reject an undirected path as a dead end when its only bridge is a generic high-degree contract (`IDisposable`, `IEquatable`, `Object`, and similar), a test base, or a generated/review-snapshot node unrelated to the question. A mathematically shortest path is not evidence of a meaningful architectural relationship. Save rejected paths with `--outcome dead_end`.

After writing the explanation, save it back:

```bash
$(cat graphify-out/.graphify_python) -m graphify save-result --question "Path from NODE_A to NODE_B" --answer "ANSWER" --type path_query --nodes NODE_A NODE_B
```

---

## Explain one node

Give a plain-language explanation of a single node - everything connected to it. Prefer the CLI when installed:

```bash
graphify explain "NODE_NAME"
```

If the CLI is unavailable:

```bash
$GRAPH explain "NODE_NAME"
```

Replace `NODE_NAME` with the concept the user asked about. Then write a 3-5 sentence explanation of what this node is, what it connects to, and why those connections are significant. Use the source locations as citations.

After writing the explanation, save it back:

```bash
$(cat graphify-out/.graphify_python) -m graphify save-result --question "Explain NODE_NAME" --answer "ANSWER" --type explain --nodes NODE_NAME
```

## Gotchas

- `graph.py` focused commands need `graphifyy` and `networkx`; fallback commands need neither. Before first run, read `scripts/requirements.txt` (research skill base directory) in full.
- `ModuleNotFoundError` for `graphify`/`networkx` in the chosen interpreter → install with that interpreter: `<python> -m pip install -r <research>/scripts/requirements.txt`; rerun. Skip install when imports succeed.
- Install only requirements.txt; **MUST NOT** upgrade or unpin versions.
