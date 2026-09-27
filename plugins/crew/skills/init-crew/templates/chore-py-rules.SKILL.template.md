---
name: chore-py-rules
description: Repository-specific Python cleanup rules for Chorey. Used only by Chorey during behavior-preserving review.
---

# Chore Python rules

## Hazard rules

- Never collapse a narrowed `except SomeError:` back into a broader `except Exception:` while refactoring — the narrowing is often a deliberate prior fix, not incidental style.

## Review rules

- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

## Repository rules

<!-- Add observed repository-specific cleanup rules and protected content here. -->
