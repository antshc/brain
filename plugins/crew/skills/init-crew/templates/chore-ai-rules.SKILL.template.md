---
name: chore-ai-rules
description: Repository-specific AI authoring cleanup rules for Chorey. Used only by Chorey during behavior-preserving review.
---

# Chore AI authoring rules

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
