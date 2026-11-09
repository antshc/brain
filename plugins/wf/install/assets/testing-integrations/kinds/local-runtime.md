# Local Runtime Playbook

**Kind:** run a local instance of the application (local stack: app services + emulated dependencies + UI) and test it from outside like a user, without the integration testing framework (that is `functional-slice` kind). Ladder rungs 6–7: REST API first, web GUI last.

**Trigger:** Real user behavior must be shown on a running app and no lower rung (component, functional-slice incl. real cloud) can show it; or the user asks for the running app.

## Steps

1. **Find the local-run path.** From Discover `localInstance`: doc or skill that starts the local stack, its health/status command, endpoints (API, UI, dashboards), logs, and stop command. Prefer a repo skill that drives the stack; invoke it by name. **Done when:** start, health, stop, endpoints cited.
2. **Preflight.** Run its environment checks (doctor / container daemon / ports / built artifacts). **Done when:** checks OK.
3. **Start + health.** Start the stack; poll health/status until every required service is up. **Done when:** health green, endpoints reachable.
4. **Exercise.** REST API first: `curl` / repo HTTP files against the documented endpoints. Web GUI only when the behavior is UI-only or the visible GUI outcome is the question: repo browser-automation skill or scenario runner. One behavior per run. **Done when:** request/scenario executed.
5. **Observe.** Capture the evidence: response body/status, UI state or screenshot/receipt, log lines, persisted record. **Done when:** evidence saved with path or quoted.
6. **Stop.** Stop the stack unless the user wants it kept. **Done when:** status shows down, or kept by request.

## Key Rule

Last rung. REST before GUI. Evidence comes from the running app, not from reading code. Health green before exercising; artifact (response, receipt, log line) for every claim.
