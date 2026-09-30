# Explanations in agent skills

## Why agents add explanations

Agents often add rationale when writing a skill because rationale can help another agent generalize the rule beyond the exact wording.

Example:

```md
Do not use OCR unless necessary.
```

This is deterministic but narrow.

With rationale:

```md
Do not use OCR unless necessary; built-in vision is usually more reliable and cheaper.
```

The second form helps an agent decide what to do in an unseen case.

## When explanation is useful

Keep explanation only when it improves execution:

- **Ambiguous rule** — explains how to choose between valid actions.
- **Non-obvious constraint** — prevents an agent from "fixing" or ignoring a deliberate rule.
- **Trade-off** — explains what to optimize: correctness, cost, latency, safety, compatibility.
- **Boundary** — clarifies why this skill owns the task instead of another skill.
- **Exception** — explains when the normal rule should not apply.

## When explanation is noise

Remove rationale when the instruction is already deterministic.

Prefer:

```md
Run [scripts/locate_me.py](./scripts/locate_me.py) from this skill's base directory.
```

Avoid:

```md
Run the script from this skill's base directory because the skill can be invoked from
different working directories and relative paths may otherwise resolve incorrectly.
This ensures that the script is always found consistently.
```

The explanation adds tokens but does not change the action.

## Rule of thumb

Write skills as executable instructions, not documentation.

Use:

```text
Rule → condition/exception → action
```

Add **why** only when knowing why changes how the agent should act.

## Compression test

For every explanatory sentence ask:

> If I remove this sentence, can the agent still choose the correct action in all expected cases?

- **Yes** → remove it.
- **No** → keep it, but make it as short as possible.

## Good pattern

```md
Use X for Y.
If Z, use A instead because X cannot handle Z.
```

The rationale explains an exception that affects behavior.

## Bad pattern

```md
Use X for Y.

This approach is preferred because it provides a clean and consistent way to perform Y
and helps ensure the workflow remains reliable and maintainable.
```

The paragraph does not affect execution.

## Practical target

A strong skill body prioritizes:

1. Trigger/boundary.
2. Required actions.
3. Decision rules.
4. Exceptions.
5. Inputs/outputs.
6. Verification.
7. Minimal rationale only where it changes decisions.

Move background knowledge, tutorials, and extended reasoning to referenced documentation when needed.
