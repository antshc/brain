import pytest

from page_diagrams.patterns import strip_ignored_sections


def test_strip_ignored_sections_no_markers_is_noop():
    md = "# Title\n\nSome text.\n"
    assert strip_ignored_sections(md) == md


def test_strip_ignored_sections_removes_single_block():
    md = (
        "# Title\n\nkeep this\n\n"
        "<!-- adf:ignore:start -->\n"
        "# Source Material\n\n| a | b |\n| --- | --- |\n"
        "<!-- adf:ignore:end -->\n\n"
        "trailing text\n"
    )
    result = strip_ignored_sections(md)
    assert "Source Material" not in result
    assert "keep this" in result
    assert "trailing text" in result
    assert "adf:ignore" not in result


def test_strip_ignored_sections_removes_multiple_blocks():
    md = (
        "<!-- adf:ignore:start -->\ndrop one\n<!-- adf:ignore:end -->\n"
        "keep middle\n"
        "<!-- adf:ignore:start -->\ndrop two\n<!-- adf:ignore:end -->\n"
    )
    result = strip_ignored_sections(md)
    assert "drop one" not in result
    assert "drop two" not in result
    assert "keep middle" in result


def test_strip_ignored_sections_unterminated_start_raises():
    md = "keep\n<!-- adf:ignore:start -->\nnever closed\n"
    with pytest.raises(ValueError, match="unterminated"):
        strip_ignored_sections(md)
