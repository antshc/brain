# Mocking

## When to Mock

Mock at **system boundaries** only: external APIs, databases (prefer test DB), time/randomness, file system.

**Never mock** your own classes, internal collaborators, or anything you control.

## Designing for Mockability

1. **Use dependency injection** — pass external dependencies in via constructor, never `new` them internally
2. **Prefer SDK-style interfaces** — one method per operation (each independently mockable), not a generic `FetchAsync(endpoint, method, body)` that requires conditional mock logic

## Moq

- Use `MockBehavior.Strict` by default — unexpected calls throw, surfacing unintended interactions
- `Setup` + `ReturnsAsync` for happy paths
- `SetupSequence` for different values per call
- `ThrowsAsync` for simulating failures
- `Callback` for argument capture when you need to assert on what was passed
