---
name: to-prd
description: Create a PRD from codebase context and submit as a GitHub issue. Use when user wants to write a PRD or plan a new feature.
argument-hint: '<feature description>'
---

Ask the user: _"What is the target branch and feature ID? (e.g. `release/1.1.10`, `PROJ-1234`)"_

You may skip steps if you don't consider them necessary.

Harvest from the conversation before writing:
- Grilling decisions → *Implementation Decisions*
- Out-of-scope items → *Out of Scope*

1. Explore the repo. Use domain glossary and respect ADRs if `grill-with-docs` ran. Identify the layer structure in use (`references/layers.md`): layers present, naming conventions, one example each — emit a brief layer map.

2. Sketch modules to build or modify. Prefer deep modules (broad functionality, simple stable interface). Assign each a layer (Manager / Engine / ResourceAccessor / Repository / Client / Utilities) and validate dependency direction — flag upward references. Confirm modules, layer assignments, and test scope with the user.

3. Write the PRD using the template and writing style defined in `references/format-prd.md`.

4. Save to GitHub — see _Create GitHub Issue section_ below.

5. Report the PRD location, milestone title, and URLs to the user.
---

### Create GitHub Issue section (if user chooses GitHub issue as destination)

Resolve the target repo once.

**bash:**
```bash
REPO=$((git remote get-url board 2>/dev/null || git remote get-url origin) | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
```

**PowerShell:**
```powershell
$REPO = ($(git remote get-url board 2>$null) ?? $(git remote get-url origin)) `
  -replace '^git@[^:]+:','' `
  -replace '^https?://[^/]+/','' `
  -replace '\.git$',''
```

1. Create the issue:
   ```bash
   gh issue create --repo "$REPO" --label prd --title "<feature-id>: <prd-title>"
   ```

2. Create a milestone and assign the issue to it:
   ```bash
   gh api repos/$REPO/milestones \
     --method POST \
     --field title="<feature-id>: <prd-title>" \
     --field description="**Feature ID:** \`<feature-id>\`\n**Target Branch:** \`<target-branch>\`"
   gh issue edit <number> --repo "$REPO" --milestone "<feature-id>: <prd-title>"
   ```

---

## Troubleshooting

**Label not found** (`prd` label missing): run `setup-gh-labels` to create the required labels, then retry.