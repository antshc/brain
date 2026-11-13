# Graphify search: query, path, explain

Research skill playbook for searching an existing `graphify-out/` graph; searching only, never building. Run from the graph root: the launch repository root (harness reporoot), never a git worktree; indexed repositories usually sit under `<root>/workspace/<repo>`. Default to the focused search script; the `graphify query` CLI and inline NetworkX traversal are fallbacks.

Building, updating, or exporting a graph is project-owned: `GRAPHIFY.md` names the build entry point. Never build, `--update`, or re-cluster from here.

## Contents

- Query health and intent preflight
- Focused search (default)
- CLI fallback: constrained query expansion and traversal
- Path between two nodes
- Explain one node

Two traversal modes - choose based on the question:

| Mode | Flag | Best for |
|------|------|----------|
| BFS (default) | _(none)_ | "What is X connected to?" - broad context, nearest neighbors first |
| DFS | `--dfs` | "How does X reach Y?" - trace a specific chain or dependency path |

## Query health and intent preflight

Run this preflight before every query, path, or explain operation against an existing graph:

0. Read `<graph root>/GRAPHIFY.md` in full when present. Its corpus, exclusion, health preflight, search vocabulary, and degraded-mode rules override the generic steps below.
1. Run `graphify reflect --if-stale` and read `graphify-out/reflections/LESSONS.md`. Do not repeat a known dead end unless the graph or source has changed.
2. Read `graphify-out/.graphify_root` when present and the recorded commit: `built_at_commit` in `graphify-out/graph.json`. If the root is a Git checkout, compare the recorded commit with its current `HEAD`. A missing root or commit makes freshness unknown; a mismatch makes the graph stale.
3. Inspect node `source_file` prefixes and `file_type` counts in `graphify-out/graph.json`. Report material generated/snapshot inputs such as `.artifacts/`, `bin/`, `obj/`, `TestResults/`, or `review_diff/`, and whether the source or documentation needed by the question is represented.
4. Print one concise health line before the query: corpus roots/coverage, freshness (`current`, `stale`, or `unknown`), and material noise. Do not rebuild automatically. When coverage is missing or freshness is stale, use the graph only for candidate discovery and verify against current source or authoritative documentation.

Classify the query before choosing traversal:

- **Exact symbol, file, or node:** `focused_query.py query <Symbol> --anchor` (add `--both` for callers), or `graphify explain` with the exact name. If it is ambiguous, retry with the repo-relative path or full node ID. Use broad traversal only if the exact node's neighborhood is insufficient.
- **Behavior of a known symbol:** explain the exact class and controlling method first. If the method node omits the calls or data flow that determine the result, state that the graph is insufficient and verify the behavior in live source; do not infer it from nearby type edges.
- **Broad architecture or relationship:** confirm that architecture/document nodes and the relevant source roots exist in the corpus before BFS. A code-only graph cannot authoritatively answer a documentation-level architecture question.
- **Path between concepts:** `resolve` both endpoints to exact class labels before path traversal and apply the path-quality rules below.

First check the graph exists:
```bash
$(cat graphify-out/.graphify_python 2>/dev/null || echo python3) -c "
from pathlib import Path
if not Path('graphify-out/graph.json').exists():
    print('ERROR: No graph found.')
    raise SystemExit(1)
"
```
If it fails, report the missing graph and the build entry point named in `GRAPHIFY.md` (if any), then continue without the graph.

## Focused search (default)

`scripts/focused_query.py` (research skill base directory) is read-only and writes nothing. Run it from the graph root with the graphify interpreter (`$(cat graphify-out/.graphify_python)`, else `python3`); `--graph PATH` selects another graph. It drops nodes that are never the answer to a code question: tests, folders named `*deprecated*`, generated/build output, `graphify-out/`, `mocks/`/`mocker/` servers, project/package manifests, namespace and solution-project nodes, and sourceless external types. Pass `--keep test` (comma list) when the question is about tests.

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

The CLI fallback below applies only when `focused_query.py` cannot run (no `graphify` Python module for the interpreter).

## CLI fallback: constrained query expansion and traversal

### Step 0 — Constrained query expansion (REQUIRED before broad traversal)

graphify's `query` CLI matches nodes via case-folded substring + IDF — there is **no stemming, no synonyms, no cross-language match** inside the binary, and the inline fallback below matches the same way. If the user's question uses different language or different domain vocabulary than the graph's labels (user says "обработчик" / graph says "handler"; user says "authentication" / graph says "Guardian"), the literal matcher returns 0 hits and the answer collapses to noise.

Fix this **without inventing tokens** by expanding the query against the actual graph vocabulary first:

1. Extract the token vocabulary from node labels:
```bash
$(cat graphify-out/.graphify_python) -c "
import json, re
from pathlib import Path
data = json.loads(Path('graphify-out/graph.json').read_text(encoding='utf-8'))
vocab = set()
for n in data['nodes']:
    for c in re.findall(r'[^\W\d_]+', n.get('label','') or '', re.UNICODE):
        parts = re.findall(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+', c) or [c]
        for p in parts:
            t = p.lower()
            if 3 <= len(t) <= 30:
                vocab.add(t)
Path('graphify-out/.vocab.txt').write_text('\n'.join(sorted(vocab)), encoding='utf-8')
print(f'vocab: {len(vocab)} tokens')
"
```

2. Read `graphify-out/.vocab.txt`. Then for the user's question, select **up to 5 tokens from this exact list** that semantically match the query intent. For a symbol-oriented query that still needs traversal, use at most 3 discriminating tokens. Hard constraints:
   - You MUST pick only tokens present in the vocabulary file. Do NOT invent tokens.
    - Prefer tokens from the exact symbol or path over generic terms such as `service`, `manager`, `result`, `configuration`, or `test`.
    - Do not add both singular and plural forms unless they identify genuinely different graph labels.
   - If a query concept has no plausible token in the vocab, skip it — do not substitute a near-synonym from training memory.
   - If **no** vocab tokens match the query at all, output an empty list and tell the user the corpus has no relevant vocabulary for this question. Do not fabricate a search.
   - Translate cross-language: Russian "аутентификация" → look for `auth`, `credential`, `token`, `security` IFF present in vocab.
   - Morphology: "handlers" maps to `handler` IFF present; "todos" maps to `todo` IFF present.

3. Print the selection explicitly to the user before running the query, so the expansion is auditable:
```
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
python -c 'import collections,json; from pathlib import Path; g=json.loads(Path("graphify-out/graph.json").read_text()); print(collections.Counter((e.get("context") or "(none)") for e in g.get("links", g.get("edges", []))).most_common())'
graphify explain "EXACT_SYMBOL"
graphify query "EXACT_SYMBOL" --context call --budget 2000
```

If the discovery query reports more than 100 nodes or truncates, do not raise its budget. Move down the precision ladder. After anchoring and filtering, a result under 100 nodes may use a larger budget once to avoid output truncation. If the filtered retry still exceeds 100 nodes, or no context preserves the needed relationship, report that the neighborhood is too broad and use another authoritative navigation tool rather than presenting a truncated traversal as an answer.

The CLI query depth is fixed at 2. When the second hop fans out through a shared dependency, use a direction-aware raw-edge slice instead. Set `SOURCE_CONTAINS` when an exact label has multiple definitions. Keep `MAX_DEPTH=1` for direct dependencies; increase it only when the question explicitly requires a transitive relationship.

```bash
$(cat graphify-out/.graphify_python) - <<'PY'
import json
from collections import defaultdict, deque
from pathlib import Path

START_LABEL = 'EXACT_SYMBOL'
SOURCE_CONTAINS = ''
CONTEXTS = {'field'}
RELATIONS = {'references'}
DIRECTION = 'out'  # 'out', 'in', or 'both'
MAX_DEPTH = 1

data = json.loads(Path('graphify-out/graph.json').read_text(encoding='utf-8'))
nodes = {node['id']: node for node in data['nodes']}
candidates = [node_id for node_id, node in nodes.items()
              if node.get('label') == START_LABEL
              and SOURCE_CONTAINS.lower() in (node.get('source_file') or '').lower()]
if len(candidates) != 1:
    print('Expected one exact start node; candidates:')
    for node_id in candidates:
        print(nodes[node_id].get('source_file', ''), nodes[node_id].get('source_location', ''))
    raise SystemExit(1)

adjacency = defaultdict(list)
for edge in data.get('links', data.get('edges', [])):
    if CONTEXTS and (edge.get('context') or '') not in CONTEXTS:
        continue
    if RELATIONS and (edge.get('relation') or '') not in RELATIONS:
        continue
    source, target = edge['source'], edge['target']
    if DIRECTION in {'out', 'both'}:
        adjacency[source].append((target, edge))
    if DIRECTION in {'in', 'both'}:
        adjacency[target].append((source, edge))

start = candidates[0]
distances = {start: 0}
selected_edges = []
queue = deque([start])
while queue:
    source = queue.popleft()
    if distances[source] >= MAX_DEPTH:
        continue
    for target, edge in adjacency[source]:
        selected_edges.append((source, target, edge))
        if target not in distances:
            distances[target] = distances[source] + 1
            queue.append(target)

for node_id in sorted(distances, key=lambda item: (distances[item], nodes[item].get('label', ''))):
    node = nodes[node_id]
    print(f"NODE depth={distances[node_id]} {node.get('label')} src={node.get('source_file', '')} loc={node.get('source_location', '')}")
for source, target, edge in selected_edges:
    print(f"EDGE {nodes[source].get('label')} --{edge.get('relation')} [{edge.get('context', '')}]--> {nodes[target].get('label')}")
PY
```

If the CLI is unavailable, load `graphify-out/graph.json` and run the traversal inline:

1. Find the 1-3 nodes whose label best matches the expanded tokens.
2. Run the appropriate traversal from each starting node.
3. Read the subgraph - node labels, edge relations, confidence tags, source locations.
4. Answer using **only** what the graph contains. Quote `source_location` when citing a specific fact.
5. If the graph lacks enough information, say so - do not hallucinate edges.

```bash
$(cat graphify-out/.graphify_python) -c "
import sys, json
from networkx.readwrite import json_graph
import networkx as nx
from pathlib import Path

data = json.loads(Path('graphify-out/graph.json').read_text(encoding='utf-8'))
G = json_graph.node_link_graph(data, edges='links')

question = 'QUESTION'
mode = 'MODE'  # 'bfs' or 'dfs'
terms = [t.lower() for t in question.split() if len(t) >= 3]  # match the vocab threshold; keeps api/jwt/ios (#1392)
context_filters = set(CONTEXT_FILTERS)  # e.g. {'call'}; empty means all contexts
relation_filters = set(RELATION_FILTERS)  # e.g. {'calls'}; empty means all relations

# Find best-matching start nodes
scored = []
for nid, ndata in G.nodes(data=True):
    label = ndata.get('label', '').lower()
    overlap = sum(1 for t in terms if t in label)
    if overlap == 0:
        continue
    source = (ndata.get('source_file') or '').lower()
    exact = label == question.lower()
    all_terms = overlap == len(terms)
    source_penalty = 20 if any(part in source for part in ('/test/', '/tests/', '/generated/', '/obj/', '/bin/')) else 0
    degree_penalty = min(G.degree(nid), 100) / 100
    score = (100 if exact else 0) + (20 if all_terms else 0) + overlap * 5 - source_penalty - degree_penalty
    scored.append((score, nid))
scored.sort(reverse=True)
exact_starts = [nid for _, nid in scored if G.nodes[nid].get('label', '').lower() == question.lower()]
start_nodes = exact_starts[:1] or [nid for _, nid in scored[:3]]

if not start_nodes:
    print('No matching nodes found for query terms:', terms)
    sys.exit(0)

subgraph_nodes = set()
subgraph_edges = []

def allowed_neighbors(node):
    for neighbor in G.neighbors(node):
        raw = G.get_edge_data(node, neighbor)
        edge_values = raw.values() if isinstance(G, nx.MultiGraph) else [raw]
        for edge in edge_values:
            context_allowed = not context_filters or (edge.get('context') or '') in context_filters
            relation_allowed = not relation_filters or (edge.get('relation') or '') in relation_filters
            if context_allowed and relation_allowed:
                yield neighbor, edge

if mode == 'dfs':
    # DFS: follow one path as deep as possible before backtracking.
    # Depth-limited to 6 to avoid traversing the whole graph.
    visited = set()
    stack = [(n, 0) for n in reversed(start_nodes)]
    while stack:
        node, depth = stack.pop()
        if node in visited or depth > 6:
            continue
        visited.add(node)
        subgraph_nodes.add(node)
        for neighbor, _ in allowed_neighbors(node):
            if neighbor not in visited:
                stack.append((neighbor, depth + 1))
                subgraph_edges.append((node, neighbor))
else:
    # Match the CLI: explore all allowed neighbors layer by layer up to depth 2.
    frontier = set(start_nodes)
    subgraph_nodes = set(start_nodes)
    distances = {node: 0 for node in start_nodes}
    for depth in range(2):
        next_frontier = set()
        for n in frontier:
            for neighbor, _ in allowed_neighbors(n):
                if neighbor not in subgraph_nodes:
                    next_frontier.add(neighbor)
                    distances[neighbor] = depth + 1
                    subgraph_edges.append((n, neighbor))
        subgraph_nodes.update(next_frontier)
        frontier = next_frontier

# Token-budget aware output: rank by relevance, cut at budget (~4 chars/token)
token_budget = BUDGET  # default 2000
char_budget = token_budget * 4

# Score each node by term overlap for ranked output
def relevance(nid):
    label = G.nodes[nid].get('label', '').lower()
    source = (G.nodes[nid].get('source_file') or '').lower()
    overlap = sum(1 for t in terms if t in label)
    source_penalty = 20 if any(part in source for part in ('/test/', '/tests/', '/generated/', '/obj/', '/bin/')) else 0
    distance_penalty = distances.get(nid, 0) * 2 if mode == 'bfs' else 0
    degree_penalty = min(G.degree(nid), 100) / 100
    return (100 if label == question.lower() else 0) + overlap * 5 - source_penalty - distance_penalty - degree_penalty

ranked_nodes = sorted(subgraph_nodes, key=relevance, reverse=True)

lines = [f'Traversal: {mode.upper()} | Start: {[G.nodes[n].get(\"label\",n) for n in start_nodes]} | {len(subgraph_nodes)} nodes']
for nid in ranked_nodes:
    d = G.nodes[nid]
    lines.append(f'  NODE {d.get(\"label\", nid)} [src={d.get(\"source_file\",\"\")} loc={d.get(\"source_location\",\"\")}]')
for u, v in subgraph_edges:
    if u in subgraph_nodes and v in subgraph_nodes:
        _raw = G[u][v]; d = next(iter(_raw.values()), {}) if isinstance(G, nx.MultiGraph) else _raw
        lines.append(f'  EDGE {G.nodes[u].get(\"label\",u)} --{d.get(\"relation\",\"\")} [{d.get(\"confidence\",\"\")}]--> {G.nodes[v].get(\"label\",v)}')

output = '\n'.join(lines)
if len(output) > char_budget:
    output = output[:char_budget] + f'\n... (truncated at ~{token_budget} token budget - use --budget N for more)'
print(output)
"
```

Replace `QUESTION` with the **expanded** query string, `MODE` with `bfs` or `dfs`, `CONTEXT_FILTERS` with a Python list of observed edge contexts (empty by default), `RELATION_FILTERS` with a Python list of graph relations (empty by default), and `BUDGET` with the token budget (default `2000`, or whatever `--budget N` specifies). Then answer based on the subgraph output above, using only what the graph contains.

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

Default: `resolve` both endpoints to exact class labels, then run `focused_query.py path <A> <B>` (see Focused search (default)). The CLI path is directed; across interface edges (`Caller → IFoo ← Foo`) it finds no path, and phrase endpoints resolve to namespaces or generic nodes. Fallback when the script cannot run: first run `graphify explain` for both endpoints. Resolve every ambiguity with a repo-relative path or full node ID before asking for a path. Prefer the CLI when installed:

```bash
graphify path "NODE_A" "NODE_B"
```

If the CLI is unavailable, run it inline:

```bash
$(cat graphify-out/.graphify_python) -c "
import json, sys
import networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path

data = json.loads(Path('graphify-out/graph.json').read_text(encoding='utf-8'))
G = json_graph.node_link_graph(data, edges='links')

a_term = 'NODE_A'
b_term = 'NODE_B'

def find_node(term):
    term = term.lower()
    scored = sorted(
        [(sum(1 for w in term.split() if w in G.nodes[n].get('label','').lower()), n)
         for n in G.nodes()],
        reverse=True
    )
    return scored[0][1] if scored and scored[0][0] > 0 else None

src = find_node(a_term)
tgt = find_node(b_term)

if not src or not tgt:
    print(f'Could not find nodes matching: {a_term!r} or {b_term!r}')
    sys.exit(0)

try:
    path = nx.shortest_path(G, src, tgt)
    print(f'Shortest path ({len(path)-1} hops):')
    for i, nid in enumerate(path):
        label = G.nodes[nid].get('label', nid)
        if i < len(path) - 1:
            _raw = G[nid][path[i+1]]; edge = next(iter(_raw.values()), {}) if isinstance(G, nx.MultiGraph) else _raw
            rel = edge.get('relation', '')
            conf = edge.get('confidence', '')
            print(f'  {label} --{rel}--> [{conf}]')
        else:
            print(f'  {label}')
except nx.NetworkXNoPath:
    print(f'No path found between {a_term!r} and {b_term!r}')
except nx.NodeNotFound as e:
    print(f'Node not found: {e}')
"
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

If the CLI is unavailable, run it inline:

```bash
$(cat graphify-out/.graphify_python) -c "
import json, sys
import networkx as nx
from networkx.readwrite import json_graph
from pathlib import Path

data = json.loads(Path('graphify-out/graph.json').read_text(encoding='utf-8'))
G = json_graph.node_link_graph(data, edges='links')

term = 'NODE_NAME'
term_lower = term.lower()

# Find best matching node
scored = sorted(
    [(sum(1 for w in term_lower.split() if w in G.nodes[n].get('label','').lower()), n)
     for n in G.nodes()],
    reverse=True
)
if not scored or scored[0][0] == 0:
    print(f'No node matching {term!r}')
    sys.exit(0)

nid = scored[0][1]
data_n = G.nodes[nid]
print(f'NODE: {data_n.get(\"label\", nid)}')
print(f'  source: {data_n.get(\"source_file\",\"unknown\")}')
print(f'  type: {data_n.get(\"file_type\",\"unknown\")}')
print(f'  degree: {G.degree(nid)}')
print()
print('CONNECTIONS:')
for neighbor in G.neighbors(nid):
    _raw = G[nid][neighbor]; edge = next(iter(_raw.values()), {}) if isinstance(G, nx.MultiGraph) else _raw
    nlabel = G.nodes[neighbor].get('label', neighbor)
    rel = edge.get('relation', '')
    conf = edge.get('confidence', '')
    src_file = G.nodes[neighbor].get('source_file', '')
    print(f'  --{rel}--> {nlabel} [{conf}] ({src_file})')
"
```

Replace `NODE_NAME` with the concept the user asked about. Then write a 3-5 sentence explanation of what this node is, what it connects to, and why those connections are significant. Use the source locations as citations.

After writing the explanation, save it back:

```bash
$(cat graphify-out/.graphify_python) -m graphify save-result --question "Explain NODE_NAME" --answer "ANSWER" --type explain --nodes NODE_NAME
```
