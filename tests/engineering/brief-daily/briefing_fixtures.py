"""Shared builders for the daily-briefing tests; a unique name so a combined pytest run never
resolves another folder's `conftest`."""
ME = "63f4d6193ec8aa51d3d20548"
MY_NAME = "Ada Lovelace"
THEM = "712020:987e9d71-5a3c-419d-89f7-aeeea9b36723"
THEIR_NAME = "Grace Hopper"
SITE = "https://example.atlassian.net"


def doc(*inline):
    return {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": list(inline)}]}


def text(value):
    return {"type": "text", "text": value}


def mention(account_id, name):
    """ADF comment body mentioning `account_id`, as twg returns it."""
    return doc(text("ping "), {"type": "mention", "attrs": {"id": account_id, "text": f"@{name}", "accessLevel": ""}})


def comment(created, *, author=THEM, name=THEIR_NAME, body=None):
    return {
        "id": created,
        "body": body if body is not None else doc(text("plain text")),
        "created": created,
        "updated": created,
        "author": {"accountId": author, "displayName": name},
    }


def issue(key, *, comments, total=None, summary="A summary", status="New", **fields):
    """twg flattens Jira fields onto the issue and adds its browse `url`."""
    return {
        "key": key,
        "url": f"{SITE}/browse/{key}",
        "summary": summary,
        "status": {"name": status},
        "comment": {
            "comments": comments,
            "total": len(comments) if total is None else total,
            "startAt": 0,
            "maxResults": len(comments),
        },
        **fields,
    }


def page(nodes, *, has_next=False):
    """Mirrors live `twg jira workitem query -o json --output-file` output."""
    return {"command": "jira.workitem.query", "data": {"issues": nodes}, "pageInfo": {"hasNextPage": has_next}}
