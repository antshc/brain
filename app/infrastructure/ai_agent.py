"""Thin wrapper around the Copilot CLI for code-review operations."""

import json
import subprocess
from pathlib import Path

from domain.review_thread import ReviewThread

# infra → app → root
_ROOT = Path(__file__).resolve().parent.parent.parent
_LOG_DIR = _ROOT / "logs"
_PROMPT_PATH = _ROOT / "prompt.md"

_DEFAULT_MODEL = "claude-sonnet-4.6"

_DENIED_TOOLS = [
    "shell(git reset)",
    "shell(git rebase)",
    "shell(git clean)",
]


class AIAgent:
    """Copilot CLI agent for automated code-review operations."""

    def __init__(self, *, model: str = _DEFAULT_MODEL) -> None:
        self._model = model

    def review(self, threads: list[ReviewThread]) -> None:
        """Build the prompt and run the Copilot agent on the given review threads."""
        prompt = self._build_prompt(threads)
        proc = self._run(prompt)
        self._stream_text(proc)

    def _build_prompt(self, threads: list[ReviewThread]) -> str:
        threads_data = [
            {
                "thread_id": t.thread_id,
                "prefix": next(
                    (lbl.value for c in reversed(t.comments) if (lbl := c.get_label()) is not None),
                    "",
                ),
                "path": t.path,
                "lines": t.lines,
                "actionable_comment": t.actionable_comment,
                "comments": [{"author": c.author, "body": c.body} for c in t.comments],
            }
            for t in threads
        ]
        threads_json = json.dumps(threads_data, indent=2)
        template = _PROMPT_PATH.read_text()
        return f"# Review Threads\n\n{threads_json}\n\n{template}"

    def _run(self, prompt: str) -> subprocess.Popen:
        cmd = [
            "copilot",
            "-p", prompt,
            "--model", self._model,
            "--output-format", "json",
            "--allow-all-tools",
            "--no-ask-user",
            "--log-dir", str(_LOG_DIR),
        ]
        for tool in _DENIED_TOOLS:
            cmd.extend(["--deny-tool", tool])

        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def _stream_text(self, proc: subprocess.Popen) -> str:
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
