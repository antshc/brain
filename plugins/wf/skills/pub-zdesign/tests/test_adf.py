from zdesign_publisher.adf import build_adf_doc, wire_media_ids


def test_wire_media_ids_maps_index_to_file_id():
    diagrams = [
        {"index": 0, "filename": "00-a.png"},
        {"index": 1, "filename": "01-b.png"},
    ]
    filename_to_file_id = {"00-a.png": "file-1", "01-b.png": "file-2"}
    assert wire_media_ids(diagrams, filename_to_file_id) == {0: "file-1", 1: "file-2"}


def test_build_adf_doc_toc_placeholder_becomes_expand():
    doc = build_adf_doc("<!-- confluence:toc -->\n# Title", {})
    toc = doc["content"][0]
    assert toc["type"] == "expand"
    assert toc["attrs"]["title"] == "Table of Contents"
    assert toc["content"][0]["attrs"]["extensionKey"] == "toc"
    assert doc["content"][1]["type"] == "heading"


def test_build_adf_doc_no_toc_without_placeholder():
    doc = build_adf_doc("# Title", {})
    assert doc["content"][0]["type"] == "heading"


def test_build_adf_doc_wraps_blocks_with_doc_envelope():
    doc = build_adf_doc("# Title\n\nParagraph text.", {})
    assert doc["version"] == 1
    assert doc["type"] == "doc"
    assert doc["content"][0]["type"] == "heading"
    assert doc["content"][1]["type"] == "paragraph"


def test_build_adf_doc_substitutes_media_marker_with_file_id():
    processed_md = "\x00MEDIA:0\x00"
    doc = build_adf_doc(processed_md, {0: "the-file-id"}, image_width=900)
    media_single = doc["content"][0]
    assert media_single["type"] == "mediaSingle"
    assert media_single["attrs"]["width"] == 900
    assert media_single["content"][0]["attrs"]["id"] == "the-file-id"
