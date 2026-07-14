# LSP Summary Output

Record the shared **LSP baseline** pass (Step 5) as a single **LSP summary** shared with every sub-agent. It is the only artifact the axes see from that step, so it must be uniform and auditable. It captures cheap facts gathered once — a per-symbol contract snapshot plus one relationship sweep (representative callers, fan-out counts, affected overrides). Each axis escalates from there to Level 2/3 as directed by the **LSP focus** section in its own reference file.

One row per changed symbol:

| Symbol | Contract (before → after) | Nullability | Callers (representative) | Fan-out (files/callers) | Overrides? | Risk flag |
|--------|---------------------------|-------------|--------------------------|-------------------------|------------|-----------|

The columns are axis-neutral facts — record **all** of them regardless of which axis will consume them. Each axis decides which columns it starts from in its own **LSP focus** section.

Close with a **Risk flags** list naming only the symbols that carry a risk signal (contract change, new nullability, changed behavior, wide fan-out, shared/async state) and a one-word reason, so the axes know where to focus.

Rules:
- One row per changed symbol — no symbol silently omitted.
- Keep cells terse; cite representative callers, not exhaustive lists.
- Record fan-out as counts (e.g. `3 files / 7 callers`), not a full list.
- Mark the risk flag as `none` / `low` / `high` with a short reason.
