"""Table-geometry rejection cases for both conversion directions."""
import json


def test_md_to_adf_rejects_ragged_table(run_cli):
    md = "| a | b | c |\n| --- | --- | --- |\n| 1 | 2 |"
    result = run_cli("md-to-adf", md)
    assert result.returncode != 0
    assert "table" in result.stderr.lower()
    assert result.stdout == ""


def test_adf_to_md_rejects_ragged_colspan_table(run_cli):
    doc = {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "table",
                "attrs": {"isNumberColumnEnabled": False, "layout": "default"},
                "content": [
                    {
                        "type": "tableRow",
                        "content": [
                            {
                                "type": "tableHeader",
                                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "a"}]}],
                            },
                            {
                                "type": "tableHeader",
                                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "b"}]}],
                            },
                            {
                                "type": "tableHeader",
                                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "c"}]}],
                            },
                        ],
                    },
                    {
                        "type": "tableRow",
                        "content": [
                            {
                                "type": "tableCell",
                                "attrs": {"colspan": 2},
                                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "1-2"}]}],
                            },
                        ],
                    },
                ],
            }
        ],
    }
    result = run_cli("adf-to-md", json.dumps(doc))
    assert result.returncode != 0
    assert "table" in result.stderr.lower()
    assert result.stdout == ""
