"""Top-level ADF document assembly (pure): wires parsed blocks + media fileIds together."""
from __future__ import annotations

from .blocks import parse_blocks


def build_adf_doc(processed_md: str, file_ids_by_index: dict[int, str], image_width: int = 768) -> dict:
    lines = processed_md.splitlines()
    content = parse_blocks(lines, file_ids_by_index, image_width=image_width)
    return {"version": 1, "type": "doc", "content": content}


def wire_media_ids(diagrams: list[dict], filename_to_file_id: dict[str, str]) -> dict[int, str]:
    return {d["index"]: filename_to_file_id[d["filename"]] for d in diagrams}
