# CLI JSON Handoff

## Purpose
Two independently invoked CLI scripts need to exchange structured data (e.g. one script resolves credentials or facts, another consumes them) without importing one into the other.

## Rules
- MUST have the producing script emit exactly one JSON payload on stdout and nothing else (`print(json.dumps(...))`); send logs, warnings, and errors to stderr instead.
- MUST NOT write secrets (tokens, passwords, credentials) to stderr, logs, or any diagnostic output.
- MUST have the consuming script parse that JSON via `subprocess.run(..., capture_output=True, text=True, check=True)` and `json.loads(result.stdout)`, or via `json.load(sys.stdin)` when the shell composes the pipeline instead — never by scraping or regexing stdout.
- SHOULD use `subprocess.run(..., check=True)` when the consumer itself must own error handling and always control the producer's invocation; use shell piping only when a human or wrapper script composes the two commands ad hoc, and add `set -o pipefail` there so a producer failure doesn't silently hand the consumer empty or partial JSON.

## Design Guidance
Two variants share the same producer contract:
- **Subprocess capture** — the consumer calls `subprocess.run([...], capture_output=True, text=True, check=True)` and parses `result.stdout` with `json.loads`. A non-zero producer exit raises `CalledProcessError` in the consumer, so failure is never silent.
- **Shell pipe** — producer and consumer are chained as `producer | consumer`, and the consumer reads `json.load(sys.stdin)`. The consumer sees no automatic signal of the producer's exit code unless the pipeline runs under `set -o pipefail`.

Choose subprocess capture when the consumer must reliably detect and handle the producer failing. Choose shell piping when composition happens at the shell or wrapper-script level and the two commands are meant to be interchangeable, ad hoc pipeline stages.

The producer contract is what makes both variants interchangeable: stdout carries only the JSON payload, so a consumer can treat it as a pure data channel regardless of which composition mechanism wraps it.

## Examples
- `/preflight-atlassian`'s **Read** command (plugins/atl/skills/init-atl/preflight-atlassian.SKILL.template.md, Resolve step 1): `python3 -c "from pathlib import Path; print(Path('.atlassian.json.user').read_text())"` prints the config JSON as its only stdout output — the producer half of this contract.
- `/preflight-atlassian`'s **Locate** command prints `configPath`; `fetch-page`, `fetch-work`, and `publish-page` scripts take it as `--config "<configPath>"` and read the JSON themselves, because their stdin already carries the page or issue content.

## Considered options


## Consequences
- Every consumer pays the cost of the producer running as a separate process (process-startup latency) instead of a direct function import — accepted in exchange for keeping the two scripts independently invocable from the CLI.
