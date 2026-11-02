from pathlib import Path

import shared_anchors

FIXTURE = Path(__file__).resolve().parents[1] / "fetch-page" / "fixtures" / "shared-anchor.md"


def test_lists_the_toi_shared_id_with_its_block_count(capsys):
    assert shared_anchors.main([str(FIXTURE)]) == 0

    assert capsys.readouterr().out == "1e1cb525-8cdd-4497-8fce-7213342df598\t2\n"


def test_prints_nothing_when_every_id_is_on_one_block(tmp_path, capsys):
    page = tmp_path / "page.md"
    page.write_text('<!-- adf:comment id="a" -->x<!-- /adf:comment --> <!-- adf:comment id="a" -->y<!-- /adf:comment -->\n')

    assert shared_anchors.main([str(page)]) == 0
    assert capsys.readouterr().out == ""
