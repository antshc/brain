---
name: to-prd
description: Create a PRD through user interview, codebase exploration, and module design, then submit as a GitHub issue. Use when user wants to write a PRD, create a product requirements document, or plan a new feature.
argument-hint: '<target-branch> <jira-ticket> <feature description>'
---

This skill will be invoked when the user wants to create a PRD. You may skip steps if you don't consider them necessary.

The skill accepts positional arguments: `<target-branch> <jira-ticket> <feature description>`. If provided, use those values directly instead of asking later.

1. Ask the user for a long, detailed description of the problem they want to solve and any potential ideas for solutions.

2. Explore the repo to verify their assertions and understand the current state of the codebase.

3. Interview the user relentlessly about every aspect of this plan until you reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

4. Sketch out the major modules you will need to build or modify to complete the implementation. Actively look for opportunities to extract deep modules that can be tested in isolation.

A deep module (as opposed to a shallow module) is one which encapsulates a lot of functionality in a simple, testable interface which rarely changes.

Check with the user that these modules match their expectations. Check with the user which modules they want tests written for.

5. **Before writing the PRD**, ask the user:
   - **Target branch**: Which release branch should this work be based on? (e.g. `release/1.1.10`)
   - **Jira ticket**: What is the Jira ticket number for this work? (e.g. `PROJ-1234`)
   - **Save destination**: Where should the PRD be saved?
     - File: `<repo-root>/plans/{prd-title}.prd.md`
     - Create GitHub Issue: `gh issue create --repo $((git remote get-url board 2>/dev/null || git remote get-url origin) | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##') --label prd`

   If these were provided as positional arguments, skip asking.

6. **If saving as a GitHub issue**, after the issue is created, create a milestone and assign the issue to it:

   ```bash
   repo=$((git remote get-url board 2>/dev/null || git remote get-url origin) | sed -E 's#^git@[^:]+:##; s#^https?://[^/]+/##; s#\.git$##')
   gh api repos/$repo/milestones \
     --method POST \
     --field title="<jira-ticket>: <prd-title>" \
     --field description="**Jira Ticket:** \`<jira-ticket>\`\n**Target Branch:** \`<target-branch>\`"
   gh issue edit <number> --milestone "<jira-ticket>: <prd-title>"
   ```

   Report the milestone title and URL to the user.

7. Write the PRD using the `format-prd` skill's template and writing style. Save to the chosen destination.