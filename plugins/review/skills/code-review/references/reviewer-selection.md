# Reviewer selection

Resolve before spawning. Prefer the runtime's available Rubber Duck agent for each axis; otherwise use a general read-only reviewer and record the fallback. Do not install or invent an agent. Fresh context per axis; the axis contract remains authoritative.

## Model routing

Count additions + deletions and changed files from the pinned diff. Exclude generated/vendor content from size counts, but inventory it and inspect runtime impact. Record exclusions. Count renames/binary changes as files; unavailable size or unclear complexity requires the strongest tier.

| Tier | Size floor | Complexity floor |
|---|---|---|
| Fast coding | ≤200 lines and ≤5 files | Local, straightforward behavior |
| Standard reasoning | 201–800 lines or 6–20 files | Cross-module behavior |
| Strongest reasoning | >800 lines or >20 files | Authentication/authorization, concurrency, transactions, migrations, public contracts, distributed state, recovery, destructive operations |

Highest matching floor wins. Large mechanical changes retain their size floor; record mechanical character separately. Complexity can only raise the tier. Use one PR classification for all eligible axes; model choice never reduces coverage/evidence requirements.

Resolve tier → concrete model ID from explicit caller/runtime configuration and the runtime's supported-model catalog. If no mapping exists, select supported models using advertised coding/reasoning capabilities; record the chosen mapping. Do not hard-code or invent IDs. When a tier is unavailable, prefer an available stronger tier; otherwise inherit the current model and disclose the limitation. If model selection is unsupported, inherit and record `model selection unsupported`.

Before delegation, record: reviewed SHA, counted lines/files, exclusions, complexity triggers, tier, agent, requested model, and selection rationale/fallback. Record actual model when exposed; never claim an unobservable selection took effect.
