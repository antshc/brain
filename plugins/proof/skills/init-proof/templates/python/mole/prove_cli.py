"""Usage: python3 -m mole.prove_cli [--url URL] [--feature NAME] [--surface web|api]

Exit 0 PASS, 1 FAIL, 2 can't tell. Receipts and screenshots go to proof/.runs/.
Runs against an app you already started, in its own throwaway browser. `mole prove` does the same in mole's browser.
"""

from __future__ import annotations

import argparse
import sys
import time

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from proof.app import APP
from proof.features import FEATURES
from proof.kit import exit_code, prove_features, run_proof, select_features, surfaces_for

from .commands import DIAGNOSE, RERUN
from .receipts import write_receipt
from .runtime import DEFAULT_URL, ROOT, SURFACES, discover_api, source_revision


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prove_cli", allow_abbrev=False)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--feature", action="append", default=[])
    parser.add_argument("--surface", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        selected = select_features(FEATURES, args.feature)
        surfaces = surfaces_for(FEATURES, selected, SURFACES, args.surface)
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
                receipt = run_proof(
                    browser, args.url, prove_features(FEATURES, selected), screenshot=shot, revision=source_revision,
                    surfaces=surfaces, api_url=api_url, features=selected, rerun=RERUN, diagnose=DIAGNOSE,
                )
            finally:
                browser.close()
    except (RuntimeError, ValueError, OSError, PlaywrightError) as exception:
        print(exception, file=sys.stderr)
        return 2
    print(write_receipt(directory / "last-receipt.json", receipt))
    return exit_code(receipt)


if __name__ == "__main__":
    sys.exit(main())
