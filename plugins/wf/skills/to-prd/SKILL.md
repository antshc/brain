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

1. Explore the repo to understand the current state of the codebase, if you haven't already. If `grill-with-docs` ran, use the project's domain glossary vocabulary throughout the PRD and respect any ADRs in the area you're touching.

2. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

3. Write the PRD using the template and writing style defined in `references/format-prd.md`.

4. Save to GitHub — see _Create GitHub Issue section_ below.

5. Report the PRD location, milestone title, and URLs to the user.
---

### Create GitHub Issue section (if user chooses GitHub issue as destination)

Resolve the target repo once.

**bash:**
```bash
REPO=$(git remote get-url origin | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
```

**PowerShell:**
```powershell
$REPO = $(git remote get-url origin) `
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
