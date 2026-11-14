# Help Playbook

**Trigger:** Invocation args start with `help`. `help` alone → usage examples. `help <request>` → 3 ranked ways to run the request. Never edits files, runs playbooks, or calls other skills.

## help (no request)

Print the block below verbatim, then stop.

```text
/factory-mode <request>                  restate goal, pick a playbook, run it
/factory-mode help                       this help
/factory-mode help <request>             3 ranked playbook options for <request>, with reasoning; runs nothing

PLAYBOOKS — matched from the request
 bug-fix            reproduce → binary-search root cause → fix → verify on same surface → draft PR
  /factory-mode fix <symptom> when <trigger>
  /factory-mode <Class.Method> throws <error> on <input>

 design             resolve unknowns; /design wayfinder maintains HLD automatically, or /design grill → requested spec/HLD; no code
  /factory-mode design <capability>; resolve open questions first
  /factory-mode we need <feature>, figure out the decisions

 stories            normalize requirements → approve breakdown → draft ordered User stories with Jira metadata
  /factory-mode stories from <requirements or spec>
  /factory-mode break <feature design> into User stories

 review             /review code publishes → read comments → /prove claims → reply with evidence; resolve false positives
  /factory-mode review https://github.com/owner/repo/pull/123
  /factory-mode review this PR and prove its published comments

 feature            research → architect sketch → resolve questions → /design spec → implement parallel → verify app → Review playbook → /review comments → finalize draft PR
  /factory-mode add <behavior> to <module>
  /factory-mode add <feature>, Initiative <PROJ-1234>, branch <main>, repo <owner/name>
  /factory-mode add <feature> checkpoint  (pause for design approval)

Read-only questions and behavior-preserving refactors use the no-playbook fallback.
Research and Prove own research and empirical verification.

Principles, autonomy, subagent, and reply rules apply to every playbook.
```

**Done when:** block printed; nothing executed.

## help <request>

1. **Restate.** Goal, problem, and smallest change that meets it, in 2–3 lines. **Done when:** printed.
2. **Locate.** Light read-only scan: owning module, existing tests, matching `ARCHITECTURE.md` / `GLOSSARY.md` rows, open unknowns. Names via search only; no subagents. **Done when:** owning area named, or `unknown`.
3. **Build 3 options** from the Playbooks table, each a different playbook or approach (e.g. `design` before `feature`, `feature` directly, `stories` for planning-only work). **Done when:** 3 distinct options.
4. **Print**, per option:
   - **Option N — {{playbook}}** ({{approach}})
   - **Delivers / skips:** artifact produced (answer, spec, design, draft PR, decision) vs what it leaves out
   - **Skills called:** in order
   - **Needs:** inputs or access (Initiative ID, target branch, repository, cloud creds)
   - **Asks you:** required inputs and any explicitly requested checkpoint, or `none`
   - **Reasoning:** why this option fits the request
5. **Recommend** one option in one line with the deciding reason, then stop. Run nothing until the user picks. **Done when:** options + recommendation printed.

## Key Rule

Help is read-only. Print usage or options; execution waits for an explicit pick.
