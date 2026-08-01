# CHORE

<!-- Read in full by ralph-chore. Add only repository-specific review rules supported by evidence. -->

<!-- C# .NET
After the Verify phase passes, review all changed files together for refactoring candidates:
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic
-->