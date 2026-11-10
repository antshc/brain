# Branches

Load [Branch naming](../references/branch-names.md) to draft a candidate. The caller verifies availability and authorizes creation or resumption.

## Execute

Use `branch inspect/create/fetch/push/delete --help` through `GIT_TOOL`. Use an absolute checkout. For fetch and push, verify the named remote belongs to the qualified repository. Fetch a full commit SHA. Push a verified local branch head with its recorded previous remote SHA or `absent`. Reconcile a lost push response by rereading the remote. Delete a local branch only after the caller authorizes cleanup and its recorded tip is reachable from the supplied integration SHA.
