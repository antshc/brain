# {{scenarioSlug}} — scenario log

<!-- @: problems faced and their solutions only; append each bullet once solved or blocked, before the next action -->

## Draft

<!-- @: group under `### <draft step>` when a step applies; omit section when Draft had no problems -->

- **Problem:** {{problem|what went wrong or was missing}} → **Solution:** {{solution|what changed in the scenario file and why}}

## Run {{runNumber}} — {{date}}

<!-- @: one section per run, appended; keep earlier runs unchanged -->

### {{stageName|Preflight, Prerequisites, Build broken state, Reproduce, Apply remediation, Validation, Cleanup}}

<!-- @: one subsection per stage that hit a problem; omit stages without problems -->

- **Problem:** {{problem|failing command, compile error, or signal line, redacted}} → **Solution:** {{solution|scenario/code change made; stages re-run}}
- **Problem:** {{problem}} → **Unblocker:** {{unblocker|what is needed to continue}}
