"""Thin wrapper around the GitHub CLI (`gh`) for GraphQL and REST operations."""

import json
import subprocess


def graphql(query: str, variables: dict | None = None) -> dict:
    """Execute a GraphQL query via `gh api graphql` and return the parsed JSON response.

    Args:
        query: The GraphQL query string.
        variables: Optional dict of variables. String values are passed with `-f`,
                   numeric values with `-F`.

    Returns:
        The full parsed JSON response (includes 'data' key).
    """
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in (variables or {}).items():
        flag = "-F" if isinstance(value, (int, float)) else "-f"
        cmd.extend([flag, f"{key}={value}"])

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


_REVIEW_THREADS_QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        nodes {
          id isResolved path line startLine
          comments(first: 50) {
            nodes { author { login } body }
          }
        }
      }
    }
  }
}
"""


def list_open_prs(user: str, repo: str) -> list[str]:
    """List open PR URLs authored by the given user in the repo."""
    result = subprocess.run(
        [
            "gh", "pr", "list",
            "--repo", repo,
            "--author", user,
            "--state", "open",
            "--json", "url",
            "--jq", ".[].url",
        ],
        capture_output=True, text=True, check=True,
    )
    return [url.strip() for url in result.stdout.strip().splitlines() if url.strip()]


def checkout_pr(pr_url: str) -> None:
    """Check out a PR branch locally."""
    subprocess.run(["gh", "pr", "checkout", pr_url], check=True)


def fetch_review_threads(owner: str, repo: str, number: int) -> list[dict]:
    """Fetch review threads for a PR via GraphQL.

    Returns a list of thread dicts with comments flattened (comments.nodes → comments).
    """
    data = graphql(_REVIEW_THREADS_QUERY, {"owner": owner, "repo": repo, "number": number})
    threads = data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
    for t in threads:
        t["comments"] = t["comments"]["nodes"]
    return threads
