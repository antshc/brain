"""Dispatches review threads to the Copilot agent."""

from domain.pull_request import PullRequest
from domain.review_thread import ReviewThread
from features.review import _prompt_builder
from infrastructure import copilot_client, gh_client


def run_agent(pr: PullRequest, threads: list[ReviewThread]) -> None:
    """Check out the PR branch and run the Copilot agent on actionable threads."""
    gh_client.checkout_pr(pr.url)
    prompt = _prompt_builder.build_prompt(threads)
    proc = copilot_client.run(prompt)
    copilot_client.stream_text(proc)
