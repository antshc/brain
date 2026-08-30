"""Round-trip: Markdown -> ADF -> Markdown preserves wording word for word."""
import re

_ORIGINAL_MD = """# Heading One

A paragraph with **bold**, *italic*, `inline code`, a [link](https://example.com/page), and ~~strikethrough~~ text.

- bullet one
- bullet two

1. ordered one
2. ordered two

> a blockquote line

```python
x = 1
```

| Col A | Col B |
| --- | --- |
| one | two |
| three | four |

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
