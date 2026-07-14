# LSP Summary Output

Record the LSP analysis pass as a single **LSP summary**. In spawned mode it is supplied in
the input payload; in standalone mode you produce it. It must be uniform and auditable.

One row per changed symbol:

| Symbol | Contract (before → after) | Nullability | Callers (representative) | Fan-out (files/callers) | Overrides? | Risk flag |
|--------|---------------------------|-------------|--------------------------|-------------------------|------------|-----------|

The columns are axis-neutral facts:
- **Contract, Nullability, Overrides** — broken assumptions, missing guards, contract drift.
- **Fan-out** — wide spread hints at scattered impact. Record how many files and callers the symbol reaches.
- **Callers (representative)** — trace whether the changed behavior is actually wired to its callers.

Close with a **Risk flags** list naming only the symbols that carry a risk signal (contract
change, new nullability, changed behavior, wide fan-out, shared/async state) and a one-word reason.

Rules:
- One row per changed symbol — no symbol silently omitted.
- Keep cells terse; cite representative callers, not exhaustive lists.
- Record fan-out as counts (e.g. `3 files / 7 callers`), not a full list.
- Mark the risk flag as `none` / `low` / `high` with a short reason.
