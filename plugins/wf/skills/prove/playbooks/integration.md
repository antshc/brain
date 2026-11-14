# Integration

Route procedure for SDK/API, cloud, broker, database or service behavior. Integration-test discovery and selection belong to `testing-integrations`; Prove owns the claim and the evidence conclusion.

## Workflow

1. **Select.** *Load and follow the `testing-integrations` skill to pick the minimal seam and prove it with evidence* using **Select**. Pass claim/criteria, actual boundary, pinned target, original launch/harness root, proof checkout, available runtime/services, supplied suite discovery, limits, output destinations and cleanup owner. Reuse a selection only while claim, revision, environment and suite facts remain applicable. *Done when* a fastest sufficient current-system path or explicit blocker is returned.
2. **Run selected.** A valid existing test path → *Load and follow the `testing-integrations` skill to pick the minimal seam and prove it with evidence* using **Run selected** with the returned selection/discovery. Preserve its preflight/cloud gates and narrow filter. *Done when* actual assertions, executed tests and summary establish the observation, or execution is blocked.
3. **Probe.** No suitable existing test → record why none settles the claim, then build the smallest authorized real-boundary probe: REST/cloud API → CLI; SDK semantics → real SDK with existing fixtures; broker → minimum producer/consumer processes; database → existing access stack and scratch data. Reuse repo scripts/orchestration; stub only irrelevant dependencies. Run it once. *Done when* one command exposes the deciding response/state/error.
4. **Capture.** Record selected seam, speed rationale, readiness prerequisites, rejected insufficient alternatives, command/working directory, real versus mocked dependencies, actual output and limits. *Done when* the result can be rerun from the record.

Return control for *Rerun*.

## Cloud and unavailable tools

- `testing-integrations` unavailable → report blocked integration selection; continue independent checks. Never silently copy its discovery/ladder or skip selection.
- Fallback cloud probe: reuse verified account/profile/subscription/region facts; verify active identity before operations. Do not install CLIs, log in, create credentials or reconfigure accounts for the proof.
- Keep mutations in authorized local/sandbox resources within caller limits. Record run-owned resources, costs and cleanup needs; broader writes need existing caller authorization.
- Filter/redact output to deciding fields. A mocked boundary or emulator cannot confirm real-provider semantics it does not exercise.
