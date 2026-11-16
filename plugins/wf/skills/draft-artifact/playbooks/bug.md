# Bug

Draft and print one standalone bug report that defines the affected behavior, reproduction, actual result, expected result, and useful technical context.

## Inputs

 observed behavior and any available affected users, expected behavior, impact, boundaries, preconditions, reproduction steps, evidence, and technical context. Derive omitted details from the conversation and repository when evidence is available.

## Required resources

Read the router's Bug template and shared requirements resources; apply normalization only to authored expected behavior and definition of fixed. Preserve exact reproduction, observed labels, errors, identifiers and evidence.

## Workflow

1. **State the impact** → state the affected behavior or users, expected versus actual behavior, impact on users and the system, boundaries, and definition of fixed. *Done when* the Impact identifies one observable defect without prescribing an implementation or unverified root cause.
2. **Sweep context** → inspect the nearest relevant documentation, tests, configuration, logs, errors, and implementation surfaces when repository access can clarify the report. When the evidence path is unclear, spawn a built-in `explore` subagent with a bounded, read-only lookup and the facts to return with `path:line` evidence. Blocked lookup → record it and continue drafting from available evidence. Stop once the report fields can be stated accurately; root-cause analysis is outside this skill. *Done when* every included technical claim is grounded in supplied or observed evidence and remaining unknowns stay explicit.
3. **Write reproduction** → list only required preconditions, then numbered user actions from the starting state to the observed result. *Done when* another person can attempt the reproduction without inferring setup or intermediate actions.
4. **Separate results** → state the observed outcome under Actual Results and the required behavior under Expected Results. *Done when* the two results are directly comparable and use concrete, testable language.
5. **Verify** → apply Completion criteria line by line. *Done when* every check passes and the report contains no invented facts.

## Completion criteria

- The Impact covers affected behavior or users, expected versus actual behavior, impact on users and the system, boundaries, and the observable definition of fixed.
- The Impact is prose in business language: business terms, cloud resources, public contracts (REST endpoint, event names), page names, and user-visible page elements are allowed; class, method, or variable names, file paths, and internal component names are not.
- Preconditions contain only state or setup required before the first action.
- User Actions are ordered, reproducible actions and contain no expected outcomes.
- Actual Results report observations, including exact error text or identifiers when available.
- Expected Results define one externally verifiable outcome.
- Technical notes contain only useful known evidence, references, environment details, explicit unknowns, or a root cause; they do not speculate about an unverified root cause.
- Unknown required details are marked `Unknown` rather than invented.


## Update behavior

Preserve observations and technical evidence; distinguish new evidence from prior observations. Leave missing facts Unknown.

## Output

Return one Bug template body without wrapper prose.
