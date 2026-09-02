# CHORE — Python

<!-- Read in full by crew-review during Chorey's REVIEW step. Hazard rules below are Python-general and ship with this template — kept even when repository practice differs; a conflict is recorded in the shared GOTCHAS.md instead of edited here. Review rules/Never describe this repo's own behavior-preserving cleanup rules — never invent or copy example values from another repo. When this file exists it replaces crew-review's inline default for this Stack's files. -->

## Hazard rules (Python)
- Never collapse a narrowed `except SomeError:` back into a broader `except Exception:` while refactoring — the narrowing is often a deliberate prior fix, not incidental style.

## Review rules
<!--
List the behavior-preserving refactor patterns Chorey should look for and apply to this repo's Python code, and anything it must never touch. Default checklist (replace or extend with real, repo-specific rules):
-->
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

## Never
<!-- List anything Chorey must never change in this repo's Python code (e.g. public API signatures, generated files, migration history). -->
