# .crew/

Harness files for coding agents working in this repo. Resolved via the nearest ancestor `.harness.env` (see [`../.harness.env`](../.harness.env)), which maps each path to a file here:

| Path var | File | Purpose |
|---|---|---|
| `CODE_PATH` | [CODE.md](CODE.md) | Coding/test conventions for production C# code and tests. Read during implementation. |
| `VERIFY_PATH` | [VERIFY.md](VERIFY.md) | Always-on feedback loop (diagnostics → build → unit tests → mock-sanity), run after any change. |
| `MEMORY_PATH` | [MEMORY.md](MEMORY.md) | Curated guardrails, distilled by a human from recurring `LOG.md` entries. Read-only for agents. |
| `LOG_PATH` | [LOG.md](LOG.md) | Append-only problem log, written by agents at the end of a session. |

These files are conventions, not tool-specific — any agent that resolves `.harness.env` can use them, not just one particular assistant.
