---
name: {{skill_name}}
description: Repository-specific {{stack_description_name}} cleanup rules for Chorey. Used only by Chorey during behavior-preserving review.
---

# Chore {{stack_display_name}} rules

## Hazard rules

<!-- stack: ai -->
- Never fold two skills' distinct triggers into one shared description just to remove duplication — a description that now fires on unrelated tasks is a correctness regression, not a cleanup.
<!-- /stack: ai -->
<!-- stack: dotnet -->
- Never hand-edit a generated file (`*.Designer.cs`, `*.g.cs`, or anything under `obj/`/`bin/`) as part of a cleanup — regenerate it through its source instead.
<!-- /stack: dotnet -->
<!-- stack: py -->
- Never collapse a narrowed `except SomeError:` back into a broader `except Exception:` while refactoring — the narrowing is often a deliberate prior fix, not incidental style.
<!-- /stack: py -->

## Review rules

<!-- stack: ai -->
- **Duplication** → extract shared procedure into the skill that owns it, invoked by name
- **Long/branching steps** → break into decision criteria or sub-steps
- **Shallow skills** → combine or deepen
- **Stale reference** → update or disclose to a sibling file
- **Existing content** the new content reveals as problematic
<!-- /stack: ai -->
<!-- stack: dotnet -->
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic
<!-- /stack: dotnet -->
<!-- stack: py -->
- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic
<!-- /stack: py -->

## Repository rules

<!-- Add observed repository-specific cleanup rules and protected content here. -->
