# Tests

## Rules

- Test through public API only — verify WHAT, not HOW
- Use `// Arrange`, `// Act`, `// Assert` comments to separate test phases
- One logical assertion per test
- Verify by calling back through the same interface, not inspecting internals
- SUT: create in constructor via `new`. Use factory method when config varies per test
- Mocks: wrap setup in named helper methods when reused across tests (`SetupReadMock(arg1, arg2)`)
- No `if` in tests — exception: reducing excessive duplication
- Name describes observable behavior, not implementation mechanism (`Read_ThrowsCircuitOpenException_AfterRepeatedTransientFailures`)

## Red Flags

- Mocking internal collaborators
- `Times.Exactly(N)` / call-count assertions
- `MockBehavior.Strict`
- Testing private methods
- Verifying via DB/state inspection instead of public API
- Test breaks on refactor with no behavior change
