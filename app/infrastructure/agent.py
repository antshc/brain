"""Thin wrapper around the Copilot CLI for code-review operations."""

import json
import subprocess
from pathlib import Path

from domain.review_thread import ReviewThread

# infra → app → root
_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = _ROOT / "logs"
PROMPT_PATH = _ROOT / "prompt.md"

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


def build_prompt(threads: list[ReviewThread]) -> str:
    """Build the full copilot prompt from review threads and the prompt template."""
    threads_data = [
        {
            "thread_id": t.thread_id,
            "prefix": t.label.value,
            "path": t.path,
            "lines": t.lines,
            "body": t.body,
            "comments": [{"author": c.author, "body": c.body} for c in t.comments],
        }
        for t in threads
    ]
    threads_json = json.dumps(threads_data, indent=2)
    template = PROMPT_PATH.read_text()
    return f"# Review Threads\n\n{threads_json}\n\n{template}"


def review(threads: list[ReviewThread]) -> None:
    """Build the prompt and run the Copilot agent on the given review threads."""
    prompt = build_prompt(threads)
    proc = run(prompt)
    stream_text(proc)
