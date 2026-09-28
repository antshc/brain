---
name: crew-chore
description: Repository-specific, stack-aware cleanup rules for Chorey. Used only by Chorey during behavior-preserving review.
---

# Crew Chore rules

Accept the manifest's JSON array from Chorey as `STACKS`. Do not infer stacks from the review scope.

When `STACKS` is nonempty, read each existing `stacks/<stack>.md` file named by the array. Report every missing named file as a discovery gap, then continue with the available rules and observed repository conventions. When `STACKS` is empty, enumerate and read every configured `stacks/*.md` file in filename order. Apply each loaded rule only where relevant and retain rule conflicts as findings. If no stack files are available, use observed repository conventions alone.

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
