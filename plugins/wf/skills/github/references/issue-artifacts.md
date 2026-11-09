# Issue artifacts

`artifact list REF` reads every page. `artifact get REF NUMBER` returns the exact attachment. `artifact put REF --name NAME --type TYPE --body-file FILE` needs gh 2.103.2 or newer and verifies the written name, type and body. Match exact names from the Design bundle manifest, record returned URLs, and resume at missing artifacts. Retain the manifest and confirmed URLs on partial failure.
