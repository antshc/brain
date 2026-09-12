"""Integration test for the swimlane-beta-to-drawio converter against the full reference
diagram in docs/ongoing/swimlane.mmd, embedded here so the test doesn't depend on that file
changing independently of this converter.
"""
import xml.etree.ElementTree as ET

from page_diagrams.swimlane_drawio import convert

_SWIMLANE_MMD = """\
%%{init: {'themeVariables': {'lineColor': '#8b949e'}}}%%
%% diagram-id: order-fulfillment-solution-responsibility
swimlane-beta TB
  accTitle: Order fulfillment ownership
  accDescr: Shows responsibility moving from the customer to the order service and order database.

  subgraph customer [Customer]
    start([Start])
    submit[/Place order/]
    result[/Confirmation or error/]
    endNode([End])
  end

  subgraph restApi [Order Service - REST API]
    validate[Validate order]
    valid{Order valid and in stock?}
    payment[[Process payment]]
  end

  subgraph database [Order Database - Database]
    persistOrder[(Order database)]
  end

  start --> submit -->|order request| validate --> valid
  valid -->|invalid| result
  valid -->|valid| payment --> persistOrder --> result --> endNode

  classDef default fill:#242424,stroke:#8b949e,color:#c9d1d9,stroke-width:1px
"""


def test_convert_full_order_fulfillment_reference_diagram():
    xml_text = convert(_SWIMLANE_MMD)
    root = ET.fromstring(xml_text)
    cells = {cell.get("id"): cell for cell in root.findall(".//mxCell")}

    lanes = [cell for cell_id, cell in cells.items() if cell_id.startswith("lane-")]
    lanes_by_x = sorted(lanes, key=lambda cell: float(cell.find("mxGeometry").get("x")))
    assert [lane.get("value") for lane in lanes_by_x] == [
        "Customer",
        "Order Service - REST API",
        "Order Database - Database",
    ]

    expected_nodes = {
        "start": ("shape=mxgraph.flowchart.start_1", "lane-customer"),
        "submit": ("shape=parallelogram", "lane-customer"),
        "result": ("shape=parallelogram", "lane-customer"),
        "endNode": ("shape=mxgraph.flowchart.start_1", "lane-customer"),
        "validate": ("rounded=1", "lane-restApi"),
        "valid": ("rhombus", "lane-restApi"),
        "payment": ("shape=process", "lane-restApi"),
        "persistOrder": ("shape=mxgraph.flowchart.database", "lane-database"),
    }
    for node_id, (style_fragment, expected_parent) in expected_nodes.items():
        cell = cells[node_id]
        assert style_fragment in cell.get("style")
        assert cell.get("parent") == expected_parent

    edges = [cell for cell in root.findall(".//mxCell") if cell.get("edge") == "1"]
    pairs = [(edge.get("source"), edge.get("target")) for edge in edges]
    assert pairs == [
        ("start", "submit"),
        ("submit", "validate"),
        ("validate", "valid"),
        ("valid", "result"),
        ("valid", "payment"),
        ("payment", "persistOrder"),
        ("persistOrder", "result"),
        ("result", "endNode"),
    ]

    labels = {
        cell.get("value")
        for cell in root.findall(".//mxCell")
        if cell.get("style", "").startswith("edgeLabel")
    }
    assert labels == {"order request", "invalid", "valid"}

    assert "#242424" not in xml_text and "#f6f8fa" in xml_text
    assert "#8b949e" not in xml_text and "#57606a" in xml_text
    assert "#c9d1d9" not in xml_text and "#24292f" in xml_text
