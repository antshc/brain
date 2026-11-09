from __future__ import annotations

import json
import sys
from pathlib import Path

WF = Path(__file__).resolve().parents[3] / "plugins/wf"
sys.path.insert(0, str(WF / "skills/github/scripts"))

from github_cli.cli import main
from github_cli.gh import Gh

MANIFEST = WF / "install/github-labels.json"
LABELS = json.loads(MANIFEST.read_text())


def test_preserves_existing_labels_and_verifies_creates(capsys):
    existing = {label["name"]: "existing" for label in LABELS if label["name"] != "bug"}
    writes = []

    def run(argv):
        assert argv[:2] == ["gh", "api"]
        if "--method" in argv:
            assert argv[3:5] == ["POST", "repos/owner/tracker/labels"]
            payload = json.loads(Path(argv[-1]).read_text())
            writes.append(payload)
            existing[payload["name"]] = payload["color"]
            return 0, json.dumps(payload), ""
        assert argv[-1] == "repos/owner/tracker/labels?per_page=100"
        return 0, json.dumps([[{"name": name} for name in existing]]), ""

    args = ["label", "ensure", "--repo", "owner/tracker", "--manifest", str(MANIFEST)]
    assert main(args, gh=Gh(run)) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["labels"] == [
        "hitl", "spec", "bug", "wayfinder:map", "wayfinder:research", "wayfinder:experiment",
        "wayfinder:grilling", "wayfinder:task", "wayfinder:contract-design",
    ]
    assert output["created"] == ["bug"]
    assert writes == [{"name": "bug", "color": "d73a4a", "description": "Failure requiring investigation"}]
    assert existing["hitl"] == "existing"
    assert main(args, gh=Gh(run)) == 0
    assert len(writes) == 1


def test_lookup_failure_prevents_creation(capsys):
    def run(argv):
        assert argv[:4] == ["gh", "api", "--paginate", "--slurp"]
        return 1, "", "not permitted"

    args = ["label", "ensure", "--repo", "owner/tracker", "--manifest", str(MANIFEST)]
    assert main(args, gh=Gh(run)) == 1
    assert "not permitted" in capsys.readouterr().err
