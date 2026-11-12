# CodeGraphContext vs graphify — measured code search on a C#/TypeScript product

Researched: 2026-11-12  
Scope: [CodeGraphContext (CGC)](https://github.com/CodeGraphContext/CodeGraphContext) 0.6.13 (Tree-sitter and SCIP variants) vs [graphify](https://pypi.org/project/graphifyy/) 0.9.107 on one private product codebase.  
Related research: [CGC SCIP indexing for C# and TypeScript](cgc-scip-csharp-typescript.md), [CGC multi-repository workspaces](https://github.com/antshc/brain/blob/research/cgc-multirepo/docs/research/cgc-multirepo.md).

## Question

Is CGC a better code-search graph than graphify for an AI agent answering "where is X" and "how does A reach B" questions on a real C# backend plus TypeScript frontend?

## Verdict

**No, not overall; CGC was evaluated and not adopted.** Its strength is narrow: with SCIP it gives exact "who calls X / what implements I" answers through interfaces. graphify wins on multi-hop flow tracing, frontend code, docs coverage, and in the agent-in-the-loop run.

| Dimension | graphify | CGC (best variant) | Winner |
|---|---|---|---|
| Locate code, best skill script | 0.536 | 0.621 (SCIP) | CGC, but the gain comes from a custom script, not CGC's own commands |
| Locate code, raw CLI | 0.302 | 0.279 (Tree-sitter) | graphify (slightly) |
| Trace A→B, best skill script | 0.950 | 0.794 (SCIP) | graphify |
| Trace A→B, CGC built-ins (`analyze chain`, Cypher `shortestPath`) | — | 0 of 6 flows | — |
| Agent run (6 cases × 1 run) | 0.820 | 0.702 | graphify |
| Frontend (React) components | indexed | SCIP drops arrow-function components | graphify |
| Docs, ADRs, concepts | indexed | code only | graphify |
| Exact callers through DI interfaces | approximate | compiler-exact (SCIP) | CGC |
| Index size | 85 MB JSON | ~8 MB DB; SCIP run 8 min, 840 MB RAM | CGC lighter |

Scores are 0-1 means over golden cases; see Method.

## Method

### Codebase

- Backend: one C# repository, ~2,730 `.cs` files, one `.sln`, ASP.NET Core services with DI and interface-based modules.
- Frontend: one React/TypeScript app, ~360 `.ts`/`.tsx` files (a deprecated legacy frontend excluded).
- Indexed as two non-overlapping CGC roots into one named context (one per language, so each gets its own SCIP pass, per the related SCIP research).

### Cases and metrics

22 golden cases verified against source: 14 `locate`, 6 `flow` (endpoints + required intermediate files), 2 `explain`. Questions use user wording and do not name the answer classes.

| Metric | Definition |
|---|---|
| Query score | 0.35 MRR + 0.35 recall of expected files in the visible output (first 2,000 tokens) + 0.2 precision (hits inside the case's code area) + 0.1 non-noise (not test/mock/generated/manifest) |
| Path score | 0.3 endpoints resolved + 0.2 path found + 0.3 recall of required intermediate files + 0.2 share of semantic hops (not import/file/namespace hubs) |
| Agent score | 0.5 answer recall (cited files) + 0.3 best graph-call score + 0.2 clean citations |

Both backends consumed the same fixed term sets per case (raw question terms, graphify skill terms, optimizer oracle terms), so differences come from index and ranking, not term choice. CGC was queried through one long-lived read-only worker (in-process Cypher and the CLI's own `find`/`analyze` code paths) so latency excludes CLI start-up.

### Strategies

| CGC strategy | Mirrors graphify | What it does |
|---|---|---|
| `cgc_find_raw` | `raw` (`graphify query "<question>"`) | `cgc find name` per question term |
| `cgc_find_skill` | `skill_q2` | `cgc find name` for the graphify skill's top-2 terms |
| `cgc_pattern_skill` | `compound` | `cgc find pattern` for the same terms |
| `cgc_neighborhood` | `skill_both` | top hit, all 1-hop neighbours |
| `cgc_cypher_bfs` | `skill_q2` | top hits, 2 hops over CALLS/INHERITS/IMPLEMENTS/CONTAINS, tests filtered |
| `cgc_skill` | `skill_q2` | custom script: identifier-compound terms → substring find (types first) → neighbours |
| `cgc_chain` | `path_cli` | `cgc analyze chain A B --depth 8` |
| `cgc_cypher_path` | `path_cli_undirected` | Cypher `shortestPath` A→B, else B→A |
| `cgc_skill_path` | `skill_path` | custom script: resolve endpoints, cheapest undirected path, hub nodes penalized |

## Results

### Index cost and graph shape

| | CGC Tree-sitter | CGC SCIP | graphify |
|---|---|---|---|
| Index wall time backend / frontend | 350 s / 32 s | 481 s / 85 s | not measured |
| Peak RSS backend / frontend | 323 / 194 MB | 839 / 844 MB | — |
| DB / export bundle | 7.8 / 3.3 MB | 8.4 / 3.2 MB | 85 MB `graph.json` |
| Function / Class / Interface nodes | 11,415 / 2,310 / 624 | 10,287 / 2,551 / 419 | 24,717 nodes total |
| CALLS edges | 7,577 (99.8 % `EXTRACTED`) | 33,361 (26,849 from SCIP) | 105,762 edges total |
| INHERITS / IMPLEMENTS | 1,112 / 122 | 3,107 / 9 | — |

### Locate (22 cases)

| Strategy | graphify | CGC Tree-sitter | CGC SCIP |
|---|---|---|---|
| raw CLI search | 0.302 | 0.279 | 0.252 |
| `find name` with graphify skill terms | 0.536 (`skill_q2`) | 0.253 | 0.248 |
| `find pattern` | 0.499 (`compound`) | 0.506 | 0.511 |
| 1-hop neighbourhood | 0.487 (`skill_both`) | 0.316 | 0.292 |
| Cypher 2-hop BFS | 0.536 (`skill_q2`) | 0.348 | 0.320 |
| **custom CGC skill script** | 0.536 (`skill_q2`) | **0.604** | **0.621** |
| `find content` (text control) | — | 0.394 | 0.456 |
| `find name` with oracle terms | 0.874 (oracle) | 0.488 | 0.440 |

- `cgc find name` matches the whole name within Levenshtein distance 2; identifier compounds (`orderreconciler`) rarely hit and `Variable` nodes flood the output. Even oracle terms reach only 0.44-0.49.
- `find pattern` matches graphify's compound strategy on score, but 35-39 % of its visible output is test/mock noise (graphify's filtered strategies: 0 %).
- The custom script wins on MRR (0.54-0.59 vs 0.45): substring match ranked exact > prefix > suffix > infix, types before members.
- Both tools fail the same three cases where the question words do not appear in code identifiers (≤ 0.11).

### Trace A→B (6 flow cases)

| Strategy | graphify | CGC Tree-sitter | CGC SCIP |
|---|---|---|---|
| CLI path (directed) | 0.075 | 0.300 (0/6 found) | 0.300 (0/6) |
| CLI path (undirected / both directions) | 0.176 | 0.300 (0/6) | 0.300 (0/6) |
| **best skill script** | **0.950** (6/6, via 0.83) | 0.359 (1/6, via 0.00) | 0.794 (6/6, via 0.58) |

CGC endpoints score 1.0 because its CLI strategies got exact symbol names; "found" and "via" are the fair comparison. On SCIP, the custom path script found every flow, but two flows that cross an event publisher went through shared exception/base-class hubs instead of the real hop (via recall 0).

### Agent in the loop (6 cases × 1 run)

A read-only code-search agent run headless through GitHub Copilot CLI, in a sandbox that offered only one skill: graphify's or CGC's (SCIP DB).

| Case shape | graphify score / recall | CGC score / recall |
|---|---|---|
| locate backend service (2 cases) | 0.91 / 1.00 | 0.96 / 1.00 |
| locate frontend component | 0.76 / 0.67 | 0.37 / 0.33 |
| locate cross-module reaction | 0.73 / 1.00 | 0.70 / 1.00 |
| flow REST API → task | 0.94 / 1.00 | 0.70 / 1.00 |
| flow domain event → handler | 0.66 / 0.67 | 0.53 / 0.67 |
| **mean** | **0.820 / 0.889** | **0.702 / 0.833** |

- Where the agent used CGC (backend locate cases), it beat graphify (best graph call 0.78-0.93 vs 0.69-0.72).
- In 3/6 cases it loaded the CGC skill, ran `cgc list`, then answered from docs and text search without a single graph query; answers stayed correct, the score dropped on the graph-call weight.
- The frontend case failed because SCIP output lacked the React components.
- Neither agent ever used a path command.

### Latency (median per call, in-process)

| Call | ms |
|---|---|
| `cgc find name` (fuzzy, Python-side scan of ~20k names on FalkorDB) | 500-1,000 |
| `cgc find pattern`, Cypher 1-2 hops | 25-35 |
| `cgc find content` | ~100 |
| `cgc analyze chain` | 15-20 |
| custom script after a ~1.5 s symbol load | < 1 |

Each CLI invocation an agent makes adds ~2 s Python/CGC start-up.

## CGC behaviour worth knowing

| Finding | Impact |
|---|---|
| FalkorDB Lite (embedded default) Linux wheels need glibc ≥ 2.39 (Ubuntu 24.04+); older hosts fall back to an sdist build that fails | install gate |
| CGC pins `protobuf<3.21`; overriding to protobuf 7 works for indexing, but the bundled `scip_pb2` needs `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` | SCIP fails silently to Tree-sitter otherwise |
| Per-repo context mode resolves from the **index path**: `cgc index <path>` creates `.codegraphcontext/` inside that root (writes into nested repos) | use a named context for multi-root indexing |
| `.cgcignore` is read only inside the index root (bounded by that root's `.git`) and auto-created if missing | a parent `.cgcignore` is ignored; symlink one in |
| When a local SCIP indexer fails, CGC silently tries Docker images; there is no switch to disable it | put a failing `docker` shim on `PATH` for reproducible runs |
| The index log does not print the SCIP language line at default log level | verify with `MATCH ()-[r:CALLS]->() WHERE r.source='scip' RETURN count(r)` |
| SCIP `CALLS` edges go `File → Function`, not `Function → Function`; members lose `class_context` (owner only in the docstring signature) | "who calls X" answers name files, not methods |
| scip-typescript output covers `function` declarations only; `const X = () =>` components disappear (79 vs 588 frontend functions) | React codebases lose most components |
| FalkorDB Cypher: no `=~`; `shortestPath` only inside `WITH`/`RETURN` and directed only | no undirected shortest path in Cypher |
| `cgc analyze chain` follows directed `CALLS` between named functions only | misses every DI/interface hop |
| Tree-sitter variant: no field or type-reference edges; interface calls mostly unresolved even with `ENABLE_INHERIT_RESOLVE=true` | Tree-sitter CGC unsuitable for DI-heavy C# flows |
| `cgc --version` prints to stderr when not attached to a TTY | scripts reading stdout get nothing |

## Recommendation

- Keep graphify as the default code-and-docs graph for agents.
- CGC with SCIP is worth adding only for exact "who calls X / what implements I" lookups, and only if the team accepts maintaining a SCIP pipeline (restorable `.sln`, installed frontend dependencies, ~8 min full reindex with no incremental refresh).
- Do not rely on CGC's built-in `find name` or `analyze chain` for agent navigation; a thin custom script over Cypher is required to be competitive.

## Limits

- One codebase; one agent run per case (noisy).
- graphify's corpus also covered extra frontend folders and docs; CGC indexed only the two code roots.
- CGC strategies were baselined untuned; the path hub penalty was the only design choice made after inspecting outputs.
- Neither tool links frontend HTTP calls to backend controllers.
