# grill-design — SRP analysis and proposed breakdown

Scope: [grill-design/SKILL.md](../../plugins/wf/skills/grill-design/SKILL.md) (192 lines) and the skills it calls —
[manage-docs/SKILL.md](../../plugins/wf/skills/manage-docs/SKILL.md) (67), [trigger-indexer/SKILL.md](../../plugins/wf/skills/trigger-indexer/SKILL.md) (64), plus the `explore` subagent.

## Verdict

Both callees pass SRP. Each has one axis of change and an explicit ownership boundary —
`trigger-indexer` owns *table matching/sync* and disclaims ledgers, templates, and sweeps;
`manage-docs` owns *where docs live, what they look like, when they're created*.

`grill-design` is the violator: **six independent reasons to change** in one file, plus rules
copied down from its own callees.

## Responsibilities in grill-design

| # | Responsibility | Lines | Independent reason to change |
|---|---|---|---|
| 1 | Interview protocol (cadence, recommended answers, veto list, output format) | 8–24 | Facilitation UX changes |
| 2 | Decision taxonomy & lifecycle (evidence checklist, Feature Assumption / Feature Decision / Recorded) | 16–22, 81–85, 151–161, 183–191 | Taxonomy renamed or a fourth state added |
| 3 | Ledger storage schema (path, 3 sections, line formats, compaction) | 58–85 | Memory store or line format changes |
| 4 | Retrieval/caching policy (load order, touched-surface cache key, monotonic scan, re-fetch) | 40–56, 73–79, 113–115, 127–129 | A new indexed table type is added |
| 5 | Adjudication (conflict classes, source-authority precedence, drift) | 117–133 | Precedence order changes |
| 6 | Runtime/context-budget policy (`explore` delegation, `view`/`grep` reserve) | 91–93 | Agent tooling changes — unrelated to grilling |
| 7 | Doc-worthiness gates (ADR 3-test, Concept 3-test) | 163–181 | The bar for an ADR moves |
| 8 | External-source sync (Jira/Confluence/GitHub read **and write**) | 141–147 | Tracker is swapped |
| 9 | Domain probes (glossary, fuzzy terms, scenarios, test categories) | 95–111 | The interview's subject matter changes |

Only #1 and #9 belong to a skill named "grill-design".

## Defects this coupling already produced

1. **Broken internal cross-reference.** Line 56 points to *Continuously validate against Concepts and ADRs* —
   no such heading exists; it was renamed *Classify conflicts* (line 117). A rename in responsibility 5
   silently broke a pointer in responsibility 4.
2. **Ledger format specified twice.** The log-line grammar appears inside load step 3 (line 46) *and* at
   58–71. Two edit sites for one schema.
3. **Callee rules copied into the caller.** Line 155 restates `manage-docs`' *Keep each document in its lane*;
   `Lazy creation` is paraphrased five times (44, 151, 159, 171, 181). Contradicts
   [0006-terminology-consistency](../concepts/0006-terminology-consistency.md) — cite the rule by name once,
   never re-word it.
4. **Resource access inlined.** Lines 141–147 instruct the agent to "detect whether a write-capable tool for
   that source type is available" and write to Jira/Confluence/GitHub directly. Violates
   [0001-resource-access-skill](../concepts/0001-resource-access-skill.md); `manage-backlog` already exists
   for GitHub.
5. **Ledger duplicated against its own Concept.** [0002-ledger](../concepts/0002-ledger.md) declares Ledger a
   first-class crosscutting concept, yet its schema is defined only inside this one skill — so
   `grill-requirements` and `to-tickets` cannot reuse it without copy-paste.
6. **Double-wide trigger surface.** The frontmatter description promises both "get grilled" *and* "record an
   architectural decision", so the skill fires — dragging the whole 192-line interview protocol into context —
   for requests that only wanted a doc write.

## Proposed breakdown

Split by *reason to change*, not by the old grilling / domain-modeling seam. That seam was false: the
interview's veto list (line 20) is the write trigger for the durable docs (line 185), and the ledger holds the
interview's output. Follow the pattern `manage-docs` already uses — `SKILL.md` plus `*-FORMAT.md` reference
files loaded on demand.

```
plugins/wf/skills/grill-design/
  SKILL.md                 ~55 lines — interview loop, probe list, dispatch to the files below
  DECISION-LIFECYCLE.md    resp. 2 + 7 + the veto/closing sweep
  GUARDRAILS.md            resp. 4 + 5 (load -> match -> classify, precedence, re-fetch)
```

### Extractions

| Move | Target | Reasoning |
|---|---|---|
| Ledger schema (resp. 3) | new `manage-ledger` skill | It is a store with an interface (append opened record / append surface term / stage decision / resolve). Concept 0002 already names it; other grill-* skills need it; `trigger-indexer` explicitly disclaims it, so today nobody owns it. |
| External-source sync (resp. 8) | `manage-backlog` + a one-line "surface the contradiction, then delegate the fix" rule | Concept 0001. Removes tracker-specific knowledge from a design skill. |
| `explore` delegation + re-fetch rule (resp. 6) | shared instructions file (e.g. `.github/instructions/context-budget.instructions.md`) | Runtime-coupled, skill-agnostic, already needed by other grill-* skills. |
| Touched-surface cache semantics (part of resp. 4) | fold the *monotonic* rule into `trigger-indexer` **Scan and match** | Whether a re-scan is needed is a property of the matcher, not the interviewer. The caller then just passes new surface terms. |

### Deduplication (applies with or without the file split)

- Delete the ledger grammar at line 46; cite *Track opened records* by name.
- Delete line 155; replace the five `Lazy creation` paraphrases with one sentence in *Managing the docs*:
  creation, placement, and lane rules are `manage-docs`' — never restate them.
- Fix the dangling cross-reference at line 56 -> *Classify conflicts*.
- Narrow the frontmatter description to the interview trigger only; let doc-only requests route to
  `manage-docs`.

## Expected effect

`grill-design` drops to roughly a third of its size for the common turn, each rule gets exactly one edit site,
and the three cross-skill boundaries (docs / index / ledger) become symmetrical — each callee owning one store
with a declared `Ownership` section, as `trigger-indexer` already does.

## Suggested sequencing

1. Low-risk, no structural change: defects 1–3 plus the description narrowing.
2. Extract `DECISION-LIFECYCLE.md` and `GUARDRAILS.md` (mechanical move, no wording change).
3. Extract `manage-ledger`; update `grill-design` and `grill-requirements` to call it.
4. Route external-source writes through `manage-backlog`.
5. Move the `explore`/re-fetch policy to a shared instructions file.
