# graphify-path route

Two named or describable ends with a covering graph: "how does A reach B", "flow from A to B", "end to end", handoff. Uses the already-loaded graphify.md.

1. `$GRAPH resolve` both ends to exact labels before any `query` or `rg`.
2. `$GRAPH path <A> <B>`; add `--directed` when call direction matters.
3. Walk each hop in source, including interface dispatch and DI binding; cite each hop with `path:line`.
4. Path ends at an interface or is missing → trace the binding through LSP and source.
5. A hop through a DTO, exception, or base class is a shortcut → `$GRAPH query <hop> --anchor --both` for the real neighbor.
6. Reject an undirected path bridged only by a generic contract, test base, or generated node (graphify.md Path between two nodes); continue with LSP call hierarchy from A.
7. Cross-deployable hop → name sender, wire contract, receiver, and deployment/config binding; matching names alone leave the crossing unconfirmed.
