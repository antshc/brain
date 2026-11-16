# Write a root-cause report

Render and print one root-cause summary from supplied evidence. Add no new facts and run no probes.

## Input

Require the caller's `logPath`, checked hypotheses from that log, current-run mechanism-chain evidence, and analysis artifacts with what each contributed. Read the supplied log in full; the diagnosis caller owns locating, creating, updating and confirming it. Missing log or evidence returns as a blocker.

## Gate

At least one supplied hypothesis MUST be `confirmed`. If none is confirmed, stop and report that the root cause is not established. Never promote a falsified or blocked hypothesis to a cause.

## Execution

1. Match the confirmed hypothesis, checked alternatives, current evidence and supplied artifacts to the Root-cause template. Done when every claim has supplied support or is marked `Unknown`.
2. Fill the template, preserving business language, evidence row IDs, canonical URLs, optional-section conditions and redaction rules. Done when every mechanism claim cites re-checkable evidence and no secret or placeholder remains.
3. Print the rendered summary without wrapper prose. MUST NOT save the rendered summary to a file. Return a conflicting save request or missing evidence separately to the caller. Done when the report is returned inline and the hypothesis log remains unchanged.
