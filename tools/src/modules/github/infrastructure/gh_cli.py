"""Thin wrapper around the `gh` CLI for subprocess execution."""

import json
import subprocess

_ISSUE_COMMENTS_LIMIT = 20
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
_OPEN_ISSUES_QUERY = """
query($owner: String!, $repo: String!) {{
  repository(owner: $owner, name: $repo) {{
    issues(first: 100, states: OPEN) {{
      nodes {{
        number title body url
        labels(first: 20) {{
          nodes {{ name }}
        }}
        comments(first: {comments_limit}) {{
          nodes {{ id body createdAt }}
        }}
      }}
    }}
  }}
}}
""".format(comments_limit=_ISSUE_COMMENTS_LIMIT)


class GhCli:
    """Executes `gh` CLI commands and returns raw data."""

    def pr_list(self, user: str, repo: str) -> list[dict]:
        """Run `gh pr list` and return parsed JSON list of PR objects."""
        result = subprocess.run(
            [
                "gh", "pr", "list",
                "--repo", repo,
                "--author", user,
                "--state", "open",
                "--json", "url",
            ],
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)

    def fetch_threads_raw(self, owner: str, repo: str, number: int) -> list[dict]:
        """Run `gh api graphql` for review threads and return flattened nodes."""
        cmd = [
            "gh", "api", "graphql",
            "-f", f"query={_REVIEW_THREADS_QUERY}",
            "-f", f"owner={owner}",
            "-f", f"repo={repo}",
            "-F", f"number={number}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        nodes = data["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
        for node in nodes:
            node["comments"] = node["comments"]["nodes"]
        return nodes

    def fetch_issues_raw(self, owner: str, repo: str) -> list[dict]:
        """Run `gh api graphql` for open issues and return flattened nodes."""
        cmd = [
            "gh", "api", "graphql",
            "-f", f"query={_OPEN_ISSUES_QUERY}",
            "-f", f"owner={owner}",
            "-f", f"repo={repo}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        nodes = data["data"]["repository"]["issues"]["nodes"]
        for node in nodes:
            node["labels"] = [label["name"] for label in node["labels"]["nodes"]]
            node["comments"] = node["comments"]["nodes"]
        return nodes

    def pr_checkout(self, pr_url: str) -> None:
        """Run `gh pr checkout` for the given PR URL."""
        subprocess.run(["gh", "pr", "checkout", pr_url], check=True)
