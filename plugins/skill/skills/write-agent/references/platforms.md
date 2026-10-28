# Platforms

Agent file location, format, and metadata per client (October 2026).

## GitHub Copilot

- Location: `.github/agents/*.agent.md` or `.github/agents/*.md`; plugin agents under `plugins/<plugin>/agents/*.agent.md`.
- Format: YAML frontmatter + Markdown body.
- Fields: `name`, `description`, `tools`, `model`, `target`, invocation controls.
- Tool aliases: `read`, `search`, `edit`, `execute` (e.g. `tools: ["read", "search", "edit", "execute"]`).
- Omitting `tools` enables all available tools.
- IDE and cloud support differ; IDE handoffs are not supported by GitHub cloud agent.

## Claude Code

- Location: `.claude/agents/*.md`.
- Format: YAML frontmatter + Markdown body; the body is the subagent system prompt.
- Required: `name`, `description`. Optional: `tools`, `model`, `skills`, `memory`, `isolation`, `permissionMode`.
- Tools: comma list, e.g. `tools: Read, Glob, Grep`; omit `Edit`/`Bash` for read-only roles.

## OpenAI Codex

- Location: `.codex/agents/*.toml`.
- Format: TOML. Required: `name`, `description`, `developer_instructions` (body as a `"""` string). Optional: model settings, feature toggles.
- Custom agents inherit parent permissions; prompt text does not create a read-only sandbox.
- `name` uses underscores in official examples (`code_explorer`).

## Gemini CLI

- Location: `.gemini/agents/*.md`.
- Format: YAML frontmatter + Markdown body.
- Fields: `name`, `description`, `kind` (e.g. `local`), `tools` (YAML list, e.g. `read_file`, `grep_search`), `model`, `max_turns`, `timeout_mins`.

## Grok Build

- Location: `.grok/agents/`.
- Format: Grok-specific agent definitions; built-in types `general-purpose`, `explore`, `plan`; persona overlays configure behavior.
- Verify field names in the client docs before writing.

## Multi-platform

When several clients must run the same agent, keep one canonical behavioral body and render a thin adapter per client (`.claude/agents/`, `.github/agents/`, `.codex/agents/`); keep model and tool metadata in the adapter.
