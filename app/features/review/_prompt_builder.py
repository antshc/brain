"""Assembles the Copilot agent prompt from review threads and the prompt template."""

import json
from pathlib import Path

from domain.review_thread import ReviewThread

# review → features → app → root
PROMPT_PATH = Path(__file__).resolve().parent.parent.parent.parent / "prompt.md"


def build_prompt(threads: list[ReviewThread]) -> str:
    """Build the full copilot prompt from review threads and the prompt template."""
    threads_data = [
        {
            "thread_id": t.thread_id,
            "prefix": t.label.value,
            "path": t.path,
            "lines": t.lines,
            "body": t.body,
            "discussion": t.discussion,
        }
        for t in threads
    ]
    threads_json = json.dumps(threads_data, indent=2)
    template = PROMPT_PATH.read_text()
    return f"# Review Threads\n\n{threads_json}\n\n{template}"
