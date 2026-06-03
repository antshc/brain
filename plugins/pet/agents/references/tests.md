# Tests

## Rules

- Test through public API only — verify WHAT, not HOW
- Mock at system boundaries only: external APIs, databases, time/randomness, file system
- Never mock your own classes, internal collaborators, or anything you control
- Use dependency injection for external dependencies; do not `new` them internally
- Prefer SDK-style interfaces: one method per operation
- Use `// Arrange`, `// Act`, `// Assert` comments to separate test phases
- One logical assertion per test
- Verify by calling back through the same interface, not inspecting internals
- SUT: create in constructor via `new`. Use factory method when config varies per test
- Mocks: wrap setup in named helper methods when reused across tests (`SetupReadMock(arg1, arg2)`)
- Use `MockBehavior.Strict` by default — unexpected calls throw
- Use `Setup` + `ReturnsAsync` for happy paths
- Use `SetupSequence` for different values per call
- Use `ThrowsAsync` for simulating failures
- Use `Callback` for argument capture when needed
- No `if` in tests — exception: reducing excessive duplication
- Name describes observable behavior, not implementation mechanism (`Read_ThrowsCircuitOpenException_AfterRepeatedTransientFailures`)

## Red Flags

- Mocking internal collaborators
- `Times.Exactly(N)` / call-count assertions
- Testing private methods
- Verifying via DB/state inspection instead of public API
- Test breaks on refactor with no behavior change
