from page_diagrams.theme import LIGHT_THEME_COLOR_MAP, LIGHT_THEME_CSS, apply_light_theme


def test_apply_light_theme_swaps_every_known_dark_hex():
    code = "fill:#242424,stroke:#8b949e,color:#c9d1d9\nstroke:#4a7a5a\nstroke:#8a4a4a\nborderColor=\"#4a5a8a\"\nbgColor=\"#2a2a2a\"\nbgColor=\"#1a1a1a\""
    result = apply_light_theme(code)
    assert "#242424" not in result and "#f6f8fa" in result
    assert "#8b949e" not in result and "#57606a" in result
    assert "#c9d1d9" not in result and "#24292f" in result
    assert "#4a7a5a" not in result and "#1a7f37" in result
    assert "#8a4a4a" not in result and "#cf222e" in result
    assert "#4a5a8a" not in result and "#0969da" in result
    assert "#2a2a2a" not in result
    assert "#1a1a1a" not in result and "#d0d7de" in result


def test_apply_light_theme_keeps_internal_and_external_fills_distinct():
    result = apply_light_theme('bgColor="#2a2a2a" bgColor="#1a1a1a"')
    internal, external = LIGHT_THEME_COLOR_MAP["#2a2a2a"], LIGHT_THEME_COLOR_MAP["#1a1a1a"]
    assert internal != external
    assert internal in result and external in result


def test_apply_light_theme_leaves_unrelated_code_unchanged():
    code = "graph TD; A-->B;"
    assert apply_light_theme(code) == code


def test_light_theme_css_overrides_cluster_rect():
    assert ".cluster rect" in LIGHT_THEME_CSS
    assert "!important" in LIGHT_THEME_CSS
