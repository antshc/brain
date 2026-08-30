from zdesign_publisher.theme import LIGHT_THEME_CSS, apply_light_theme


def test_apply_light_theme_swaps_every_known_dark_hex():
    code = "fill:#2a2a2a,stroke:#8b949e,color:#c9d1d9\nstroke:#4a7a5a\nstroke:#8a4a4a\nborderColor=\"#4a5a8a\""
    result = apply_light_theme(code)
    assert "#2a2a2a" not in result and "#f6f8fa" in result
    assert "#8b949e" not in result and "#57606a" in result
    assert "#c9d1d9" not in result and "#24292f" in result
    assert "#4a7a5a" not in result and "#1a7f37" in result
    assert "#8a4a4a" not in result and "#cf222e" in result
    assert "#4a5a8a" not in result and "#0969da" in result


def test_apply_light_theme_leaves_unrelated_code_unchanged():
    code = "graph TD; A-->B;"
    assert apply_light_theme(code) == code


def test_light_theme_css_overrides_cluster_rect():
    assert ".cluster rect" in LIGHT_THEME_CSS
    assert "!important" in LIGHT_THEME_CSS
