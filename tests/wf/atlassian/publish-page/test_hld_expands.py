from __future__ import annotations

import re
from pathlib import Path

from atl_cli.page_diagrams.adf import substitute_media
from atl_cli.page_diagrams.mermaid import extract_mermaid
from atl_cli.page_diagrams.pipeline import convert_markdown_to_adf


def test_instantiated_hld_keeps_requirements_and_all_diagrams_inside_expands():
    template = (Path(__file__).resolve().parents[4] / "plugins/wf/skills/design/templates/design-template.md").read_text()
    markdown = template.split("````markdown\n", 1)[1].split("\n````", 1)[0]
    diagram = "```mermaid\nflowchart TD\n    A --> B\n```"
    for placeholder in ("architectureRepresentationDiagram", "crossDeployableFlowDiagram", "functionalSliceBehaviorDiagram", "artifactSpecificContent"):
        markdown = markdown.replace("{{" + placeholder + "}}", diagram)
    markdown = re.sub(r"\{\{.*?\}\}", "Example", markdown)
    processed, diagrams = extract_mermaid(markdown)
    adf = convert_markdown_to_adf(processed)
    adf, count = substitute_media(adf, {str(item["index"]): f"file-{item['index']}" for item in diagrams}, "100")
    assert count == 4
    media_expands = []
    requirements_tables = []

    def walk(node, expands=()):
        if node.get("type") == "expand":
            expands = (*expands, node["attrs"]["title"])
        if node.get("type") == "media":
            media_expands.append(expands)
        if node.get("type") == "table" and "Requirements" in expands:
            requirements_tables.append(node)
        for child in node.get("content", []):
            walk(child, expands)

    walk(adf)
    assert len(media_expands) == 4
    assert all(media_expands)
    assert len(requirements_tables) == 1
