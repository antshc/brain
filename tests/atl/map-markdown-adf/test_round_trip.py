"""Round-trip: Markdown -> ADF -> Markdown preserves wording word for word."""
import re

_ORIGINAL_MD = """<!-- adf:toc -->

# Heading One

A paragraph with **bold**, *italic*, `inline code`, a [link](https://example.com/page), and ~~strikethrough~~ text.

- bullet one
- bullet two

1. ordered one
2. ordered two

> a blockquote line

> [!WARNING]
> a panel line

Assignee: 🔵[In Progress]

```python
x = 1
```

| Col A | Col B |
| --- | --- |
| one | two |
| three | four |

<!-- adf:wide-table -->

| Wide A | Wide B |
| --- | --- |
| five | six |

---

<details>
<summary>More details</summary>

hidden paragraph text
</details>"""


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def test_round_trip_preserves_wording(md_to_adf, adf_to_md):
    doc = md_to_adf(_ORIGINAL_MD)
    round_tripped = adf_to_md(doc)
    assert _words(round_tripped) == _words(_ORIGINAL_MD)


def test_round_trip_preserves_code_span_inside_link(md_to_adf, adf_to_md):
    source = "see [`Foo.Bar`](https://example.com) here"
    assert adf_to_md(md_to_adf(source)).strip() == source


_LAYOUT_MD = """<!-- adf:breakout mode="wide" width="760" -->
<details>
<summary>Wide expand</summary>

inner
</details>

<!-- adf:breakout mode="full-width" -->
```python
x = 1
```

<!-- adf:table layout="wide" width="960" -->

| A | B |
| --- | --- |
| 1 | 2 |

<!-- adf:table width="600" -->

| C | D |
| --- | --- |
| 3 | 4 |

<!-- adf:wide-table -->

| E | F |
| --- | --- |
| 5 | 6 |"""


def test_breakout_and_table_attrs_round_trip_exactly(md_to_adf, adf_to_md):
    assert adf_to_md(md_to_adf(_LAYOUT_MD)).strip() == _LAYOUT_MD


def test_breakout_marker_sets_the_mark_on_the_next_expand_or_code_block(md_to_adf):
    expand, code, wide_960, width_600, wide = md_to_adf(_LAYOUT_MD)["content"]
    assert expand["marks"] == [{"type": "breakout", "attrs": {"mode": "wide", "width": 760}}]
    assert code["marks"] == [{"type": "breakout", "attrs": {"mode": "full-width"}}]
    assert (wide_960["attrs"]["layout"], wide_960["attrs"]["width"]) == ("wide", 960)
    assert (width_600["attrs"]["layout"], width_600["attrs"]["width"]) == ("default", 600)
    assert "width" not in wide["attrs"]


def test_breakout_marker_before_a_paragraph_is_dropped(md_to_adf):
    doc = md_to_adf('<!-- adf:breakout mode="wide" -->\nplain text')
    assert doc["content"] == [{"type": "paragraph", "content": [{"type": "text", "text": "plain text"}]}]


def test_float_table_width_from_confluence_renders_as_an_integer(adf_to_md):
    table = {
        "type": "table",
        "attrs": {"layout": "wide", "width": 960.0},
        "content": [{"type": "tableRow", "content": [{"type": "tableHeader", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "H"}]}]}]}],
    }
    assert adf_to_md({"type": "doc", "content": [table]}).startswith('<!-- adf:table layout="wide" width="960" -->')


def test_breakout_on_the_toc_expand_round_trips_and_does_not_leak(md_to_adf, adf_to_md):
    source = '<!-- adf:breakout mode="wide" width="760" -->\n<!-- adf:toc -->\n\n<details>\n<summary>Later</summary>\n\nbody\n</details>'
    toc, later = md_to_adf(source)["content"]
    assert toc["marks"] == [{"type": "breakout", "attrs": {"mode": "wide", "width": 760}}]
    assert "marks" not in later
    assert adf_to_md(md_to_adf(source)).strip() == source
