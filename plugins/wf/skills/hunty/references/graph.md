# Graph routes: graphify-find, graphify-path, impact

Search an existing `<graph root>/graphify-out/` graph read-only through `@hunty/scripts/graph.py`. The graph root is the harness root (`git rev-parse --show-toplevel` from the launch folder); run from there, never from a `workspace/<repo>` checkout or a worktree, and never probe those for their own `graphify-out/`.

## Contents

- Rules
- Setup and health
- Commands
- Search terms
- Route graphify-find
- Route graphify-path
- Impact
- Gotchas

## Rules

- Search only. Never build, `--update`, re-cluster, `save-result`, add, watch, export, feedback, or run `graphify reflect`; read `graphify-out/reflections/LESSONS.md` if present and skip known dead ends. Build requests → report the entry point named in `GRAPHIFY.md`.
- Pass 1-2 identifier terms to `query`, never question text; `terms` takes the question.
- The graph reflects the main checkout at build time; source wins. A missing node is never absence evidence. Cite source files, not graph nodes.
- Worktree target → translate graph paths from `@mainCheckout/…` to `@worktreeRoot/…` before reading source.
- Record graph freshness and target coverage separately from the reviewed checkout's revision or dirty state. Stale or revision-mismatched graphs supply candidates only.
- `graph.py` exits `3` (missing module) and install per Gotchas fails → return control to the hunty router for *Route the lookup*, graph fallback row.

## Setup and health

```bash
GRAPH="$(cat graphify-out/.graphify_python 2>/dev/null || echo python3) @hunty/scripts/graph.py"
$GRAPH check
```

1. Read `<graph root>/GRAPHIFY.md` in full when present; its corpus, exclusion, vocabulary, and degraded-mode rules override this file.
2. `$GRAPH check` compares `built_at_commit` with the root's `HEAD` and lists corpus roots and noise (`.artifacts/`, `bin/`, `obj/`, `TestResults/`, `review_diff/`). Exit `1` → graph missing: report it and continue without the graph.
3. Print one health line before the first query: corpus coverage, freshness (`current | stale | unknown`), material noise. Missing coverage or stale → graph is candidate discovery only; verify in source.

## Commands

`--graph PATH` selects another graph. Focused commands (`terms`, `query`, `resolve`, `path`, `affected`) need the `graphify` module and exclude tests, `*deprecated*` folders, generated/build output, `graphify-out/`, `mocks/`/`mocker/`, manifests, namespace and solution nodes, and sourceless external types; pass `--keep test` when the question is about tests.

| Command | Use |
|---|---|
| `terms "<question>"` | Candidate terms: question words joined into compounds the graph contains, longest first, with label hit counts. |
| `query <T1> [<T2>]` | BFS depth 2 from the best match of each term. `--anchor` seeds only the top match; `--both --anchor` lists 1-hop callers and callees; `--context call` filters edges. |
| `resolve "<Label or phrase>"` | Exact class label first, then best compound match; returns `label file:line`. |
| `path <A> <B>` | Shortest path on the focused graph; `--directed` for dependency direction; drops import edges by default. |
| `affected <Symbol>` | Reverse dependency edges from a symbol or node ID; depth defaults to two; repeat `--relation` to select edge types. |
| `slice <Label> --direction in\|out\|both` | Stdlib raw-edge slice; `--source-contains` disambiguates duplicate labels. |

Truncated output (`[!] TRUNCATED`) → narrow the term or add `--anchor`; do not raise `--budget` first.

## Search terms

- Run several small 1-2 term queries rather than one long one; every extra term seeds its own flood.
- Translate question words into code names: CamelCase domain + role compounds (`OrderJanitor`, `InvoicePaid`), using `GRAPHIFY.md` vocabulary and role suffixes such as `Controller`, `Manager`, `Task`, `HostedService`, `BackgroundService`, `Middleware`, `Repository`, `Converter`, `Facade`, `Validator`, `Invoker`, `Events`, `Accessor`.
- Keep a `terms` suggestion only when its hit count is small (roughly under 50) and it names the concept; check own guesses with `terms`/`resolve`.
- Drop question words (`how`, `flow`, `explain`, `each`, `old`, `request`) and generic singles (`service`, `manager`, `api`, `task`, `status`, `configuration`).

## Route graphify-find

Unknown names: "which service does X", concept → code, "which modules", architecture, doc ↔ code.

1. Translate the question through `GLOSSARY.md` and `GRAPHIFY.md` vocabulary.
2. `$GRAPH terms "<question>"`, then `$GRAPH query` with the top 1-2 identifier terms per Search terms.
3. Known symbol among hits → `$GRAPH query <Symbol> --anchor --both` for callers and callees.
4. Architecture or doc questions need document nodes in the corpus; a code-only graph cannot settle them.
5. Open the top production hits in source; confirm ownership from registration, startup, or deployment evidence.
6. Empty or noisy results → `rg` on glossary terms and code-shaped guesses; report the graph gap.

## Route graphify-path

Two named or describable ends: "how does A reach B", "flow from A to B", "end to end", handoff.

1. `$GRAPH resolve` both ends to exact labels before any `query` or `rg`.
2. `$GRAPH path <A> <B>`; add `--directed` when call direction matters.
3. Walk each hop in source, including interface dispatch and DI binding; cite each hop with `path:line`. Interface hops (`Caller → IFoo ← Foo`) are real dependencies: trace the binding through LSP and source.
4. A hop through a DTO, exception, or base class is a shortcut → `$GRAPH query <hop> --anchor --both` for the real neighbor.
5. Reject a path bridged only by a generic contract (`IDisposable`, `IEquatable`, `Object`), a test base, or a generated/snapshot node; continue with LSP call hierarchy from A. A shortest path is not evidence of an architectural relationship.
6. Cross-deployable hop → name sender, wire contract, receiver, and deployment/config binding; matching names alone leave the crossing unconfirmed.
7. Return ordered hops with `path:line`, rejected paths with reasons, and the commands run.

## Impact

Run after LSP references (search.md Impact step 1).

```bash
$GRAPH affected OrderService --depth 2
$GRAPH affected OrderService --depth 1 --relation calls --relation references
```

- Seed the changed member or interface member; use the declaring type for type-wide changes or when the graph omits the member. Raise depth only for a specific cross-boundary question.
- Exit `5` lists ambiguous matches with IDs → retry with a qualified symbol or exact ID. Exit `4` → missing seed. Zero dependents → none within the selected graph, depth, and relations.
- Focused command unavailable → `$GRAPH slice <Label> --direction in --depth 1`.
- Verify material hits in source; empty, unresolved, or stale results continue with LSP and targeted `rg`.

## Gotchas

- `ModuleNotFoundError` for `graphify`/`networkx` → `<interpreter> -m pip install -r @hunty/scripts/requirements.txt` with the graph interpreter, once; rerun. **MUST NOT** upgrade or unpin versions.
- `graphify query | path | explain` may update `graphify-out/cache/`; that is the only permitted write.
