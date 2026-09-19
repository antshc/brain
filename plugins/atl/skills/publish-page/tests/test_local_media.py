from page_diagrams.local_media import extract_local_media


def test_extract_local_media_replaces_a_standalone_image_reference_with_a_marker(tmp_path):
    image = tmp_path / "screenshot.png"
    image.write_bytes(b"png-bytes")
    md = f"# Title\n\n![screenshot.png](screenshot.png)\n\nMore text.\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == "# Title\n\n\x00MEDIA:0\x00\n\nMore text.\n"
    assert items == [
        {"index": 0, "path": str(image), "filename": "screenshot.png", "is_image": True}
    ]


def test_extract_local_media_captures_width_and_height_from_a_following_size_comment(tmp_path):
    image = tmp_path / "screenshot.png"
    image.write_bytes(b"png-bytes")
    md = (
        "![screenshot.png](screenshot.png)\n"
        "<!-- media-size: width=611 height=793 -->\n"
    )

    processed, items = extract_local_media(md, tmp_path)

    assert processed == "\x00MEDIA:0\x00\n"
    assert items == [
        {
            "index": 0,
            "path": str(image),
            "filename": "screenshot.png",
            "is_image": True,
            "width": 611,
            "height": 793,
        }
    ]


def test_extract_local_media_drops_the_size_comment_even_when_unused_by_a_non_image_file(tmp_path):
    # A size comment should never appear after a generic-file link in practice (/fetch-page
    # only ever emits it after an image), but if it did, it must still be consumed so it
    # never survives into the ADF as a stray paragraph.
    doc = tmp_path / "notes.pdf"
    doc.write_bytes(b"pdf-bytes")
    md = "[notes.pdf](notes.pdf)\n<!-- media-size: width=611 height=793 -->\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == "\x00MEDIA:0\x00\n"
    assert items == [{"index": 0, "path": str(doc), "filename": "notes.pdf", "is_image": False}]


def test_extract_local_media_replaces_a_standalone_file_link_with_a_marker(tmp_path):
    doc = tmp_path / "notes.pdf"
    doc.write_bytes(b"pdf-bytes")
    md = "[notes.pdf](notes.pdf)\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == "\x00MEDIA:0\x00\n"
    assert items == [{"index": 0, "path": str(doc), "filename": "notes.pdf", "is_image": False}]


def test_extract_local_media_leaves_an_inline_reference_mixed_with_prose_untouched(tmp_path):
    (tmp_path / "screenshot.png").write_bytes(b"png-bytes")
    md = "See the ![screenshot.png](screenshot.png) above.\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == md
    assert items == []


def test_extract_local_media_leaves_an_external_url_untouched(tmp_path):
    md = "![diagram](https://example.com/diagram.png)\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == md
    assert items == []


def test_extract_local_media_leaves_an_in_page_anchor_untouched(tmp_path):
    md = "[Section](#section)\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == md
    assert items == []


def test_extract_local_media_leaves_an_unresolvable_local_path_untouched(tmp_path):
    md = "![missing.png](missing.png)\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == md
    assert items == []


def test_extract_local_media_resolves_a_percent_encoded_path(tmp_path):
    image = tmp_path / "Screenshot 2026-02-10.png"
    image.write_bytes(b"png-bytes")
    md = "![Screenshot 2026-02-10.png](Screenshot%202026-02-10.png)\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == "\x00MEDIA:0\x00\n"
    assert items[0]["path"] == str(image)


def test_extract_local_media_continues_indexing_from_start_index(tmp_path):
    (tmp_path / "notes.pdf").write_bytes(b"pdf-bytes")
    md = "[notes.pdf](notes.pdf)\n"

    processed, items = extract_local_media(md, tmp_path, start_index=3)

    assert processed == "\x00MEDIA:3\x00\n"
    assert items[0]["index"] == 3


def test_extract_local_media_indexes_multiple_references_in_order(tmp_path):
    (tmp_path / "a.png").write_bytes(b"a")
    (tmp_path / "b.pdf").write_bytes(b"b")
    md = "![a.png](a.png)\n\n[b.pdf](b.pdf)\n"

    processed, items = extract_local_media(md, tmp_path)

    assert processed == "\x00MEDIA:0\x00\n\n\x00MEDIA:1\x00\n"
    assert [item["index"] for item in items] == [0, 1]
    assert [item["filename"] for item in items] == ["a.png", "b.pdf"]
