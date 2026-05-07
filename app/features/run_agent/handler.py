"""Dispatches review threads to the Copilot agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from domain.pull_request import PullRequest
from domain.review_thread import ReviewThread
from features.run_agent import prompt_builder
from infrastructure import copilot_client, gh_client


def run_agent(pr: PullRequest, threads: list[ReviewThread]) -> None:
    """Check out the PR branch and run the Copilot agent on actionable threads.

    Args:
        pr: The pull request to process.
        threads: Actionable review threads to address.
    """
    gh_client.checkout_pr(pr.url)
    prompt = prompt_builder.build_prompt(threads)
    proc = copilot_client.run(prompt)
    copilot_client.stream_text(proc)
