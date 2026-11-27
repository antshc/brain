# rg route

Literals, config keys, error text, route paths, test names, file globs, frontend components, UI text; fallback search for every other route.

## Search

- Use the harness grep/rg tool, or shell `rg` with `-t <lang>` / `-g <glob>`; add `-F` for literals containing regex metacharacters.
- Search the literal, then its naming variants (camelCase, snake_case, kebab-case, config-section path) when the thoroughness level requires variants.
- A hit inside a symbol whose callers or implementations matter → continue on route `lsp`.
- Absence → re-run with `rg -uu` across every searched root, then return `NOT FOUND` with those roots.

## Install

`command -v rg` empty → install once per-user, no sudo: latest `BurntSushi/ripgrep` release asset for the platform (`x86_64-unknown-linux-musl`, `aarch64-unknown-linux-gnu`, `<arch>-apple-darwin` `.tar.gz`; `x86_64-pc-windows-msvc` `.zip`), verified against its `.sha256`, only `rg` extracted to `~/.local/bin/` (Windows: `%LOCALAPPDATA%\Programs\ripgrep\`), run by absolute path when not on `PATH`. Install fails → LSP and bounded reads; report the coverage gap.

## Gotchas

- `rg` exit `1` means no match, not a missing binary; only `command -v rg` decides presence. Exit `2` is an error.
- **MUST NOT** install `rg` while `command -v rg` resolves.
