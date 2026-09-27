---
name: crew-chore
description: Repository-specific, stack-aware cleanup rules for Chorey. Used only by Chorey during behavior-preserving review.
---

# Crew Chore rules

Read the files in `stacks/` before reviewing. Each file contains the rules for one configured stack. Infer the applicable stacks from the review scope, then load every matching stack file. If no stack file confidently matches, use observed repository conventions alone.

<!-- stack: ai -->
## Hazard rules

- Never fold two skills' distinct triggers into one shared description just to remove duplication — a description that now fires on unrelated tasks is a correctness regression, not a cleanup.

## Review rules

- **Duplication** → extract shared procedure into the skill that owns it, invoked by name
- **Long/branching steps** → break into decision criteria or sub-steps
- **Shallow skills** → combine or deepen
- **Stale reference** → update or disclose to a sibling file
- **Existing content** the new content reveals as problematic

## Repository rules

<!-- Add observed repository-specific cleanup rules and protected content here. -->
<!-- /stack: ai -->
<!-- stack: dotnet -->
## Hazard rules

- Never hand-edit a generated file (`*.Designer.cs`, `*.g.cs`, or anything under `obj/`/`bin/`) as part of a cleanup — regenerate it through its source instead.

## Review rules

- **Duplication** → extract function/class
- **Long methods** → break into private helpers (keep tests on public interface)
- **Shallow modules** → combine or deepen
- **Feature envy** → move logic to where data lives
- **Primitive obsession** → introduce value objects
- **Existing code** the new code reveals as problematic

## Repository rules

<!-- Add observed repository-specific cleanup rules and protected content here. -->
<!-- /stack: dotnet -->
<!-- stack: py -->
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

<!-- /stack: py -->
