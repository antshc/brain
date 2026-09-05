import pytest

from page_diagrams.patterns import strip_ignored_sections


def test_strip_ignored_sections_no_markers_is_noop():
    md = "# Title\n\nSome text.\n"
    assert strip_ignored_sections(md) == md


def test_strip_ignored_sections_removes_single_block():
    md = (
        "# Title\n\nkeep this\n\n"
        "<!-- confluence:ignore:start -->\n"
        "# Source Material\n\n| a | b |\n| --- | --- |\n"
        "<!-- confluence:ignore:end -->\n\n"
        "trailing text\n"
    )
    result = strip_ignored_sections(md)
    assert "Source Material" not in result
    assert "keep this" in result
    assert "trailing text" in result
    assert "confluence:ignore" not in result


def test_strip_ignored_sections_removes_multiple_blocks():
    md = (
        "<!-- confluence:ignore:start -->\ndrop one\n<!-- confluence:ignore:end -->\n"
        "keep middle\n"
        "<!-- confluence:ignore:start -->\ndrop two\n<!-- confluence:ignore:end -->\n"
    )
    result = strip_ignored_sections(md)
    assert "drop one" not in result
    assert "drop two" not in result
    assert "keep middle" in result


def test_strip_ignored_sections_unterminated_start_raises():
    md = "keep\n<!-- confluence:ignore:start -->\nnever closed\n"
    with pytest.raises(ValueError, match="unterminated"):
        strip_ignored_sections(md)
