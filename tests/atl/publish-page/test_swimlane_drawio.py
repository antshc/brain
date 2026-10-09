import xml.etree.ElementTree as ET

import pytest

from page_diagrams.swimlane_drawio import convert


def _cells(xml_text: str) -> list[ET.Element]:
    root = ET.fromstring(xml_text)
    return root.findall(".//mxCell")


def _cell(xml_text: str, cell_id: str) -> ET.Element:
    for cell in _cells(xml_text):
        if cell.get("id") == cell_id:
            return cell
    raise AssertionError(f"no mxCell with id {cell_id!r} in output")


_ONE_LANE_TEMPLATE = "swimlane-beta TB\n  subgraph a [A]\n    {node}\n  end\n"


@pytest.mark.parametrize(
    "node_decl,node_id,expected_style_fragment",
    [
        ("start([Start])", "start", "shape=mxgraph.flowchart.start_1"),
        ("stepA[Do it]", "stepA", "rounded=1"),
        ("valid{OK?}", "valid", "rhombus"),
        ("sub[[Nested]]", "sub", "shape=process"),
        ("store[(Data)]", "store", "shape=mxgraph.flowchart.database"),
        ("io[/Payload/]", "io", "shape=parallelogram"),
    ],
)
def test_convert_maps_each_supported_shape(node_decl, node_id, expected_style_fragment):
    xml_text = convert(_ONE_LANE_TEMPLATE.format(node=node_decl))
    cell = _cell(xml_text, node_id)
    assert expected_style_fragment in cell.get("style")


def test_convert_orders_lanes_by_declaration():
    code = (
        "swimlane-beta TB\n"
        "  subgraph one [First]\n    a([Start])\n  end\n"
        "  subgraph two [Second]\n    b([Start])\n  end\n"
        "  subgraph three [Third]\n    c([Start])\n  end\n"
    )
    xml_text = convert(code)
    lanes = [cell for cell in _cells(xml_text) if cell.get("id", "").startswith("lane-")]
    lanes_by_x = sorted(lanes, key=lambda cell: float(cell.find("mxGeometry").get("x")))
    assert [lane.get("value") for lane in lanes_by_x] == ["First", "Second", "Third"]


@pytest.mark.parametrize("orientation", ["LR", "RL", "BT"])
def test_convert_rejects_unsupported_orientations(orientation):
    code = f"swimlane-beta {orientation}\n  subgraph a [A]\n    start([Start])\n  end\n"
    with pytest.raises(ValueError, match=orientation):
        convert(code)


def test_convert_defaults_to_tb_when_orientation_omitted():
    code = "swimlane-beta\n  subgraph a [A]\n    start([Start])\n  end\n"
    convert(code)  # does not raise


def test_convert_rejects_non_swimlane_input():
    with pytest.raises(ValueError, match="swimlane-beta"):
        convert("flowchart TD\n  a --> b\n")


def test_convert_splits_a_handoff_chain_into_individual_edges():
    code = (
        "swimlane-beta TB\n"
        "  subgraph a [A]\n"
        "    start([Start])\n"
        "    step[Step]\n"
        "    endNode([End])\n"
        "  end\n"
        "  start --> step --> endNode\n"
    )
    xml_text = convert(code)
    edges = [cell for cell in _cells(xml_text) if cell.get("edge") == "1"]
    pairs = [(edge.get("source"), edge.get("target")) for edge in edges]
    assert pairs == [("start", "step"), ("step", "endNode")]


def test_convert_attaches_edge_labels_as_child_cells():
    code = (
        "swimlane-beta TB\n"
        "  subgraph a [A]\n"
        "    valid{Valid?}\n"
        "    result[/Result/]\n"
        "  end\n"
        "  valid -->|invalid| result\n"
    )
    xml_text = convert(code)
    edges = [cell for cell in _cells(xml_text) if cell.get("edge") == "1"]
    assert len(edges) == 1
    edge_id = edges[0].get("id")
    label_cell = _cell(xml_text, f"{edge_id}-label")
    assert label_cell.get("value") == "invalid"
    assert label_cell.get("parent") == edge_id


def test_convert_raises_on_edge_to_undeclared_node():
    code = "swimlane-beta TB\n  subgraph a [A]\n    start([Start])\n  end\n  start --> missing\n"
    with pytest.raises(ValueError, match="missing"):
        convert(code)


def test_convert_keeps_flow_order_across_a_retry_back_edge():
    # b <-> c is a retry loop (decision sends back to the step it gates); it must not push
    # nodes declared before the loop below nodes that are actually reached after it.
    code = (
        "swimlane-beta TB\n"
        "  subgraph a [A]\n    start([Start])\n    b[Retry step]\n    d[After loop]\n  end\n"
        "  subgraph e [E]\n    c{OK?}\n  end\n"
        "  start --> b\n"
        "  b --> c\n"
        "  c -->|no| b\n"
        "  c -->|yes| d\n"
    )
    xml_text = convert(code)
    y = {
        node_id: float(_cell(xml_text, node_id).find("mxGeometry").get("y"))
        for node_id in ("start", "b", "c", "d")
    }
    assert y["start"] < y["b"] < y["c"] < y["d"]


def test_convert_uses_a_uniform_lane_width_sized_to_the_longest_label():
    code = (
        "swimlane-beta TB\n"
        "  subgraph a [A]\n    short[Go]\n  end\n"
        "  subgraph b [B]\n    long[This is a much longer process label]\n  end\n"
    )
    xml_text = convert(code)
    lanes = [cell for cell in _cells(xml_text) if cell.get("id", "").startswith("lane-")]
    widths = {float(lane.find("mxGeometry").get("width")) for lane in lanes}
    assert len(widths) == 1  # uniform across all lanes
    lane_width = widths.pop()

    long_node = _cell(xml_text, "long")
    assert float(long_node.find("mxGeometry").get("width")) > float(_cell(xml_text, "short").find("mxGeometry").get("width"))
    assert lane_width > 160  # grown past the minimum by the long label


def test_convert_grows_node_height_for_a_long_wrapped_label():
    short_code = _ONE_LANE_TEMPLATE.format(node="a[Short]")
    long_code = _ONE_LANE_TEMPLATE.format(node="a[This label is long enough to wrap onto more than one line]")

    short_height = float(_cell(convert(short_code), "a").find("mxGeometry").get("height"))
    long_height = float(_cell(convert(long_code), "a").find("mxGeometry").get("height"))
    assert long_height > short_height


def test_convert_recolors_default_classdef_through_the_light_theme_map():
    code = (
        "swimlane-beta TB\n"
        "  subgraph a [A]\n    start([Start])\n  end\n"
        "  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px\n"
    )
    xml_text = convert(code)
    assert "#242424" not in xml_text and "#f6f8fa" in xml_text
    assert "#8b949e" not in xml_text and "#57606a" in xml_text
    assert "#c9d1d9" not in xml_text and "#24292f" in xml_text


def test_convert_applies_delta_class_override_to_a_single_node():
    code = (
        "swimlane-beta TB\n"
        "  subgraph a [A]\n    added[New step]\n    plain[Old step]\n  end\n"
        "  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9\n"
        "  classDef added stroke:#4a7a5a\n"
        "  class added added\n"
    )
    xml_text = convert(code)
    added_cell = _cell(xml_text, "added")
    plain_cell = _cell(xml_text, "plain")
    assert "strokeColor=#1a7f37" in added_cell.get("style")
    assert "strokeColor=#57606a" in plain_cell.get("style")
