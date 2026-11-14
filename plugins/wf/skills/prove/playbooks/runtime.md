# Runtime

Route procedure for how a framework, runtime, hosting model, middleware pipeline, lifecycle, concurrency model, serializer, OS, container, process or automation mechanism behaves. Typical claims: ASP.NET Core middleware exception handling, DI scope/disposal, request cancellation, BackgroundService shutdown, serializer behavior, routing/filter/middleware ordering.

## Workflow

1. **Reuse.** Take runtime, framework, packages, hosting model, scripts and container setup from the Frame's Facts; read only gaps. *Done when* the stack is cited or a gap is named.
2. **Build.** Isolate the mechanism in the smallest runnable artifact: console/CLI app, minimal web app, script, test host, container/Compose setup, or minimal set of cooperating processes. Use the real framework/runtime mechanism; stub irrelevant external systems. Expose relevant inputs, state transitions, timing, output, exit codes, logs or failures. *Done when* one command exercises the mechanism.
3. **Run.** Execute the smallest cases that prove or disprove the assumption. *Done when* observed behavior per case is captured.

Retain the experiment shell until the caller finishes verification and requested follow-up. Return control for *Rerun*.

## Constraints

- Do not redesign the production architecture.
- Do not add abstractions unrelated to the claim.
- Do not turn the experiment into a production implementation.
