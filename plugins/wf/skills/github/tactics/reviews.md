# Reviews

- **Draft or finalize review comment** → load [Review comments](../references/review-comments.md). Apply `writing-style` **Unslop only** to draft prose. Final keeps the validated visible body verbatim and applies the ownership rules for the terminal marker.
- **Discussion** → `review discussion REF --pretty` before checkout or mutation. Honor `stop / skip / proceed`. Preserve the full published `threads[].comments` snapshots, IDs, and head.
- **Inline** → `review inline REF --expected HEAD [--base BASE] --path PATH --line LINE --body-file FILE`. Use only the selected route's verified right-side diff anchor and approved text. Keep unanchored findings unposted.
- **Reply** → `review reply REF --expected HEAD --thread ID --snapshot FILE --body-file FILE`. Snapshot is the target thread's exact published comments array. Append the confirmed returned comment to the recorded snapshot.
- **Resolve** → `review resolve REF --expected HEAD --thread ID --snapshot FILE`. Caller must confirm settled evidence, agent ownership, and no unaccepted deferral or open question. Compare complete comments including edited bodies/timestamps. Reassess changes. Missing or truncated thread context blocks the write.
