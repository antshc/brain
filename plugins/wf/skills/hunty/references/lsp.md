# lsp route

Exact type or member: definitions, references, implementations, callers; impact of a known symbol; call hierarchy from A when no graph covers a flow.

## Lookup

- Use the harness LSP or usages tool for definitions, references, implementations, and call hierarchy; follow with `rg` for references LSP misses: DI registration, configuration binding, reflection, serialization names, routes, event subscriptions.
- Interface or abstract member → list every implementation; name the one the executing path binds (registration, factory, configuration) or mark the binding unresolved.
- Separate production implementations from tests, mocks, stubs, and emulators.
- Flow without a covering graph → walk the call hierarchy outward from A toward B; cite each hop.
- LSP unavailable → word-bounded `rg` on the symbol name with `-t <lang>`; report the degraded coverage.

## Impact

1. Run LSP references and implementations on the changed member or interface member.
2. Graph covers the target → run `affected` per the already-loaded graphify.md Reverse dependencies section: start at depth two; use the declaring type for type-wide changes or missing member coverage; resolve ambiguity before traversal; use `slice --direction in` when the focused command is unavailable.
3. Verify material consumers in source. Empty, unresolved, or incomplete graph results → targeted `rg` for configuration, event subscriptions, and wire or data contracts the graph may omit.
4. Return each consumer with `path:line`, the relationship (call, implementation, reference, configuration), and the graph command or skip reason.
