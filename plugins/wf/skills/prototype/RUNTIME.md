# Runtime Prototype

Use when the uncertainty is in framework, process, backend/frontend runtime, OS, container, serialization, concurrency, lifecycle, or automation behavior rather than an external contract.

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
5. Stub external systems unless their real behavior is part of the question; then use [INTEGRATION.md](INTEGRATION.md).
6. Expose relevant inputs, state transitions, timing, output, exit codes, logs, or failures.
7. Run the smallest cases that prove or disprove the assumption.
8. Capture the observed behavior and discard the prototype shell.

## Constraints

- Do not redesign the production architecture.
- Do not add abstractions unrelated to the question.
- Do not turn the prototype into a production implementation.
