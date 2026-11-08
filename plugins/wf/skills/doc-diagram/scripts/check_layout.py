#!/usr/bin/env python3
"""Render Mermaid behavior diagrams with mermaid-cli and check rendered element order follows the flow."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from pathlib import Path

MMDC = ["npx", "-y", "@mermaid-js/mermaid-cli"]
SVG_ID = "my-svg"
TOLERANCE = 1.0
FENCE = re.compile(r"^```mermaid\s*\n(.*?)^```", re.MULTILINE | re.DOTALL)
DIAGRAM_ID = re.compile(r"^\s*%%\s*diagram-id:\s*(\S+)", re.MULTILINE)
HEADER = re.compile(r"^\s*(flowchart|graph|swimlane-beta|sequenceDiagram)\b[ \t]*(\w+)?", re.MULTILINE)
STEP = re.compile(r"^\s*(\d+(?:[a-z]\.\d+)*)\s+-\s")
TRANSLATE = re.compile(r"translate\(\s*([-\d.e]+)[ ,]+([-\d.e]+)\s*\)")
EDGE_ID = re.compile(rf"^{SVG_ID}-L_(.+)_\d+$")
NODE_ID = re.compile(rf"^{SVG_ID}-(?:flowchart-)?(.+)-\d+$")
SVG_NS = "{http://www.w3.org/2000/svg}"


@dataclass(frozen=True)
class Diagram:
    name: str
    source: str


@dataclass(frozen=True)
class Node:
    node_id: str
    label: str
    position: float
    step: str | None


def extract_diagrams(path: Path) -> list[Diagram]:
    text = path.read_text(encoding="utf-8")
    if path.suffix != ".md":
        return [Diagram(path.name, text)]
    diagrams = []
    for index, match in enumerate(FENCE.finditer(text), start=1):
        source = match.group(1)
        id_match = DIAGRAM_ID.search(source)
        diagrams.append(Diagram(id_match.group(1) if id_match else f"block-{index}", source))
    return diagrams


def render(source: str, work_dir: Path) -> tuple[str | None, str]:
    input_path = work_dir / "diagram.mmd"
    output_path = work_dir / "diagram.svg"
    input_path.write_text(source, encoding="utf-8")
    result = subprocess.run(
        [*MMDC, "-q", "-i", str(input_path), "-o", str(output_path), "--svgId", SVG_ID],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None, (result.stderr or result.stdout).strip()
    return output_path.read_text(encoding="utf-8"), ""


def flow_axis(source: str) -> tuple[str, str] | None:
    """Return (diagram kind, axis) where axis is 'y' or 'x'; None when not a flowchart-like diagram."""
    match = HEADER.search(source)
    if not match or match.group(1) == "sequenceDiagram":
        return None
    direction = (match.group(2) or "TB").upper()
    if direction in ("TB", "TD"):
        return match.group(1), "y"
    if direction == "LR":
        return match.group(1), "x"
    raise ValueError(f"unsupported direction {direction}; use TD, TB, or LR")


def parse_svg(svg: str, axis: str) -> tuple[dict[str, Node], list[tuple[str, str]]]:
    root = ElementTree.fromstring(svg)
    nodes: dict[str, Node] = {}
    for group in root.iter(f"{SVG_NS}g"):
        if "node" not in group.get("class", "").split():
            continue
        id_match = NODE_ID.match(group.get("id", ""))
        position_match = TRANSLATE.search(group.get("transform", ""))
        if not id_match or not position_match:
            continue
        label = " ".join("".join(group.itertext()).split())
        step_match = STEP.match(label)
        x, y = (float(value) for value in position_match.groups())
        nodes[id_match.group(1)] = Node(
            id_match.group(1), label, y if axis == "y" else x, step_match.group(1) if step_match else None
        )

    edges: list[tuple[str, str]] = []
    for path in root.iter(f"{SVG_NS}path"):
        edge_match = EDGE_ID.match(path.get("id", ""))
        if edge_match:
            edge = split_edge(edge_match.group(1), nodes)
            if edge:
                edges.append(edge)
    return nodes, edges


def split_edge(body: str, nodes: dict[str, Node]) -> tuple[str, str] | None:
    for index in range(1, len(body)):
        if body[index] == "_" and body[:index] in nodes and body[index + 1:] in nodes:
            return body[:index], body[index + 1:]
    return None


def parent_step(step: str) -> str | None:
    """Predecessor of a hierarchical step number: 3 -> 2, 2a.1 -> 2, 2a.2 -> 2a.1."""
    head, _, last = step.rpartition(".")
    if not head:
        return str(int(step) - 1) if int(step) > 1 else None
    if int(last) > 1:
        return f"{head}.{int(last) - 1}"
    return head[:-1]


def find_cycle(nodes: dict[str, Node], edges: list[tuple[str, str]]) -> list[str] | None:
    graph: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for source, target in edges:
        graph[source].append(target)
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node_id: str) -> list[str] | None:
        state[node_id] = 1
        stack.append(node_id)
        for target in graph[node_id]:
            if state.get(target) == 1:
                return stack[stack.index(target):] + [target]
            if target not in state:
                cycle = visit(target)
                if cycle:
                    return cycle
        stack.pop()
        state[node_id] = 2
        return None

    for node_id in graph:
        if node_id not in state:
            cycle = visit(node_id)
            if cycle:
                return cycle
    return None


def check_order(nodes: dict[str, Node], edges: list[tuple[str, str]]) -> list[str]:
    problems: list[str] = []
    cycle = find_cycle(nodes, edges)
    if cycle:
        problems.append(f"cycle: {' -> '.join(cycle)}; draw the loop-back as a terminal connector node")

    with_incoming = {target for _, target in edges}
    with_outgoing = {source for source, _ in edges}
    starts = [node for node in nodes.values() if node.node_id not in with_incoming and node.node_id in with_outgoing]
    if len(starts) != 1:
        problems.append(f"expected exactly one start node, found {[node.node_id for node in starts]}")
    lowest = min(node.position for node in nodes.values())
    for start in starts:
        if start.position > lowest + TOLERANCE:
            problems.append(f"start node '{start.label}' is not first in the flow direction")

    for source, target in edges:
        if nodes[target].position < nodes[source].position - TOLERANCE:
            problems.append(f"edge runs against flow: '{nodes[source].label}' -> '{nodes[target].label}'")

    by_step = {node.step: node for node in nodes.values() if node.step}
    for step, node in by_step.items():
        parent = parent_step(step)
        if parent in by_step and node.position < by_step[parent].position - TOLERANCE:
            problems.append(f"step {step} renders before its predecessor {parent}")
    return problems


def check_diagram(diagram: Diagram, work_dir: Path) -> list[str]:
    try:
        flow = flow_axis(diagram.source)
    except ValueError as exception:
        return [str(exception)]
    svg, error = render(diagram.source, work_dir)
    if svg is None:
        return [f"render failed: {error}"]
    if flow is None:
        return []
    nodes, edges = parse_svg(svg, flow[1])
    if not nodes:
        return ["no nodes found in rendered SVG"]
    return check_order(nodes, edges)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help=".mmd file, or .md file whose mermaid blocks are all checked")
    args = parser.parse_args()

    diagrams = extract_diagrams(args.path)
    if not diagrams:
        print(f"no mermaid diagrams in {args.path}", file=sys.stderr)
        return 1

    failed = False
    with tempfile.TemporaryDirectory() as work_dir:
        for diagram in diagrams:
            problems = check_diagram(diagram, Path(work_dir))
            if problems:
                failed = True
                print(f"FAIL {diagram.name}", file=sys.stderr)
                for problem in problems:
                    print(f"  - {problem}", file=sys.stderr)
            else:
                print(f"OK   {diagram.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
