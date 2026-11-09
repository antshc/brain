# Issues and labels

Resolve the tracker separately from source. Use qualified `OWNER/REPO#NUMBER` or GitHub issue URLs. Use `issue read --comments` for complete issue context and `issue list --repo R --label LABEL` to reconcile candidates.

| Operation | CLI |
| --- | --- |
| Create | `issue create --repo R --title TITLE --body-file FILE --label LABEL` |
| Update | `issue edit-body REF --body-file FILE`; prepare from the latest body and preserve unrelated changes |
| Claim or release | `issue assign/unassign REF --login @me`; read back the sole claimant before work |
| Relationships | `issue children/blockers REF`, `issue link-child PARENT CHILD`, `issue block REF --by BLOCKER...` |
| Evidence | `issue post-comment REF --body-file FILE` for a verbatim comment, `issue comment REF --body-file FILE --run-id ID` for Implement Spec evidence, or `issue upsert-comment REF --marker MARKER --body-file FILE` for an existing caller-owned marker |
| Close | `issue close REF` with caller-authorized evidence or exact closing summary |
| Labels | `label ensure/verify --repo R --manifest FILE` or `--name LABEL`; ensure requires color and preserves existing labels |

Record the issue reference before linking. On partial publication, read it and retry only missing links. Use native edges when requested. Body-based Wayfinder blockers stay caller policy.
