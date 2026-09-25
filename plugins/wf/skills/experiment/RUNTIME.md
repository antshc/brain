# Runtime Experiment

Use when the uncertainty is how a framework, runtime, hosting model, middleware pipeline, lifecycle, concurrency model, serializer, OS, container, process, or automation mechanism behaves. Build the smallest executable application that reproduces the mechanism.

Typical questions include ASP.NET Core middleware exception handling, DI scope/disposal, request cancellation, BackgroundService shutdown, serializer behavior, and routing/filter/middleware ordering.

## Build

1. Inspect the repository and reuse its runtime, framework, packages, hosting model, scripts, and container setup.
2. Isolate the mechanism under test.
3. Choose the smallest runnable artifact:
   - console/CLI app
   - minimal web app
   - script
   - test host
   - container/Compose setup
   - minimal set of cooperating processes
4. Use the real framework/runtime mechanism being evaluated.
5. Stub irrelevant external systems. When the experiment also crosses a real external boundary, apply [INTEGRATION.md](INTEGRATION.md) in addition.
6. Expose relevant inputs, state transitions, timing, output, exit codes, logs, or failures.
7. Run the smallest cases that prove or disprove the assumption.
8. Capture the observed behavior and discard the experiment shell.

## Constraints

- Do not redesign the production architecture.
- Do not add abstractions unrelated to the question.
- Do not turn the experiment into a production implementation.
