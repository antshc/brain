"""Usage: python3 -m proof.engine.prove_cli [--url URL] [--feature NAME] [--surface web|api]

Exit 0 PASS, 1 FAIL, 2 can't tell. Receipts and screenshots go to proof/.runs/.
Runs against an app you already started, in its own throwaway browser. `mole prove` does the same in mole's browser.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from ..app import APP
from .proof import run_proof
from .registry import prove_features, select_features, surfaces_for
from .runtime import DEFAULT_URL, ROOT, discover_api, source_revision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prove_cli", allow_abbrev=False)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--feature", action="append", default=[])
    parser.add_argument("--surface", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        selected = select_features(args.feature)
        surfaces = surfaces_for(selected, args.surface)
        api_url = discover_api() if "api" in surfaces else None
        if "api" in surfaces and not api_url:
            web_hint = ", or prove the web surface only: --surface web" if "web" in APP.surfaces else ""
            raise RuntimeError(f"The API of {APP.name} was not found. Start the app, or set PROOF_API_URL, or make APP.api.discover return it{web_hint}")
        directory = ROOT / "proof" / ".runs"
        directory.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                shot = directory / f"proof-{int(time.time() * 1000)}.png"
                receipt = run_proof(browser, args.url, prove_features(selected), shot, source_revision, surfaces=surfaces, api_url=api_url)
            finally:
                browser.close()
    except (RuntimeError, ValueError, OSError, PlaywrightError) as exception:
        print(exception, file=sys.stderr)
        return 2
    receipt.features = selected
    receipt.surfaces = surfaces
    data = json.dumps(receipt.to_json(), indent=2, default=str)
    (directory / "last-receipt.json").write_text(data)
    print(data)
    return {"PASS": 0, "FAIL": 1}.get(receipt.verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
