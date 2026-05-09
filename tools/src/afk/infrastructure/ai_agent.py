"""Thin wrapper around the Copilot CLI for code-review operations."""

import os
import subprocess

from afk.shared.log import log_json

def _is_dry_run() -> bool:
    """Return True (dry-run on) unless AFK_DRY_RUN is explicitly '0' or 'false'."""
    val = os.environ.get("AFK_DRY_RUN", "1")
    return val.lower() not in ("0", "false")


class AIAgent:
    """Copilot CLI agent for automated code-review operations."""

    def __init__(self, *, alias: str = "copilot", prompt: str = "/review") -> None:
        self._alias = alias
        self._prompt = prompt

    def run(self) -> None:
        """Run the Copilot agent on the given review threads."""
        proc = self._run(self._prompt)
        if proc is not None:
            self._stream_text(proc)

    def _run(self, prompt: str) -> subprocess.Popen | None:
        cmd = [self._alias, "-p", prompt]

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
