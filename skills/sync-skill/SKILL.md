---
name: sync-skill
description: Merge improvements from an upstream skill version into your local customized version, preserving intentional drift.
disable-model-invocation: true
---

You have a **local** skill with intentional **drift** from the **upstream** original. This skill extracts the upstream **delta**, classifies each change, and applies the ones that sharpen the local skill without touching its drift.

## Process

1. Read the local skill in full. Identify its **drift** — sections that appear intentionally customized. Done when you can state the purpose of each divergence.

2. Ask the user to paste the upstream skill content. Done when you have the full upstream text.

3. Identify the **delta**: every place upstream differs from local — added/removed steps, reworded text, new leading words, new guards, changed completion criteria. Done when every upstream change is named.

4. Classify each delta item:
   - **Adoptable** — improves the skill without touching local drift
   - **Conflicting** — would overwrite intentional local customization
   - **Irrelevant** — the skills have diverged enough the change doesn't apply

   Apply the failure-mode taxonomy from `writing-great-skills` (leading words, no-ops, premature completion, duplication, negation) to judge whether adoptable items are genuine improvements. Done when every delta item is classified.

5. Present only adoptable items. For each: quote the upstream text, name the improvement type (sharper criterion, new leading word, pruned no-op, etc.), and ask whether to adopt it. Done when the user has responded to each item.

6. Apply accepted changes to the local skill. Done when every accepted improvement is in the file and no local drift has been disturbed.
