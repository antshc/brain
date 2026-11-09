---
name: lsp-navigate
description: Semantic (LSP-backed) navigation for .NET codebase. Use whenever a definition, reference, rename, type signature, implementation, or call hierarchy is needed, and before drawing conclusions about a diff, review, refactor, or a symbol's impact. Also use whenever a stack frame, exception, log line, or failing test names a symbol whose callers, overrides, implementations, or discarded return values must be enumerated before a conclusion is drawn.
---

# LSP Navigation

Inspect symbols semantically before concluding. A diff or single file read is not evidence, and graph or semantic-search hits are candidates, not evidence.

When a stack frame, exception, or failing test hands you a symbol, that symbol is the entry point: run usages and implementations on it first. Opening files one at a time answers a different, weaker question — it shows what the code says, not who reaches it, who overrides it, or who ignores what it returns.

## 1. Bind capabilities

Map each capability to a tool this host exposes. The host's tool list is the source of truth; columns are known bindings, not a closed set.

| Capability | Copilot CLI | VS Code | If unavailable |
| --- | --- | --- | --- |
| File outline | `documentSymbol` | — | read the file |
| Find symbol by name | `workspaceSymbol` | — | text search the declaration, scoped to owning area |
| Definition | `goToDefinition` | `vscode_listCodeUsages` | text search the declaration |
| Type / signature / modifiers | `hover` | — | read the declaration site |
| All usages | `findReferences` | `vscode_listCodeUsages` | text search the symbol name |
| Implementations | `goToImplementation` | `vscode_listCodeUsages` | text search `: <TypeName>` |
| Rename | rename | `vscode_renameSymbol` | do NOT hand-edit; report and stop |
| Diagnostics | `get diagnostics` | `get_errors` | build the affected project |
| Incoming / outgoing calls | `incomingCalls`, `outgoingCalls` | — | usages, then read each enclosing method |

`vscode_listCodeUsages` returns definitions, references, and implementations in one call — do not re-call it for the same symbol.

State the binding before the first lookup, and flag any capability that fell to the "If unavailable" column so its results are read as text-derived.

Sample representatively: never expand a reference list or call graph exhaustively without a hypothesis. Stop once impact is clear.

## 2. Text-search fallbacks

Every "If unavailable" fallback is a text search, and scoping it is host-dependent — a pattern that is correct under one host silently returns a **false empty result** under another. Scope per the repo's navigation policy, `.github/copilot-instructions.md` → *Step 3a — Scope searches to the right root*; prefer absolute paths when the layout is unclear.

An empty result from a *scoped* search is unproven. Re-run unscoped across all roots before concluding a symbol does not exist.

## 3. Trust boundary

A usages lookup answers only "who names this symbol in compiled C#". These bindings are invisible to it:

| Binding | Why it is missed | Cross-check |
| --- | --- | --- |
| DI registration | composition sits in module/startup classes; the interface→implementation binding may name neither type | text search the type name across DI module and startup files |
| Configuration keys / feature switches | bound by string, not symbol | text search the key string, not the property |
| REST contracts | property names travel over the wire and into the API contract; renaming silently changes the API | check the API contract/schema and any serializer attribute |
| Serialized / persisted shapes | stored attributes and payloads key off member names | text search the member name in storage and mapping code |
| Reflection and `nameof` | resolved at runtime, or as a string after compilation | text search the bare identifier |
| Source generators / generated code | generated sources may not be loaded or indexed | build, then re-run the lookup |
| Unloaded projects | cross-project references resolve only for loaded projects | confirm project load per [Recovery](#5-recovery) step 3 |
| Non-C# assets | markup, scripts, JSON config, test data sit outside the C# semantic model | text search scoped to those areas |

**Rule:** if the symbol crosses a DI, configuration, persistence, or REST boundary, semantic results are necessary but not sufficient — pair them with one scoped text search on the identifier before reporting impact.

## 4. Rename

Rename is the only capability that writes.

1. **Size it.** Run the usages capability. If the symbol crosses any boundary above, cross-check before touching anything.
2. **Check legality.** A REST contract member, persisted attribute, or configuration key is an external contract — renaming it is a behavior change, not a refactor. Stop and raise it.
3. **Rename semantically.** Never hand-edit occurrences file by file — that is how partial renames ship.
4. **Sweep.** Text search the old identifier; expect hits only where the name must intentionally stay.
5. **Verify.** Diagnostics on changed files, then the build — analyzers and generated code fire only on a real build, per the repo's verification policy.

If rename is unavailable on this host, report and stop; do not substitute a text replace.

## 5. Recovery

An empty or erroring lookup is usually cold start: Roslyn warms up per solution **and per worktree**. Wait and retry once before running recovery — never run recovery against a server still warming up.

Then run in order; stop as soon as results are healthy:

1. If the failure was an empty **text-search fallback**, re-check scoping per [§2](#2-text-search-fallbacks) and re-run unscoped.
2. Confirm CWD is the active code root — the checkout, or the worktree currently being worked in. Each worktree is a separate project load with its own warmup; do not `cd` out of it.
3. Confirm the solution/project is loaded.
4. Reload the semantic layer (host health check `/lsp test` in Copilot CLI; restart server, or reload window).
5. Build, only when required for project evaluation (per the repo's build and validation policy).

Still failing: report that semantic navigation is unavailable, name the failed capability, fall back to text search scoped to the active code root, then manual browsing, per the repo's navigation policy.
