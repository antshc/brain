# Requirements-Coverage Checklist

Use this checklist to evaluate the diff against its originating spec. Ground every conclusion
in a quoted spec line and specific code evidence, not the patch alone.

For each requirement in the spec, classify the diff into one of:

- **Missing or partial** — the requirement is not implemented, or only partly implemented.
  Quote the spec line and name what is absent.
- **Scope creep** — behavior in the diff that the spec did not ask for. Quote the diff hunk
  and confirm no spec line requests it.
- **Implemented but wrong** — the requirement appears implemented but the behavior diverges
  from what the spec states. Quote the spec line and the diverging code.
- **Implemented correctly** — the requirement is fully and faithfully implemented. Record it
  in `passed`.

If no spec was found (`spec` is `null`), report "no spec available" and stop.

> Axis review rules (evidence, scope, deduplication, filtering) apply. See `<skill-directory>/references/review-rules.md`.
