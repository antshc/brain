#!/usr/bin/env python3
"""Read-only focused graphify search: noise-free query, term suggestions, endpoint resolve, hub-free path."""
from __future__ import annotations

import argparse
import contextlib
import io
import re
import sys
from itertools import product
from pathlib import Path

import networkx as nx
from graphify import serve

NOISE_KINDS = ("sourceless", "structure", "namespace", "generated", "deprecated", "test", "mock", "manifest")
TYPE_ONLY_CONTEXTS = frozenset({"generic_arg", "parameter_type", "return_type", "attribute", "argument", "type"})
HUB_RELATIONS = frozenset({"imports", "imports_from", "re_exports", "dynamic_import"})
GENERIC = frozenset({"service", "manager", "result", "configuration", "test", "data", "info", "model", "type", "value"})
FILLER = frozenset({
    "explain", "describe", "depend", "reach", "flow", "show", "each", "after", "before", "same", "time",
    "happen", "left", "old", "new", "way", "part", "work", "use",
})
MAX_SINGLE_RATIO = 0.01

_TEST = re.compile(
    r"(/tests?/|\.tests?/|\.integrationtests/|\.unittests/|/__tests__/|/__mocks__/|"
    r"\.(test|spec)\.[jt]sx?$|tests?\.cs$|/testutils?/|\.testutils?/|/fakes?/|\.fakes?/)",
    re.IGNORECASE,
)
_GENERATED = re.compile(
    r"(^|/)(\.artifacts|bin|obj|testresults|review_diff|\.worktrees|node_modules|graphify-out)/", re.IGNORECASE
)
_DEPRECATED = re.compile(r"(^|/)[^/]*deprecated[^/]*/", re.IGNORECASE)
_MOCK = re.compile(r"(^|/)(mocker|mocks?)/", re.IGNORECASE)
_MANIFEST = re.compile(r"(\.csproj|\.sln|/package(-lock)?\.json|/tsconfig[^/]*\.json)$", re.IGNORECASE)


def node_noise(data: dict) -> str | None:
    kind = str((data.get("metadata") or {}).get("kind") or "")
    if data.get("type") == "namespace" or kind.endswith("namespace"):
        return "namespace"
    source = (data.get("source_file") or "").replace("\\", "/")
    if not source:
        return "sourceless"
    if "/" not in source and "." not in source:
        return "structure"
    if _GENERATED.search(source):
        return "generated"
    if _DEPRECATED.search(source):
        return "deprecated"
    if _TEST.search(source):
        return "test"
    if _MOCK.search(source):
        return "mock"
    if _MANIFEST.search(source):
        return "manifest"
    return None


def load_graph(path: Path) -> nx.DiGraph:
    with contextlib.redirect_stderr(io.StringIO()):
        return serve._load_graph(str(path))


def focus(graph: nx.DiGraph, *, keep: frozenset[str] = frozenset()) -> nx.DiGraph:
    drop = frozenset(NOISE_KINDS) - keep
    focused = graph.subgraph(nid for nid, data in graph.nodes(data=True) if node_noise(data) not in drop).copy()
    focused.graph = {"_logical_directed": graph.graph.get("_logical_directed", False), "_learning_overlay": {}}
    return focused


def _label(graph: nx.DiGraph, nid: str) -> str:
    return graph.nodes[nid].get("label") or nid


def _bare(label: str) -> str:
    return label.lstrip(".").removesuffix("()")


def _label_index(graph: nx.DiGraph) -> list[str]:
    cached = graph.graph.get("_focused_labels")
    if cached is None:
        cached = [(data.get("norm_label") or (data.get("label") or "")).lower() for _, data in graph.nodes(data=True)]
        graph.graph["_focused_labels"] = cached
    return cached


def doc_frequency(graph: nx.DiGraph, token: str) -> int:
    counts = graph.graph.setdefault("_focused_df", {})
    token = token.lower()
    if token not in counts:
        counts[token] = sum(1 for label in _label_index(graph) if token in label)
    return counts[token]


def _words(graph: nx.DiGraph) -> frozenset[str]:
    cached = graph.graph.get("_focused_words")
    if cached is None:
        words: set[str] = set()
        for _, data in graph.nodes(data=True):
            for chunk in re.findall(r"[^\W\d_]+", data.get("label") or ""):
                words.update(p.lower() for p in re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+", chunk) or [chunk])
        cached = frozenset(words)
        graph.graph["_focused_words"] = cached
    return cached


def _identifiers(graph: nx.DiGraph) -> frozenset[str]:
    cached = graph.graph.get("_focused_identifiers")
    if cached is None:
        names: set[str] = set()
        for nid in graph.nodes:
            bare = _bare(_label(graph, nid)).lower()
            names.update((bare, bare.rsplit(".", 1)[-1]))
        cached = frozenset(names)
        graph.graph["_focused_identifiers"] = cached
    return cached


def _forms(graph: nx.DiGraph, token: str) -> list[str]:
    words = _words(graph)
    candidates = [token] + [
        token[: -len(suffix)] + replacement
        for suffix, replacement in (("ies", "y"), ("es", ""), ("s", ""), ("ed", ""), ("ed", "e"), ("ing", ""), ("ing", "e"))
        if token.endswith(suffix) and len(token) - len(suffix) >= 3
    ]
    forms = list(dict.fromkeys(c for c in candidates if c in words))
    return forms or ([token] if doc_frequency(graph, token) else [])


def suggest_terms(graph: nx.DiGraph, text: str, *, limit: int = 3) -> list[tuple[str, int]]:
    """Longest identifier-shaped compounds of adjacent words first, then rare single words."""
    words = [forms for raw in dict.fromkeys(serve._query_terms(text)) if (forms := _forms(graph, raw))]
    compounds: dict[str, int] = {}
    for size in (3, 2):
        for start in range(len(words) - size + 1):
            for parts in product(*words[start:start + size]):
                joined = "".join(parts)
                if doc_frequency(graph, joined) and not any(joined in longer for longer in compounds):
                    compounds[joined] = size
    covered = {form for forms in words for form in forms if any(form in compound for compound in compounds)}
    total = max(1, graph.number_of_nodes())
    identifiers = _identifiers(graph)
    singles = [
        forms[0] for forms in words
        if not covered.intersection(forms) and not (GENERIC | FILLER).intersection(forms)
        and (forms[0] in identifiers or 2 <= doc_frequency(graph, forms[0]) <= MAX_SINGLE_RATIO * total)
    ]
    ranked = sorted(compounds, key=lambda t: (t not in identifiers, -compounds[t], doc_frequency(graph, t)))
    ranked += sorted(dict.fromkeys(singles), key=lambda t: (t not in identifiers or len(t) < 8, doc_frequency(graph, t)))
    return [(term, doc_frequency(graph, term)) for term in ranked[:limit]]


def resolve(graph: nx.DiGraph, text: str, *, limit: int = 5) -> list[str]:
    """Exact (case-insensitive) label first, type over member, else the best suggested compound."""
    wanted = _bare(text.strip()).lower()
    exact = [
        nid for nid in graph.nodes
        if wanted in (_bare(_label(graph, nid)).lower(), _bare(_label(graph, nid)).rsplit(".", 1)[-1].lower())
    ]
    if exact:
        return sorted(
            exact, key=lambda nid: (_label(graph, nid).endswith(")"), "." in _label(graph, nid), -graph.degree(nid))
        )[:limit]
    terms = [term for term, _ in suggest_terms(graph, text, limit=1)] or serve._query_terms(text)
    return [nid for _, nid in serve._score_nodes(graph, terms)[:limit]]


def _undirected(graph: nx.DiGraph, *, drop_hubs: bool) -> nx.DiGraph:
    result = graph.__class__()
    result.graph = graph.graph
    result.add_nodes_from(graph.nodes(data=True))
    for u, v, data in graph.edges(data=True):
        if drop_hubs and data.get("relation") in HUB_RELATIONS:
            continue
        result.add_edge(u, v, **data)
        if not graph.has_edge(v, u):
            result.add_edge(v, u, **data)
    return result


def query_text(
    graph: nx.DiGraph, terms: list[str], *, anchor: bool = False, both: bool = False,
    depth: int = 2, budget: int = 2000, context: list[str] | None = None,
) -> tuple[str, list[str], set[str]]:
    terms = [term.lower() for term in terms]
    scores = serve._score_query(graph, terms, collect_per_term_seeds=True)
    if anchor:
        seeds = [nid for _, nid in scores.ranked[:1]]
    else:
        seeds = serve._pick_seeds(scores.ranked, G=graph, best_seed_by_term=scores.best_seed_by_term)
    if not seeds:
        return "No matching nodes found.", [], set()
    traversal = serve._filter_graph_by_context(graph, context) if context else graph
    if both:
        traversal = _undirected(traversal, drop_hubs=True)
        depth = min(depth, 1)
    visited, edges = serve._bfs(traversal, seeds, depth)
    header = f"Focused BFS depth={depth} | Start: {[_label(graph, n) for n in seeds]} | {len(visited)} nodes\n\n"
    return header + serve._subgraph_to_text(traversal, visited, edges, budget, seeds=seeds), seeds, visited


def find_path(graph: nx.DiGraph, source: str, target: str, *, directed: bool = False) -> list[str] | None:
    if directed:
        traversal = graph
    else:
        traversal = graph.graph.get("_focused_undirected")
        if traversal is None:
            traversal = _undirected(graph, drop_hubs=True)
            graph.graph["_focused_undirected"] = traversal
    try:
        return nx.shortest_path(traversal, source, target, weight=_edge_weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def _edge_weight(_u: str, _v: str, data: dict) -> float:
    """Type-only references (shared DTO/generic types) are weaker evidence of a dependency than fields, calls, implements."""
    return 3.0 if data.get("context") in TYPE_ONLY_CONTEXTS else 1.0


def _describe(graph: nx.DiGraph, nid: str) -> str:
    data = graph.nodes[nid]
    return f"{_label(graph, nid)}  {data.get('source_file', '')}:{data.get('source_location', '')}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Focused graphify search over production code only [read-only].",
        epilog=(
            "examples:\n"
            "  focused_query.py terms \"which service cleans old orders\"\n"
            "  focused_query.py query orderjanitor\n"
            "  focused_query.py query InvoiceManager --anchor --both\n"
            "  focused_query.py resolve OrdersController\n"
            "  focused_query.py path OrdersController ShipmentTask"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--graph", type=Path, default=Path("graphify-out/graph.json"))
    parser.add_argument("--keep", default="", help=f"comma list of noise kinds to keep: {','.join(NOISE_KINDS)}")
    sub = parser.add_subparsers(dest="command", required=True)
    terms = sub.add_parser("terms", help="suggest identifier-shaped search terms for a question")
    terms.add_argument("text")
    terms.add_argument("--limit", type=int, default=3)
    query = sub.add_parser("query", help="BFS from the best matches of 1-2 terms")
    query.add_argument("terms", nargs="+")
    query.add_argument("--anchor", action="store_true", help="seed only the single best match")
    query.add_argument("--both", action="store_true", help="1 hop over callers and callees, import edges dropped")
    query.add_argument("--depth", type=int, default=2)
    query.add_argument("--budget", type=int, default=2000)
    query.add_argument("--context", action="append", help="edge context filter, e.g. call, field")
    found = sub.add_parser("resolve", help="list production nodes for a label or phrase")
    found.add_argument("text")
    path = sub.add_parser("path", help="shortest hub-free path between two labels")
    path.add_argument("source")
    path.add_argument("target")
    path.add_argument("--directed", action="store_true")
    args = parser.parse_args(argv)

    if not args.graph.exists():
        print(f"error: {args.graph} missing; build it with the project's graph build (see GRAPHIFY.md) or pass --graph", file=sys.stderr)
        return 1
    keep = frozenset(kind for kind in args.keep.split(",") if kind)
    unknown = keep - set(NOISE_KINDS)
    if unknown:
        print(f"error: unknown noise kinds {sorted(unknown)}", file=sys.stderr)
        return 2
    graph = focus(load_graph(args.graph), keep=keep)
    if args.command == "terms":
        suggestions = suggest_terms(graph, args.text, limit=args.limit)
        print("\n".join(f"{term}\t{count}" for term, count in suggestions) or "no graph vocabulary matches")
    elif args.command == "query":
        text, _, _ = query_text(
            graph, args.terms, anchor=args.anchor, both=args.both, depth=args.depth,
            budget=args.budget, context=args.context,
        )
        print(text)
    elif args.command == "resolve":
        print("\n".join(_describe(graph, nid) for nid in resolve(graph, args.text)) or "no match")
    else:
        sources, targets = resolve(graph, args.source, limit=1), resolve(graph, args.target, limit=1)
        if not sources or not targets:
            print("error: endpoint not found; run `resolve` first", file=sys.stderr)
            return 1
        nodes = find_path(graph, sources[0], targets[0], directed=args.directed)
        if not nodes:
            print(f"No path between {_describe(graph, sources[0])} and {_describe(graph, targets[0])}")
            return 0
        print(f"Path ({len(nodes) - 1} hops):")
        for nid in nodes:
            print(f"  {_describe(graph, nid)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
