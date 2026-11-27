# How orchestration evaluations

`how-scenarios.json` covers discovery, cross-repository evidence, package implementation, terminal/access gaps, provider/data uncertainty, and report delivery (session workspace default, requested locations). These complement the codebase routing cases in `tests/wf/codebase/evals/`; offline contract tests validate structure, not model behavior.

Run each request in a fresh session with the Research skill and the caller context named in the case. Supply a representative read-only checkout or captured evidence when needed. Apply `commonChecks` plus each case’s checks to the transcript, requested writes, and produced explanation. Record the tested revision, supplied context, outcome, and evidence limits; do not report an unexecuted case as passed. For an explanation-only check, supply the findings directly and apply How report.
