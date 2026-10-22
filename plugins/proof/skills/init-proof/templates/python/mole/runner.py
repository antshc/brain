"""Runs scenarios for `mole run` and `mole.prove_cli`, so both prove the same way."""

from __future__ import annotations

import time
from collections.abc import Sequence
from pathlib import Path

from playwright.sync_api import Browser, Page

from proof.app import APP
from proof.kit import Receipt, Scenario, run_scenario

from .commands import DIAGNOSE, RERUN
from .runtime import fetch, source_revision


def settle(page: Page) -> None:
    if APP.web and APP.web.settle:
        APP.web.settle(page)
    else:
        page.wait_for_load_state("load")


# Each scenario keeps its evidence in its own folder under runs/<stamp>-<revision>/, so one run never overwrites another.
def run_scenarios(browser: Browser, app_url: str, api_url: str | None, scenarios: Sequence[Scenario], directory: Path) -> list[Receipt]:
    stamp = f"{int(time.time() * 1000)}-{source_revision() or 'unknown'}"
    receipts: list[Receipt] = []
    for scenario in scenarios:
        folder = directory / "runs" / stamp / scenario.id
        receipts.append(run_scenario(
            browser, app_url, scenario, directory=folder, screenshot=folder / "final.png", revision=source_revision, api_url=api_url,
            fetch=fetch, settle=settle, rerun=RERUN, diagnose=DIAGNOSE,
        ))
    return receipts
