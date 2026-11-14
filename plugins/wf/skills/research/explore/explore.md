# Explore

Route procedure for codebase exploration a calling agent needs as working evidence, like a built-in explore agent: find files or code, where is X, who calls Y, what does Z return, which implementation runs, how modules connect, a restored package API, a graph query or path. Spawns `hunty`; returns its findings inline to the requester. No explanation report, no file.

## Workflow

1. **Frame.** One Brief per independent question; keep literal and symbol spelling and everything the requester said it needs. Fill the `hunty` Brief: `@work` = the lookup (a flow names both ends) with the named repository/deployable/checkout and the requester's return shape; `@research` = this skill's absolute base directory. *Done when* every lookup has a Brief.
2. **Spawn.** Spawn one `hunty` per lookup in one parallel batch; sequence lookups that need an earlier answer. *Done when* every lookup returned a verdict or a blocker.
3. **Return.** Return each verdict inline as-is, unabridged: `route:` line, answer, findings with absolute `path:line` citations and excerpts, graph commands or skip reason, `NOT FOUND` with searched roots, blockers. Spot-check a deciding citation only when two verdicts conflict; report the conflict rather than resolving it with a narrative. *Done when* the requester has every verdict.

The requester wants an explained, saved report of a mechanism, flow, or inspection → use How instead.
