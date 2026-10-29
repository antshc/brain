# Numbered subflow template

Prefer this structure for branching workflows. Replace placeholders and omit unused branches. Keep each subflow at the level of detail requested.

```text
Flow: <name>

1. <shared discovery or entry>
2. Choose path
   → A: Run <Simple Flow>
   → B: Run <Complex Flow>
3. End


Subflow A: <Simple Flow>

1. <skill or action>
2. <skill or action>
3. Return


Subflow B: <Complex Flow>

1. <skill or action>
2. For each <item>:
   → <skill or action>
3. <skill or action>
4. Return
```

## Example: skill-call-level handoffs

```text
Flow: Idea → Implementation

1. Discovery
   → /grill-design OR /wayfinder

2. Choose path
   → A: Run Simple Flow
   → B: Run Complex Flow

3. End


Subflow A: Simple Flow

1. /to-spec
2. Architect Potato → Attach sketch to spec
3. /implement-spec parallel
4. Return


Subflow B: Complex Flow

1. /to-zdesign
2. /to-stories
3. For each story:
   → /grill-design
4. /to-spec
5. Architect Potato → Attach sketch to spec
6. /implement-spec parallel
7. Return
```
