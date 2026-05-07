"""Thin wrapper around the Copilot CLI for code-review operations."""

import json
import subprocess
from pathlib import Path

# infra → app → root → logs
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"

DEFAULT_MODEL = "claude-sonnet-4.6"

DENIED_TOOLS = [
    "shell(git reset)",
    "shell(git rebase)",
    "shell(git clean)",
]


def run(prompt: str, *, model: str = DEFAULT_MODEL) -> subprocess.Popen:
    """Launch copilot with the given prompt and return the Popen handle.

    The caller can iterate over stdout lines to consume streaming JSON output.

    Args:
        prompt: The full prompt string to send to copilot.
        model: The model to use.

    Returns:
        A Popen object with stdout piped (line-buffered text).
    """
    cmd = [
        "copilot",
        "-p", prompt,
        "--model", model,
        "--output-format", "json",
        "--allow-all-tools",
        "--no-ask-user",
        "--log-dir", str(LOG_DIR),
    ]
    for tool in DENIED_TOOLS:
        cmd.extend(["--deny-tool", tool])

    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def stream_text(proc: subprocess.Popen) -> str:
    """Consume copilot streaming output, print text deltas, and return full output.

    Reads JSON lines from the process stdout, extracts assistant message deltas,
    and prints them in real time.

    Args:
        proc: A Popen handle returned by `run()`.

    Returns:
        The concatenated text output from the assistant.
    """
    full_text = ""
    for line in proc.stdout:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant.message_delta":
            delta = event.get("data", {}).get("deltaContent", "")
            if delta:
                print(delta, end="", flush=True)
                full_text += delta

    proc.wait()
    print()
    return full_text
