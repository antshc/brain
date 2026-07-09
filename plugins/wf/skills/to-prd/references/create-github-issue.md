# Create GitHub Issue (if user chooses GitHub issue as destination)

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

## Troubleshooting

**Label not found** (`prd` label missing): run `setup-gh-labels` to create the required labels, then retry.
