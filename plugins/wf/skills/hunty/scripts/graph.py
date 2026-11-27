#!/usr/bin/env python3
"""Single read-only entry point for graphify-out/ search.

Focused commands (terms, query, resolve, path, affected) need graphify and delegate to focused_query.py.
Fallback commands (check, contexts, vocab, slice, traverse, raw-path, explain) use only the stdlib.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import graph_raw  # noqa: E402

FOCUSED = ("terms", "query", "resolve", "path", "affected")
EPILOG = """\
focused (needs graphify):
  graph.py terms "which service cleans old orders"
  graph.py query OrderJanitor --anchor --both
  graph.py resolve OrdersController
  graph.py path OrdersController ShipmentTask
  graph.py affected OrderJanitor --depth 2
fallback (stdlib only):
  graph.py check
  graph.py contexts
  graph.py vocab
  graph.py slice OrderJanitor --context field --relation references --direction out
  graph.py traverse "order janitor" --context call
  graph.py raw-path OrdersController ShipmentTask
  graph.py explain OrderJanitor
"""


def _split(values: list[str] | None) -> set[str]:
    return {item for value in values or [] for item in value.split(",") if item}


def _fallback_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graph.py", description="Read-only graphify-out/ search [run from the graph root].",
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--graph", type=Path, default=Path("graphify-out/graph.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    for name in FOCUSED:
        sub.add_parser(name, help="focused search; see focused_query.py --help", add_help=False)
    sub.add_parser("check", help="graph exists; corpus roots, file types, freshness, noise")
    sub.add_parser("contexts", help="edge context counts for --context filters")
    sub.add_parser("vocab", help="label token vocabulary for constrained query expansion")
    sliced = sub.add_parser("slice", help="direction-aware raw-edge slice from one exact label")
    sliced.add_argument("label")
    sliced.add_argument("--source-contains", default="")
    sliced.add_argument("--context", action="append")
    sliced.add_argument("--relation", action="append")
    sliced.add_argument("--direction", choices=("out", "in", "both"), default="out")
    sliced.add_argument("--depth", type=int, default=1)
    trav = sub.add_parser("traverse", help="BFS (depth 2) or DFS (depth 6) from expanded vocab tokens")
    trav.add_argument("tokens", nargs="+")
    trav.add_argument("--dfs", action="store_true")
    trav.add_argument("--context", action="append")
    trav.add_argument("--relation", action="append")
    trav.add_argument("--budget", type=int, default=2000)
    raw_path = sub.add_parser("raw-path", help="shortest path between best label matches")
    raw_path.add_argument("source")
    raw_path.add_argument("target")
    raw_path.add_argument("--undirected", action="store_true")
    node = sub.add_parser("explain", help="one node and its direct connections")
    node.add_argument("name")
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    command = next((a for a in argv if not a.startswith("-") and a in FOCUSED + ("check", "contexts", "vocab", "slice", "traverse", "raw-path", "explain")), None)
    if command in FOCUSED:
        try:
            import focused_query
        except ModuleNotFoundError as error:
            print(f"error: {error.name} missing; install scripts/requirements.txt or use the fallback commands", file=sys.stderr)
            return 3
        return focused_query.main(argv)

    args = _fallback_parser().parse_args(argv)
    if not args.graph.exists():
        print(f"ERROR: No graph found at {args.graph}; see GRAPHIFY.md for the build entry point", file=sys.stderr)
        return 1
    graph = graph_raw.RawGraph.load(args.graph)
    if args.command == "check":
        print(graph_raw.health(graph, args.graph))
    elif args.command == "contexts":
        print(graph_raw.contexts(graph))
    elif args.command == "vocab":
        tokens = graph_raw.vocab(graph)
        print(f"vocab: {len(tokens)} tokens")
        print("\n".join(tokens))
    elif args.command == "slice":
        print(graph_raw.edge_slice(
            graph, args.label, source_contains=args.source_contains, contexts_=_split(args.context),
            relations=_split(args.relation), direction=args.direction, max_depth=args.depth,
        ))
    elif args.command == "traverse":
        print(graph_raw.traverse(
            graph, " ".join(args.tokens), dfs=args.dfs, contexts_=_split(args.context),
            relations=_split(args.relation), budget=args.budget,
        ))
    elif args.command == "raw-path":
        print(graph_raw.shortest_path(graph, args.source, args.target, undirected=args.undirected))
    else:
        print(graph_raw.explain(graph, args.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
