# graphify-find route

Unknown names with a covering graph: "which service does X", concept → code, "which modules", architecture, doc ↔ code. Uses the already-loaded graphify.md.

1. Translate the question into code vocabulary through `GLOSSARY.md` and `GRAPHIFY.md` search vocabulary when present.
2. `$GRAPH terms "<question>"`; keep suggestions with small hit counts that name the concept.
3. `$GRAPH query` with the top 1-2 identifier terms, never the question text (graphify.md Focused search, search-term rules).
4. Open the top production hits in source; confirm ownership from registration, startup, or deployment evidence.
5. Empty or noisy results → `rg` on the glossary terms and code-shaped guesses; report the graph gap.
