"""Usage: python3 -m mole.prove_cli [--url URL] [id ...]

An id is a feature, a sub-feature or a scenario; none runs them all. Exit 0 PASS, 1 FAIL, 2 can't tell.
Receipts and evidence go to proof/.runs/. Runs against an app you already started, in its own throwaway browser. `mole run` does the same in mole's browser.
"""

from __future__ import annotations

import argparse
import sys

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from proof.app import APP
from proof.features import REGISTRY
from proof.kit import exit_code, select_scenarios

from .receipts import coverage_notes, summarize, write_summary
from .runner import run_scenarios
from .runtime import DEFAULT_URL, ROOT, discover_api


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prove_cli", allow_abbrev=False)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("ids", nargs="*")
    args = parser.parse_args(argv)
    try:
        selected = select_scenarios(REGISTRY, args.ids)
        api_url = discover_api() if any("api" in scenario.surfaces for scenario in selected) else None
        if api_url is None and any("api" in scenario.surfaces for scenario in selected):
            raise RuntimeError(f"The API of {APP.name} was not found. Start the app, or set PROOF_API_URL, or make APP.api.discover return it")
        directory = ROOT / "proof" / ".runs"
        directory.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                receipts = run_scenarios(browser, args.url, api_url, selected, directory)
            finally:
                browser.close()
    except (RuntimeError, ValueError, OSError, PlaywrightError) as exception:
        print(exception, file=sys.stderr)
        return 2
    summary = summarize(receipts, coverage_notes(selected))
    print(write_summary(directory / "last-receipt.json", summary))
    return exit_code(str(summary["verdict"]))


if __name__ == "__main__":
    sys.exit(main())
