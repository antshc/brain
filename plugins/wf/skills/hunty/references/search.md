# Search routes: rg and lsp

Routes `rg` (literals, globs, text) and `lsp` (symbols, callers, implementations, impact). Also the fallback search for every other route.

## Contents

- Route rg
- Route lsp
- Impact
- Install rg
- Gotchas

## Route rg

Literals, config keys, error text, route paths, test names, file globs, frontend components, UI text.

- Use the harness grep/rg tool, or shell `rg` with `-t <lang>` / `-g <glob>`; add `-F` for literals containing regex metacharacters.
- Search the literal, then its naming variants (camelCase, snake_case, kebab-case, config-section path) when the thoroughness level requires variants.
- A hit inside a symbol whose callers or implementations matter → continue with Route lsp.
- Absence → re-run with `rg -uu` across every searched root, then return `NOT FOUND` with those roots.

## Route lsp

Exact type or member: definitions, references, implementations, callers; call hierarchy from A when no graph covers a flow.

- Use the harness LSP or usages tool for definitions, references, implementations, and call hierarchy; follow with `rg` for references LSP misses: DI registration, configuration binding, reflection, serialization names, routes, event subscriptions.
- Interface or abstract member → list every implementation; name the one the executing path binds (registration, factory, configuration) or mark the binding unresolved.
- Separate production implementations from tests, mocks, stubs, and emulators.
- Flow without a covering graph → walk the call hierarchy outward from A toward B; cite each hop.
- LSP unavailable → word-bounded `rg` on the symbol name with `-t <lang>`; report the degraded coverage.

## Impact

Impact or blast radius of a known symbol.

1. Run LSP references and implementations on the changed member or interface member.
2. Graph covers the target → run graph.md Impact; otherwise record `graph skipped: <reason>`.
3. Verify material consumers in source. Empty, unresolved, or incomplete graph results → targeted `rg` for configuration, event subscriptions, and wire or data contracts the graph may omit.
4. Return each consumer with `path:line`, the relationship (call, implementation, reference, configuration), and the graph command or skip reason.

## Install rg

`command -v rg` empty → install once per-user, no sudo: latest `BurntSushi/ripgrep` release asset for the platform (`x86_64-unknown-linux-musl`, `aarch64-unknown-linux-gnu`, `<arch>-apple-darwin` `.tar.gz`; `x86_64-pc-windows-msvc` `.zip`), verified against its `.sha256`, only `rg` extracted to `~/.local/bin/` (Windows: `%LOCALAPPDATA%\Programs\ripgrep\`), run by absolute path when not on `PATH`. Install fails → LSP and bounded reads; report the coverage gap.

## Gotchas

- `rg` exit `1` means no match, not a missing binary; only `command -v rg` decides presence. Exit `2` is an error.
- **MUST NOT** install `rg` while `command -v rg` resolves.
