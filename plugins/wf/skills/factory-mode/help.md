# Help Playbook

**Trigger:** Invocation args start with `help`. `help` alone → usage examples. `help <request>` → 3 ranked ways to run the request. Never edits files, runs playbooks, or calls other skills.

## help (no request)

Print the block below verbatim, then stop.

```text
/factory-mode <request>                  restate goal, pick a playbook, run it
/factory-mode help                       this help
/factory-mode help <request>             3 ranked playbook options for <request>, with reasoning; runs nothing

PLAYBOOKS — matched from the request
 investigation      read-only, cited answer or recommendation; no code
  /factory-mode how does <flow> work end to end
  /factory-mode are we sure <assumption> holds; should we use <X> or <Y>

 bug-fix            reproduce → binary-search root cause → fix → verify on same surface → draft PR
  /factory-mode fix <symptom> when <trigger>
  /factory-mode <Class.Method> throws <error> on <input>

 design             resolve unknowns (grill-design or wayfinder) → to-spec → to-zdesign; no code
  /factory-mode design <capability>; resolve open questions first
  /factory-mode we need <feature>, figure out the decisions

 architect          explore → architect sketch → to-spec → implement-spec → verify app → code-review → finalize draft PR
  /factory-mode add <behavior> to <module>
  /factory-mode implement <story> against an architect sketch

 architect auto     goal: deliver the entire feature autonomously, no questions after start
                    asks once: Initiative ID, target branch, repository
                    arena 3 agents → interrogate + prototype → to-spec → implement-spec
                    → verify app → code-review → address → diagnosing-bugs → finalize → show-me-your-work report
  /factory-mode auto: add <feature>, Initiative <PROJ-1234>, branch <main>, repo <owner/name>
  /factory-mode run until done: <feature>

 refactoring        pin behavior → subtract → reshape in green steps → prove unchanged
  /factory-mode extract <logic> from <Class> into <module>
  /factory-mode dedupe <helpers> across <area>

 prototype          throwaway sketch or experiment to settle a fork by observation
  /factory-mode prototype 2 layouts for <screen>
  /factory-mode does <library> handle <case>; try it

Principles, autonomy, subagent, and reply rules apply to every playbook.
```

**Done when:** block printed; nothing executed.

## help <request>

1. **Restate.** Goal, problem, and smallest change that meets it, in 2–3 lines. **Done when:** printed.
2. **Locate.** Light read-only scan: owning module, existing tests, matching `ARCHITECTURE.md` / `GLOSSARY.md` rows, open unknowns. Names via search only; no subagents. **Done when:** owning area named, or `unknown`.
3. **Build 3 options** from the Playbooks table, each a different playbook or mode (e.g. `architect` vs `architect auto`, `design` before `architect`, `prototype` first). **Done when:** 3 distinct options.
4. **Print**, per option:
   - **Option N — {{playbook}}** ({{mode}})
   - **Delivers / skips:** artifact produced (answer, spec, design, draft PR, decision) vs what it leaves out
   - **Skills called:** in order
   - **Needs:** inputs or access (Initiative ID, target branch, repository, cloud creds)
   - **Asks you:** when and what, or `none after start`
   - **Reasoning:** why this option fits the request
5. **Recommend** one option in one line with the deciding reason, then stop. Run nothing until the user picks. **Done when:** options + recommendation printed.

## Key Rule

Help is read-only. Print usage or options; execution waits for an explicit pick.
