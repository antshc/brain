"""Read-only stdlib traversal of graphify-out/graph.json for when the graphify module is unavailable."""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path

NOISY_SOURCE_PARTS = ("/test/", "/tests/", "/generated/", "/obj/", "/bin/")
NOISE_PREFIXES = (".artifacts/", "bin/", "obj/", "testresults/", "review_diff/")


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    data: dict


class RawGraph:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.nodes: dict[str, dict] = {node["id"]: node for node in data.get("nodes", [])}
        self.edges = [Edge(e["source"], e["target"], e) for e in data.get("links", data.get("edges", []))]
        self.directed = bool(data.get("directed", True))

    @classmethod
    def load(cls, path: Path) -> RawGraph:
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def label(self, nid: str) -> str:
        return str(self.nodes.get(nid, {}).get("label") or nid)

    def describe(self, nid: str) -> str:
        node = self.nodes.get(nid, {})
        return f"{self.label(nid)} src={node.get('source_file', '')} loc={node.get('source_location', '')}"

    def adjacency(
        self, *, contexts: set[str] | None = None, relations: set[str] | None = None, direction: str = "out",
    ) -> dict[str, list[tuple[str, dict]]]:
        result: dict[str, list[tuple[str, dict]]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            if contexts and (edge.data.get("context") or "") not in contexts:
                continue
            if relations and (edge.data.get("relation") or "") not in relations:
                continue
            if direction in {"out", "both"} or not self.directed:
                result.setdefault(edge.source, []).append((edge.target, edge.data))
            if direction in {"in", "both"} or not self.directed:
                result.setdefault(edge.target, []).append((edge.source, edge.data))
        return result

    def degree(self, nid: str) -> int:
        return sum(1 for edge in self.edges if nid in (edge.source, edge.target))

    def best_match(self, term: str) -> str | None:
        words = term.lower().split()
        scored = [(sum(1 for w in words if w in self.label(nid).lower()), nid) for nid in self.nodes]
        scored.sort(reverse=True)
        return scored[0][1] if scored and scored[0][0] > 0 else None


def health(graph: RawGraph, graph_path: Path) -> str:
    out_dir = graph_path.parent
    root_file = out_dir / ".graphify_root"
    root = root_file.read_text(encoding="utf-8").strip() if root_file.exists() else ""
    commit = str(graph.data.get("built_at_commit") or (graph.data.get("graph") or {}).get("built_at_commit") or "")
    freshness = "unknown"
    if root and commit:
        head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True)
        if head.returncode == 0:
            freshness = "current" if head.stdout.strip().startswith(commit) or commit.startswith(head.stdout.strip()) else "stale"
    sources = [str(node.get("source_file") or "") for node in graph.nodes.values()]
    roots = Counter("/".join(s.split("/")[:2]) for s in sources if s)
    types = Counter(str(node.get("file_type") or "(none)") for node in graph.nodes.values())
    noise = Counter(p for s in sources for p in NOISE_PREFIXES if f"/{p}" in f"/{s.lower()}")
    lines = [
        f"graph: {graph_path} | {len(graph.nodes)} nodes, {len(graph.edges)} edges",
        f"root: {root or '(unknown)'} | built_at_commit: {commit or '(unknown)'} | freshness: {freshness}",
        "source roots: " + ", ".join(f"{r} ({n})" for r, n in roots.most_common(15)),
        "file types: " + ", ".join(f"{t} ({n})" for t, n in types.most_common()),
        "noise: " + (", ".join(f"{p} ({n})" for p, n in noise.most_common()) or "none"),
    ]
    return "\n".join(lines)


def contexts(graph: RawGraph) -> str:
    counts = Counter((edge.data.get("context") or "(none)") for edge in graph.edges)
    return "\n".join(f"{context}\t{count}" for context, count in counts.most_common())


def vocab(graph: RawGraph) -> list[str]:
    tokens: set[str] = set()
    for node in graph.nodes.values():
        for word in re.findall(r"[^\W\d_]+", str(node.get("label") or ""), re.UNICODE):
            for part in re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+", word) or [word]:
                if 3 <= len(part) <= 30:
                    tokens.add(part.lower())
    return sorted(tokens)


def edge_slice(
    graph: RawGraph, label: str, *, source_contains: str = "", contexts_: set[str] | None = None,
    relations: set[str] | None = None, direction: str = "out", max_depth: int = 1,
) -> str:
    candidates = [
        nid for nid, node in graph.nodes.items()
        if node.get("label") == label and source_contains.lower() in str(node.get("source_file") or "").lower()
    ]
    if len(candidates) != 1:
        return "Expected one exact start node; candidates:\n" + "\n".join(graph.describe(n) for n in candidates)
    adjacency = graph.adjacency(contexts=contexts_, relations=relations, direction=direction)
    start = candidates[0]
    distances = {start: 0}
    selected: list[tuple[str, str, dict]] = []
    queue = deque([start])
    while queue:
        source = queue.popleft()
        if distances[source] >= max_depth:
            continue
        for target, data in adjacency.get(source, []):
            selected.append((source, target, data))
            if target not in distances:
                distances[target] = distances[source] + 1
                queue.append(target)
    lines = [f"NODE depth={d} {graph.describe(n)}" for n, d in sorted(distances.items(), key=lambda i: (i[1], graph.label(i[0])))]
    lines += [
        f"EDGE {graph.label(s)} --{d.get('relation', '')} [{d.get('context', '')}]--> {graph.label(t)}"
        for s, t, d in selected
    ]
    return "\n".join(lines)


def traverse(
    graph: RawGraph, question: str, *, dfs: bool = False, contexts_: set[str] | None = None,
    relations: set[str] | None = None, budget: int = 2000,
) -> str:
    terms = [t.lower() for t in question.split() if len(t) >= 3]
    exact_label = question.lower()

    def noisy(nid: str) -> bool:
        source = str(graph.nodes[nid].get("source_file") or "").lower()
        return any(part in source for part in NOISY_SOURCE_PARTS)

    def base_score(nid: str) -> float:
        label = graph.label(nid).lower()
        overlap = sum(1 for t in terms if t in label)
        return (100 if label == exact_label else 0) + overlap * 5 - (20 if noisy(nid) else 0) - min(graph.degree(nid), 100) / 100

    scored = []
    for nid in graph.nodes:
        label = graph.label(nid).lower()
        overlap = sum(1 for t in terms if t in label)
        if overlap:
            scored.append((base_score(nid) + (20 if overlap == len(terms) else 0), nid))
    scored.sort(reverse=True)
    exact = [nid for _, nid in scored if graph.label(nid).lower() == exact_label]
    starts = exact[:1] or [nid for _, nid in scored[:3]]
    if not starts:
        return f"No matching nodes found for query terms: {terms}"

    adjacency = graph.adjacency(contexts=contexts_, relations=relations, direction="out")
    distances: dict[str, int] = {}
    edges: list[tuple[str, str]] = []
    if dfs:
        stack = [(n, 0) for n in reversed(starts)]
        while stack:
            node, depth = stack.pop()
            if node in distances or depth > 6:
                continue
            distances[node] = depth
            for neighbor, _ in adjacency.get(node, []):
                if neighbor not in distances:
                    stack.append((neighbor, depth + 1))
                    edges.append((node, neighbor))
    else:
        distances = {n: 0 for n in starts}
        frontier = set(starts)
        for depth in range(2):
            nxt = set()
            for node in frontier:
                for neighbor, _ in adjacency.get(node, []):
                    if neighbor not in distances:
                        distances[neighbor] = depth + 1
                        nxt.add(neighbor)
                        edges.append((node, neighbor))
            frontier = nxt

    ranked = sorted(distances, key=lambda n: base_score(n) - (0 if dfs else distances[n] * 2), reverse=True)
    edge_data = {(e.source, e.target): e.data for e in graph.edges}
    lines = [f"Traversal: {'DFS' if dfs else 'BFS'} | Start: {[graph.label(n) for n in starts]} | {len(distances)} nodes"]
    lines += [f"  NODE {graph.label(n)} [src={graph.nodes[n].get('source_file', '')} loc={graph.nodes[n].get('source_location', '')}]" for n in ranked]
    for u, v in edges:
        data = edge_data.get((u, v)) or edge_data.get((v, u)) or {}
        lines.append(f"  EDGE {graph.label(u)} --{data.get('relation', '')} [{data.get('confidence', '')}]--> {graph.label(v)}")
    output = "\n".join(lines)
    if len(output) > budget * 4:
        output = output[: budget * 4] + f"\n... (truncated at ~{budget} token budget - use --budget N for more)"
    return output


def shortest_path(graph: RawGraph, a_term: str, b_term: str, *, undirected: bool = False) -> str:
    source, target = graph.best_match(a_term), graph.best_match(b_term)
    if not source or not target:
        return f"Could not find nodes matching: {a_term!r} or {b_term!r}"
    adjacency = graph.adjacency(direction="both" if undirected else "out")
    previous: dict[str, tuple[str, dict] | None] = {source: None}
    queue = deque([source])
    while queue and target not in previous:
        node = queue.popleft()
        for neighbor, data in adjacency.get(node, []):
            if neighbor not in previous:
                previous[neighbor] = (node, data)
                queue.append(neighbor)
    if target not in previous:
        return f"No path found between {a_term!r} and {b_term!r}"
    hops: list[tuple[str, dict | None]] = []
    node: str | None = target
    while node is not None:
        step = previous[node]
        hops.append((node, step[1] if step else None))
        node = step[0] if step else None
    hops.reverse()
    lines = [f"Shortest path ({len(hops) - 1} hops):"]
    for i, (nid, _) in enumerate(hops):
        if i < len(hops) - 1:
            data = hops[i + 1][1] or {}
            lines.append(f"  {graph.label(nid)} --{data.get('relation', '')}--> [{data.get('confidence', '')}]")
        else:
            lines.append(f"  {graph.label(nid)}")
    return "\n".join(lines)


def explain(graph: RawGraph, term: str) -> str:
    nid = graph.best_match(term)
    if not nid:
        return f"No node matching {term!r}"
    node = graph.nodes[nid]
    lines = [
        f"NODE: {graph.label(nid)}",
        f"  source: {node.get('source_file', 'unknown')}",
        f"  type: {node.get('file_type', 'unknown')}",
        f"  degree: {graph.degree(nid)}",
        "",
        "CONNECTIONS:",
    ]
    for neighbor, data in graph.adjacency(direction="out").get(nid, []):
        lines.append(
            f"  --{data.get('relation', '')}--> {graph.label(neighbor)} [{data.get('confidence', '')}] "
            f"({graph.nodes.get(neighbor, {}).get('source_file', '')})"
        )
    return "\n".join(lines)
