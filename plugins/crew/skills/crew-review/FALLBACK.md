# Review Fallback

Used by `crew-review` Step 1 when `CHORE_PATH` is unresolved (no `CHORE.md` found). A default, technology-agnostic checklist of behavior-preserving refactor candidates:

- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic
