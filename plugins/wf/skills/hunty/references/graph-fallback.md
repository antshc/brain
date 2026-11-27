# Graph fallback

Read only when `graph.py` focused commands cannot run (exit `3`, missing `graphify` module) and the requirements install failed. Uses the `$GRAPH` setup and Rules from the already-loaded graph.md; stdlib commands (`check`, `contexts`, `vocab`, `slice`, `traverse`, `raw-path`, `explain`) still work. Order: `graphify` CLI when installed, else `$GRAPH` stdlib commands. Never save results back.

## Contents

- Query expansion
- Traversal
- Path
- Explain one node

## Query expansion

The CLI and stdlib matchers use case-folded substring + IDF: no stemming, synonyms, or cross-language match. Expand against the graph vocabulary before any traversal:

1. `$GRAPH vocab` prints node-label tokens.
2. Select up to 5 tokens (3 for a symbol-oriented query) from that exact list matching the question intent:
   - **MUST** pick only tokens present in the `vocab` output; never invent tokens or substitute near-synonyms.
   - Prefer tokens from the exact symbol or path over `service`, `manager`, `result`, `configuration`, `test`.
   - Map morphology and other languages only to tokens present (`handlers` → `handler`; `аутентификация` → `auth`, `credential`, `token`).
   - Skip both singular and plural unless they name different labels.
3. Print `Query expanded to (from graph vocab, N tokens): [token1, token2, ...]`. Empty list → report that the corpus has no relevant vocabulary and stop graph work.

## Traversal

Use the space-joined expanded tokens as `QUESTION`, never the original question.

```bash
graphify query "QUESTION"                         # CLI; add --dfs --budget 3000 for chains
$GRAPH traverse QUESTION                          # stdlib BFS, depth 2
$GRAPH traverse QUESTION --dfs --budget 3000      # stdlib DFS, depth 6
```

Precision ladder; a broad query is discovery, not the answer:

1. Run the expanded query once to find candidate anchors.
2. Pick one exact live-source symbol (`graphify explain` or `$GRAPH explain`): exact label with all discriminating terms, production source over tests, generated artifacts, snapshots, and copies.
3. Rerun from that label. Add `--context` only when the question needs one edge context; `--context` matches the edge `context` field (`call` → `calls` edges; `field`, `parameter_type`, `return_type` → kinds of `references`). List valid contexts with `$GRAPH contexts`; anchor on the method before `--context call`.
4. More than 100 nodes or truncated → move down the ladder, never raise the budget first. After anchoring and filtering, one larger-budget retry is allowed under 100 nodes. Still too broad → report it and use LSP or `rg`; never present a truncated traversal as an answer.
5. Second hop fans out through a shared dependency → `$GRAPH slice EXACT_SYMBOL --relation references --direction out --depth 1`; add `--source-contains <path fragment>` for duplicate labels, `--direction in|both` for callers. Raise depth only for an explicitly transitive question.

Answer only from the subgraph: node labels, relations, confidence tags, and `source_location`; then confirm in source. Missing information → say so; never invent edges.

## Path

Resolve both endpoints to exact labels with `explain` first, then:

```bash
graphify path "NODE_A" "NODE_B"
$GRAPH raw-path "NODE_A" "NODE_B"     # stdlib; add --undirected only when direction is irrelevant
```

Apply graph.md Route graphify-path steps 3-7 to the result.

## Explain one node

```bash
graphify explain "NODE_NAME"
$GRAPH explain "NODE_NAME"            # stdlib
```

Report what the node is, what it connects to, and why those connections matter, citing `source_location` and confirming deciding facts in source.
