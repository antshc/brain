"""Thin wrapper around the Copilot CLI for code-review operations."""

import json
import os
import subprocess
from pathlib import Path

from afk.shared.log import log_json
from modules.github.domain.review_thread import ReviewThread

# infrastructure → afk → src → tools → brain (root)
_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
_LOG_DIR = _ROOT / "logs"

_DEFAULT_MODEL = "claude-sonnet-4.6"
_DEFAULT_PROMPT = "/review"

_DENIED_TOOLS = [
    "shell(git reset)",
    "shell(git rebase)",
    "shell(git clean)",
]


def _is_dry_run() -> bool:
    """Return True (dry-run on) unless AFK_DRY_RUN is explicitly '0' or 'false'."""
    val = os.environ.get("AFK_DRY_RUN", "1")
    return val.lower() not in ("0", "false")


class AIAgent:
    """Copilot CLI agent for automated code-review operations."""

    def __init__(self, *, model: str = _DEFAULT_MODEL) -> None:
        self._model = model

    def review(self, threads: list[ReviewThread], prompt: str = _DEFAULT_PROMPT) -> None:
        """Build the prompt and run the Copilot agent on the given review threads."""
        full_prompt = self._build_prompt(threads, prompt)
        proc = self._run(full_prompt)
        if proc is not None:
            self._stream_text(proc)

    def _build_prompt(self, threads: list[ReviewThread], prompt: str) -> str:
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
        return f"{prompt}\n\n{threads_json}"

    def _run(self, prompt: str) -> subprocess.Popen | None:
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

        if _is_dry_run():
            log_json("info", "dry-run: skipping copilot agent", command=str(cmd))
            return None

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
