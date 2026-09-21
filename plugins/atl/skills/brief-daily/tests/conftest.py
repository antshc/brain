import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

ME = "63f4d6193ec8aa51d3d20548"
MY_NAME = "Ada Lovelace"
THEM = "712020:987e9d71-5a3c-419d-89f7-aeeea9b36723"
THEIR_NAME = "Grace Hopper"
CLOUD_ID = "https://example.atlassian.net"


def mention(name):
    return f'<custom data-type="mention" data-id="id-0">@{name}</custom>'


def comment(created, *, author=THEM, name=THEIR_NAME, body="plain text"):
    return {
        "id": created,
        "body": body,
        "created": created,
        "updated": created,
        "author": {"accountId": author, "displayName": name},
    }


def issue(key, *, comments, total=None, summary="A summary", status="New", **fields):
    return {
        "key": key,
        "fields": {
            "summary": summary,
            "status": {"name": status},
            "comment": {
                "comments": comments,
                "total": len(comments) if total is None else total,
                "startAt": 0,
                "maxResults": len(comments),
            },
            **fields,
        },
    }


def page(nodes, *, has_next=False):
    """Mirrors the live `searchJiraIssuesUsingJql` response: a flat `issues` list, `isLast`
    signaling pagination, and no per-issue `webUrl`."""
    return {"issues": nodes, "isLast": not has_next}


@pytest.fixture
def spill(tmp_path):
    counter = {"n": 0}

    def write(payload):
        counter["n"] += 1
        path = tmp_path / f"content{counter['n']}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    return write
