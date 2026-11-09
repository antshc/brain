"""Converts a Mermaid `swimlane-beta TB`/`TD` diagram into draw.io `mxfile` XML.

Supports exactly the node vocabulary in `swimlane-diagram-template.md` (start/end, process,
decision, subprocess, data store, input/output), lanes as top-level `subgraph`s, `-->` handoff
chains with optional `|label|`s, and `classDef default`/`classDef added|removed` + `class id
className` delta styling. Everything else (nested subgraphs, LR/RL/BT orientation, exotic
shapes, `click`) is out of scope and either ignored or raises `ValueError`.

Layout auto-scales: node width/height grow with label length, lane width is the widest node
across all lanes (uniform, so the pool looks even), and node row/height uses each node's
longest-path depth in the handoff graph so downstream steps always sit below their sources.
Colors are recolored through `theme.LIGHT_THEME_COLOR_MAP`, matching the Confluence-friendly
palette the PNG/Draw.io renderers already use.
"""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from collections import deque
from dataclasses import dataclass, field

from .theme import LIGHT_THEME_COLOR_MAP

# ── Mermaid grammar ──────────────────────────────────────────────────────────────

_HEADER_RE = re.compile(r"^swimlane-beta(?:\s+(\S+))?$")
_SUBGRAPH_RE = re.compile(r"^subgraph\s+(\w+)\s*\[(.+)\]\s*$")
_CLASSDEF_RE = re.compile(r"^classDef\s+(\w+)\s+(.+)$")
_CLASS_ASSIGN_RE = re.compile(r"^class\s+(\w+)\s+(\w+);?$")
_SKIP_LINE_RE = re.compile(r"^(%%|accTitle:|accDescr:)")

_SUPPORTED_ORIENTATIONS = ("TB", "TD")

# Longest/most specific bracket pair first — `[Text]` (process) must be tried last, since
# it would otherwise also match the inner brackets of `[[Text]]`, `[(Text)]`, and `[/Text/]`.
_NODE_PATTERNS = (
    ("start_end", re.compile(r"^(\w+)\(\[(.+?)\]\)$")),
    ("subprocess", re.compile(r"^(\w+)\[\[(.+?)\]\]$")),
    ("data_store", re.compile(r"^(\w+)\[\((.+?)\)\]$")),
    ("io", re.compile(r"^(\w+)\[/(.+?)/\]$")),
    ("decision", re.compile(r"^(\w+)\{(.+?)\}$")),
    ("process", re.compile(r"^(\w+)\[(.+?)\]$")),
)

_EDGE_TOKEN_RE = re.compile(r"\w+|-->|\|[^|]*\|")

_SHAPE_STYLES = {
    "start_end": "shape=mxgraph.flowchart.start_1;whiteSpace=wrap;html=1;aspect=fixed;",
    "process": "rounded=1;whiteSpace=wrap;html=1;",
    "decision": "rhombus;whiteSpace=wrap;html=1;",
    "subprocess": "shape=process;whiteSpace=wrap;rounded=1;html=1;",
    "data_store": "shape=mxgraph.flowchart.database;whiteSpace=wrap;html=1;",
    "io": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;rounded=1;html=1;",
}

# (width, height) before label-driven growth.
_SHAPE_BASE_SIZE = {
    "start_end": (50, 30),
    "process": (100, 60),
    "decision": (100, 75),
    "subprocess": (100, 60),
    "data_store": (100, 50),
    "io": (100, 46),
}

_DEFAULT_DARK_STYLE = {"fill": "#242424", "stroke": "#8b949e", "color": "#c9d1d9"}

# ── Layout constants ─────────────────────────────────────────────────────────────

_CHAR_WIDTH_PX = 7
_LABEL_PADDING_PX = 24
_MAX_NODE_WIDTH = 220
_LINE_HEIGHT_PX = 16
_MIN_ROW_HEIGHT = 30
_ROW_GAP = 40
_LANE_HEADER = 20
_LANE_PADDING_TOP = 40
_LANE_PADDING_BOTTOM = 40
_LANE_PADDING_SIDE = 20
_MIN_LANE_WIDTH = 160


@dataclass
class _Lane:
    id: str
    label: str
    order: int
    width: float = 0
    height: float = 0


@dataclass
class _Node:
    id: str
    label: str
    shape: str
    lane_id: str
    order: int
    class_name: str | None = None
    width: float = 0
    height: float = 0
    x: float = 0
    y: float = 0
    row: int = 0


@dataclass
class _Edge:
    source: str
    target: str
    label: str | None = None


@dataclass
class _Diagram:
    lanes: list[_Lane] = field(default_factory=list)
    nodes: dict[str, _Node] = field(default_factory=dict)
    edges: list[_Edge] = field(default_factory=list)
    class_defs: dict[str, dict[str, str]] = field(default_factory=dict)


def convert(code: str) -> str:
    """Mermaid `swimlane-beta` source to a pretty-printed draw.io `mxfile` XML string."""
    diagram = _parse(code)
    _layout(diagram)
    tree = _build_xml(diagram)
    ET.indent(tree, space="  ")
    return ET.tostring(tree, encoding="unicode", xml_declaration=True)


# ── Parsing ──────────────────────────────────────────────────────────────────────


def _parse(code: str) -> _Diagram:
    lines = [line.strip() for line in code.splitlines()]
    lines = [line for line in lines if line and not _SKIP_LINE_RE.match(line)]
    if lines and lines[0].startswith("%%{"):
        lines = lines[1:]

    header_index = next((i for i, line in enumerate(lines) if _HEADER_RE.match(line)), None)
    if header_index is None:
        raise ValueError("not a swimlane-beta diagram: missing `swimlane-beta` header")
    orientation = _HEADER_RE.match(lines[header_index]).group(1) or "TB"
    if orientation not in _SUPPORTED_ORIENTATIONS:
        raise ValueError(
            f"unsupported swimlane-beta orientation {orientation!r}; "
            f"only {'/'.join(_SUPPORTED_ORIENTATIONS)} are supported"
        )

    diagram = _Diagram()
    current_lane: str | None = None
    for line in lines[header_index + 1 :]:
        if line == "end":
            current_lane = None
            continue

        subgraph_match = _SUBGRAPH_RE.match(line)
        if subgraph_match:
            lane_id, lane_label = subgraph_match.groups()
            diagram.lanes.append(_Lane(id=lane_id, label=lane_label, order=len(diagram.lanes)))
            current_lane = lane_id
            continue

        classdef_match = _CLASSDEF_RE.match(line)
        if classdef_match:
            class_name, styles_text = classdef_match.groups()
            diagram.class_defs[class_name] = _parse_style_pairs(styles_text)
            continue

        class_assign_match = _CLASS_ASSIGN_RE.match(line)
        if class_assign_match:
            node_id, class_name = class_assign_match.groups()
            if node_id in diagram.nodes:
                diagram.nodes[node_id].class_name = class_name
            continue

        if current_lane is not None:
            node = _parse_node(line, current_lane, len(diagram.nodes))
            if node is not None:
                diagram.nodes[node.id] = node
                continue

        if "-->" in line:
            diagram.edges.extend(_parse_edge_chain(line))

    return diagram


def _parse_style_pairs(text: str) -> dict[str, str]:
    styles: dict[str, str] = {}
    for part in text.split(","):
        key, _, value = part.strip().partition(":")
        key = key.strip()
        if key in ("fill", "stroke", "color"):
            styles[key] = value.strip()
    return styles


def _parse_node(line: str, lane_id: str, order: int) -> _Node | None:
    for shape, pattern in _NODE_PATTERNS:
        match = pattern.match(line)
        if match:
            node_id, label = match.groups()
            return _Node(id=node_id, label=label, shape=shape, lane_id=lane_id, order=order)
    return None


def _parse_edge_chain(line: str) -> list[_Edge]:
    tokens = _EDGE_TOKEN_RE.findall(line)
    edges: list[_Edge] = []
    if not tokens:
        return edges
    previous = tokens[0]
    i = 1
    while i < len(tokens):
        if tokens[i] != "-->":
            raise ValueError(f"cannot parse handoff line: {line!r}")
        i += 1
        label: str | None = None
        if i < len(tokens) and tokens[i].startswith("|"):
            label = tokens[i][1:-1].strip()
            i += 1
        if i >= len(tokens):
            raise ValueError(f"cannot parse handoff line: {line!r}")
        target = tokens[i]
        i += 1
        edges.append(_Edge(source=previous, target=target, label=label))
        previous = target
    return edges


# ── Layout ───────────────────────────────────────────────────────────────────────


def _layout(diagram: _Diagram) -> None:
    for node in diagram.nodes.values():
        node.width, node.height = _node_size(node.shape, node.label)

    depths = _compute_depths(diagram.nodes, diagram.edges)
    _assign_rows(diagram.lanes, diagram.nodes, depths)

    total_rows = max((node.row for node in diagram.nodes.values()), default=-1) + 1
    row_height = [_MIN_ROW_HEIGHT] * total_rows
    for node in diagram.nodes.values():
        row_height[node.row] = max(row_height[node.row], node.height)

    row_y: list[float] = []
    offset = _LANE_HEADER + _LANE_PADDING_TOP
    for height in row_height:
        row_y.append(offset)
        offset += height + _ROW_GAP
    content_bottom = offset - _ROW_GAP if row_height else offset

    lane_width = max(
        (node.width for node in diagram.nodes.values()), default=_MIN_LANE_WIDTH - 2 * _LANE_PADDING_SIDE
    ) + 2 * _LANE_PADDING_SIDE
    lane_width = max(lane_width, _MIN_LANE_WIDTH)
    lane_height = content_bottom + _LANE_PADDING_BOTTOM

    for node in diagram.nodes.values():
        node.x = (lane_width - node.width) / 2
        node.y = row_y[node.row] + (row_height[node.row] - node.height) / 2

    for lane in diagram.lanes:
        lane.width = lane_width
        lane.height = lane_height


def _node_size(shape: str, label: str) -> tuple[float, float]:
    base_width, base_height = _SHAPE_BASE_SIZE[shape]
    raw_width = len(label) * _CHAR_WIDTH_PX + _LABEL_PADDING_PX
    width = min(max(base_width, raw_width), _MAX_NODE_WIDTH)
    chars_per_line = max(1, (width - _LABEL_PADDING_PX) // _CHAR_WIDTH_PX)
    lines = max(1, math.ceil(len(label) / chars_per_line))
    height = base_height + (lines - 1) * _LINE_HEIGHT_PX
    return width, height


def _compute_depths(nodes: dict[str, _Node], edges: list[_Edge]) -> dict[str, int]:
    """Longest-path depth per node, so a target always lands below every source that reaches it."""
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    indegree: dict[str, int] = {node_id: 0 for node_id in nodes}
    for edge in edges:
        if edge.source not in nodes or edge.target not in nodes:
            raise ValueError(f"handoff references an undeclared node: {edge.source} --> {edge.target}")
        adjacency[edge.source].append(edge.target)
        indegree[edge.target] += 1

    depth = {node_id: 0 for node_id in nodes}
    remaining_indegree = dict(indegree)
    order = {node_id: node.order for node_id, node in nodes.items()}
    unresolved = set(nodes)
    queue = deque(sorted((n for n in unresolved if remaining_indegree[n] == 0), key=order.__getitem__))
    while unresolved:
        if not queue:
            # A retry/back-edge loop leaves a cycle with no zero-indegree node; break it by
            # forcing the node closest to resolved (fewest remaining incoming edges) next, so
            # its depth is still driven by whichever forward edges have already been processed.
            queue.append(min(unresolved, key=lambda n: (remaining_indegree[n], order[n])))
        current = queue.popleft()
        if current not in unresolved:
            continue
        unresolved.discard(current)
        for target in adjacency[current]:
            if target not in unresolved:
                continue  # a retry back-edge into an already-placed node; ignore for depth ordering
            depth[target] = max(depth[target], depth[current] + 1)
            remaining_indegree[target] -= 1
            if remaining_indegree[target] <= 0:
                queue.append(target)
    return depth


def _assign_rows(lanes: list[_Lane], nodes: dict[str, _Node], depths: dict[str, int]) -> None:
    used_rows: dict[str, set[int]] = {lane.id: set() for lane in lanes}
    for node in sorted(nodes.values(), key=lambda n: (depths[n.id], n.order)):
        row = depths[node.id]
        occupied = used_rows[node.lane_id]
        while row in occupied:
            row += 1
        occupied.add(row)
        node.row = row


# ── Theming ──────────────────────────────────────────────────────────────────────


def _resolve_node_style(diagram: _Diagram, node: _Node) -> dict[str, str]:
    style = dict(diagram.class_defs.get("default", _DEFAULT_DARK_STYLE))
    if node.class_name:
        style.update(diagram.class_defs.get(node.class_name, {}))
    return {key: LIGHT_THEME_COLOR_MAP.get(value, value) for key, value in style.items()}


def _resolve_edge_stroke(diagram: _Diagram) -> str:
    default_style = diagram.class_defs.get("default", _DEFAULT_DARK_STYLE)
    stroke = default_style.get("stroke", _DEFAULT_DARK_STYLE["stroke"])
    return LIGHT_THEME_COLOR_MAP.get(stroke, stroke)


# ── XML emission ─────────────────────────────────────────────────────────────────


def _build_xml(diagram: _Diagram) -> ET.Element:
    mxfile = ET.Element("mxfile", host="app.diagrams.net")
    diagram_el = ET.SubElement(mxfile, "diagram", id="swimlane-diagram", name="Page-1")
    page_width = diagram.lanes[0].width * len(diagram.lanes) if diagram.lanes else 0
    page_height = diagram.lanes[0].height if diagram.lanes else 0
    graph_model = ET.SubElement(
        diagram_el,
        "mxGraphModel",
        dx="800",
        dy="600",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth=str(int(page_width)),
        pageHeight=str(int(page_height)),
        background="none",
        math="0",
        shadow="0",
    )
    root = ET.SubElement(graph_model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    for lane in diagram.lanes:
        lane_cell = ET.SubElement(
            root,
            "mxCell",
            id=_lane_cell_id(lane.id),
            parent="1",
            style="swimlane;html=1;startSize=20;fontStyle=0;strokeColor=#57606A;fontColor=#24292f;",
            value=lane.label,
            vertex="1",
        )
        ET.SubElement(
            lane_cell,
            "mxGeometry",
            x=str(int(lane.order * lane.width)),
            y="0",
            width=str(int(lane.width)),
            height=str(int(lane.height)),
        ).set("as", "geometry")

    for node in diagram.nodes.values():
        style_colors = _resolve_node_style(diagram, node)
        style = (
            _SHAPE_STYLES[node.shape]
            + f"fillColor={style_colors.get('fill', '')};"
            + f"strokeColor={style_colors.get('stroke', '')};"
            + f"fontColor={style_colors.get('color', '')};"
        )
        node_cell = ET.SubElement(
            root,
            "mxCell",
            id=node.id,
            parent=_lane_cell_id(node.lane_id),
            style=style,
            value=node.label,
            vertex="1",
        )
        ET.SubElement(
            node_cell,
            "mxGeometry",
            x=str(int(node.x)),
            y=str(int(node.y)),
            width=str(int(node.width)),
            height=str(int(node.height)),
        ).set("as", "geometry")

    edge_stroke = _resolve_edge_stroke(diagram)
    lane_order = {lane.id: lane.order for lane in diagram.lanes}
    for index, edge in enumerate(diagram.edges):
        edge_id = f"edge-{index}"
        source_node = diagram.nodes[edge.source]
        anchor_style = (
            _edge_anchor_style(lane_order[source_node.lane_id], lane_order[diagram.nodes[edge.target].lane_id])
            if source_node.shape == "decision"
            else ""
        )
        edge_cell = ET.SubElement(
            root,
            "mxCell",
            id=edge_id,
            parent="1",
            source=edge.source,
            target=edge.target,
            edge="1",
            style=(
                "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
                f"endArrow=classicThin;endFill=1;strokeColor={edge_stroke};{anchor_style}"
            ),
        )
        ET.SubElement(edge_cell, "mxGeometry", relative="1").set("as", "geometry")
        if edge.label:
            label_cell = ET.SubElement(
                root,
                "mxCell",
                id=f"{edge_id}-label",
                parent=edge_id,
                style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;",
                value=edge.label,
                vertex="1",
                connectable="0",
            )
            ET.SubElement(label_cell, "mxGeometry", relative="1").set("as", "geometry")

    return mxfile


def _edge_anchor_style(source_lane_order: int, target_lane_order: int) -> str:
    """Fixed exit side so multiple edges out of one node don't stack on the same corner.

    Same lane: exit the bottom. Target lane to the right/left: exit through the facing side.
    The entry side is left for draw.io to pick, so the arrow still lands on whichever face of
    the target is closest instead of a side that may not face the source.
    """
    if target_lane_order > source_lane_order:
        exit_x, exit_y = 1, 0.5
    elif target_lane_order < source_lane_order:
        exit_x, exit_y = 0, 0.5
    else:
        exit_x, exit_y = 0.5, 1
    return f"exitX={exit_x};exitY={exit_y};exitDx=0;exitDy=0;"


def _lane_cell_id(lane_id: str) -> str:
    return f"lane-{lane_id}"
