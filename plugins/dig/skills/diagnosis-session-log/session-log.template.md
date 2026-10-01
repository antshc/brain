# Diagnosis Log: {{bugTitle}}

## Summary

- Symptom: {{user's description, verbatim}} → captured: `{{exact error, wrong output, or timing}}`
- Environment: {{runtime, config, dataset}}
- Commit: `{{git rev-parse HEAD}}` on `{{branch}}`
- Setup: `{{commands a fresh session runs before the loop}}`
- Status: reusing-prior | building-loop | reproducing | hypothesising | instrumenting | confirming | root-cause-found | fixing | done | blocked
- Correct hypothesis: {{H-number — one line, or —}}
- Next step: {{exact next action so a fresh run starts here}}

## Artifacts

- `{{path[:line]}}` — {{harness | fixture | trace | instrumentation | test | fix}}: {{purpose}} — {{present | removed | moved to `path`}}

## Investigation

<!-- @: one `### {{phase name}}` per phase the run actually enters, in order; omit phases never reached -->
<!-- @: bullet IDs, consecutive across resumes: C prior handoff, L loop attempt, H hypothesis, P probe, T test run, F fix, K cleanup -->
- {{ID}} {{event}} — {{evidence: command → redacted signal line, or `path:line`}} — {{outcome}}
