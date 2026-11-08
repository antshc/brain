# Pull requests

## Draft

Use the supplied canonical initiative ID, such as a Jira key or a qualified GitHub issue reference. Report a missing ID. Use the same ID in both places.

Title example: `[PAY-42] fix(retry): cap retry delay`. The portion after the marker is a conventional commit subject.

Start the body with a standalone bracketed ID. Follow it with Why, What changed, Verification, and optional References.

- **Why** uses supplied rationale. Keep implementation details separate.
- **What changed** summarizes the actual change.
- **Verification** reports observed checks and their results or gaps.
- **References** uses plain links or qualified refs, without issue-closing keywords.

Preserve user-authored text on managed updates. The caller verifies the head and base and owns publication and tracker state.

## Read initiative

1. Read the first nonblank body line. If it consists of a bracketed ID, use that ID. Otherwise accept the first standalone legacy ID in the body. Skip URLs, fenced and inline code, and IDs embedded in a word, path, or token.
2. Accept Jira-shaped keys case-insensitively and normalize them to uppercase for comparison and lookup. Accept bare GitHub issue numbers with `#` and qualified `owner/repo#number` refs. Keep other explicitly mapped legacy IDs for the caller to resolve.
3. If the title has a leading bracketed ID, compare it with the body ID and report a conflict on mismatch. A missing body ID remains a blocker even with a title marker.
4. Return the body ID or the precise problem. Tracker selection and work item lookup belong to the caller.
