"""Inline attachment media for Jira comment bodies (I/O: one Jira REST redirect lookup per file).

A comment shows an attachment inline only through an ADF `media` node whose `id` is the Media
Services file UUID, not the Jira attachment id. Jira exposes that UUID only in the redirect of
`/rest/api/3/attachment/content/<id>`; the redirect's access token is never read or kept.
Images become a `mediaSingle` preview, every other file a card in one `mediaGroup`.
"""
from __future__ import annotations

import mimetypes
import re
from collections.abc import Callable
from dataclasses import dataclass

import requests

from .config import site_url

IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp", "image/bmp"}
_MEDIA_FILE = re.compile(r"/file/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")

MediaResolver = Callable[[str], str]


@dataclass(frozen=True)
class Uploaded:
    attachment_id: str
    filename: str
    media_id: str
    image: bool


def media_resolver(credentials: dict[str, str]) -> MediaResolver:
    """A function mapping a Jira attachment id to its Media Services file UUID."""
    site = site_url(credentials)

    def resolve(attachment_id: str) -> str:
        response = requests.get(
            f"{site}/rest/api/3/attachment/content/{attachment_id}",
            auth=(credentials["email"], credentials["token"]),
            allow_redirects=False,
            timeout=30,
        )
        found = _MEDIA_FILE.search(response.headers.get("Location", ""))
        if not found:
            raise ValueError(f"attachment {attachment_id} has no media file id (HTTP {response.status_code})")
        return found.group(1)

    return resolve


def _is_image(filename: str, mime_type: str | None) -> bool:
    # Jira often reports no mime type for an upload, so the extension decides then.
    return (mime_type or mimetypes.guess_type(filename)[0]) in IMAGE_TYPES


def uploaded_from_response(item: dict, resolve: MediaResolver) -> Uploaded:
    attachment_id, filename = str(item["id"]), str(item["filename"])
    return Uploaded(attachment_id, filename, resolve(attachment_id), _is_image(filename, item.get("mimeType")))


def media_node(uploaded: Uploaded) -> dict:
    return {"type": "media", "attrs": {"type": "file", "id": uploaded.media_id, "collection": ""}}


def with_media(adf: dict, files: list[Uploaded]) -> dict:
    """Copy of `adf` with the files appended: a preview per image, then one group of file cards."""
    content = list(adf.get("content", []))
    content += [{"type": "mediaSingle", "attrs": {"layout": "center"}, "content": [media_node(file)]} for file in files if file.image]
    cards = [media_node(file) for file in files if not file.image]
    if cards:
        content.append({"type": "mediaGroup", "content": cards})
    return {**adf, "content": content}
