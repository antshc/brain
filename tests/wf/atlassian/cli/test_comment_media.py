"""`comment_media.py`: media file-id lookup and ADF assembly for inline comment attachments."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from atl_cli import comment_media
from atl_cli.comment_media import Uploaded, media_resolver, with_media

CREDENTIALS = {"site": "org.atlassian.net", "email": "me@x.com", "token": "secret-token"}
UUID = "a7b047b2-009f-4465-b755-a060ab84fac8"


def test_media_resolver_reads_the_file_uuid_from_the_redirect_without_following_it(monkeypatch):
    seen = {}

    def get(url, **kwargs):
        seen.update(url=url, **kwargs)
        return SimpleNamespace(status_code=303, headers={"Location": f"https://api.media.atlassian.com/file/{UUID}/binary?token=abc&dl=true"})

    monkeypatch.setattr(comment_media.requests, "get", get)

    assert media_resolver(CREDENTIALS)("153773") == UUID
    assert seen["url"] == "https://org.atlassian.net/rest/api/3/attachment/content/153773"
    assert seen["allow_redirects"] is False
    assert seen["auth"] == ("me@x.com", "secret-token")


def test_media_resolver_rejects_a_response_without_a_file_uuid(monkeypatch):
    monkeypatch.setattr(comment_media.requests, "get", lambda *args, **kwargs: SimpleNamespace(status_code=404, headers={}))

    with pytest.raises(ValueError, match="no media file id.*404"):
        media_resolver(CREDENTIALS)("1")


def test_with_media_appends_previews_then_one_card_group_without_mutating_the_body():
    body = {"type": "doc", "version": 1, "content": [{"type": "paragraph"}]}
    files = [Uploaded("1", "a.txt", "m1", False), Uploaded("2", "b.png", "m2", True), Uploaded("3", "c.pdf", "m3", False)]

    result = with_media(body, files)

    assert [node["type"] for node in result["content"]] == ["paragraph", "mediaSingle", "mediaGroup"]
    assert [node["attrs"]["id"] for node in result["content"][2]["content"]] == ["m1", "m3"]
    assert body["content"] == [{"type": "paragraph"}]


@pytest.mark.parametrize(
    ("item", "image"),
    [
        ({"id": 1, "filename": "a.png", "mimeType": None}, True),
        ({"id": 1, "filename": "A.JPG"}, True),
        ({"id": 1, "filename": "a.bin", "mimeType": "image/gif"}, True),
        ({"id": 1, "filename": "a.svg", "mimeType": "image/svg+xml"}, False),
        ({"id": 1, "filename": "a.txt", "mimeType": "text/plain"}, False),
    ],
)
def test_images_are_detected_from_the_mime_type_or_the_file_extension(item, image):
    assert comment_media.uploaded_from_response(item, lambda attachment_id: "m").image is image
