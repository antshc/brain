# Verification Scope

This tactic inspects and proposes coverage; code and tests remain read-only. "Change" means a design change, not a source edit.

## Coverage categories

Trigger: a design answer changes behavior, persistence, or an integration boundary.

Check the `Crosscutting Concepts` index for a matching testing/verification Concept. Use the parent’s **Code/test lookup** operation to compare existing tests and conventions against that Concept. Send its Explore request directly to Hunter. If none matches, use evidenced code/test conventions alone.

Identify relevant test categories, reusable coverage, gaps, and proposed additions/updates/deletions. Cite evidence for existing coverage; unknown coverage stays unknown. Ask unresolved category decisions through the parent's decision flow.
