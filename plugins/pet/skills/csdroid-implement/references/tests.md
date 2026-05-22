# Tests

## Rules

- Test through public API only — verify WHAT, not HOW
- Use `// Arrange`, `// Act`, `// Assert` comments to separate test phases
- One logical assertion per test
- Verify by calling back through the same interface, not inspecting internals
- SUT: create in constructor via `new`. Use factory method when config varies per test
- Mocks: wrap setup in named helper methods when reused across tests
- No `if` in tests — exception: reducing excessive duplication
- Name describes observable behavior, not implementation mechanism

## Names Conventions

- `Read_ThrowsCircuitOpenException_AfterRepeatedTransientFailures` — Test method name describing observable behavior
- `SetupReadMock(arg1, arg2)` — Setup Method mock, configures mock for list of items returned by read method

## Red Flags

- Mocking internal collaborators
- `Times.Exactly(N)` / call-count assertions
- `MockBehavior.Strict`
- Testing private methods
- Verifying via DB/state inspection instead of public API
- Test breaks on refactor with no behavior change
