# CHORE

<!-- Read in full by crew-review during Chorey's REVIEW step. Describe this repo's own behavior-preserving cleanup rules — never invent or copy example values from another repo. When this file exists it replaces crew-review's inline default. -->

## Review rules
<!--
List the behavior-preserving refactor patterns Chorey should look for and apply in this repo, and anything it must never touch. Default checklist (replace or extend with real, repo-specific rules):
-->
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

## Never
<!-- List anything Chorey must never change in this repo (e.g. public API signatures, generated files, migration history). -->
