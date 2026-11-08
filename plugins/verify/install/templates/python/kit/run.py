from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser
from playwright.sync_api import Error as PlaywrightError

from .evidence import Collectors, EvidenceError, capture, now_iso
from .receipt import scenario_verdict
from .types import (
    EventWindow, EvidenceRef, Fetch, FlowContext, FlowStep, ProofResult, ProofStep, Receipt, Scenario, Settle, TraceEntry,
    settle_on_load,
)

# The caller supplies a revision of the code under proof, or it stays None.
Revision = Callable[[], "str | None"]


def _show(value: Any) -> str:
    return json.dumps(value, default=repr)


def _first_line(exception: BaseException) -> str:
    return str(exception).split("\n")[0]


def _checkpoint(step: ProofStep, index: int, context: FlowContext, directory: Path, now: Callable[[], str]) -> list[ProofResult]:
    results: list[ProofResult] = []
    for check in step.checks:
        references: list[EvidenceRef] = []
        observations: dict[str, Any] = {}
        try:
            for adapter in check.evidence:
                reference, observed = capture(adapter, context, check=check.id, step=index, directory=directory, now=now)
                references.append(reference)
                observations[adapter.name] = observed
        except EvidenceError as exception:
            results.append(ProofResult(check.id, index, "ERROR", evidence=tuple(references), error=str(exception)))
            continue
        try:
            assessment = check.assess(observations)
        except Exception as exception:  # A check may raise anything; an unreadable observation is not a verdict.
            results.append(ProofResult(check.id, index, "ERROR", evidence=tuple(references), error=f"Check raised {type(exception).__name__}: {_first_line(exception)}"))
            continue
        results.append(ProofResult(
            check.id, index, "PASS" if assessment.passed else "FAIL", assessment.expected, assessment.actual, tuple(references), assessment.hint,
        ))
    return results


def _remaining(scenario: Scenario, start: int, receipt: Receipt) -> None:
    for index in range(start, len(scenario.steps)):
        step = scenario.steps[index]
        if isinstance(step, FlowStep):
            receipt.trace.append(TraceEntry(index, "flow", step.flow.id, "not_reached"))
        else:
            receipt.trace.append(TraceEntry(index, "proof", "+".join(check.id for check in step.checks), "not_reached"))
            receipt.results.extend(ProofResult(check.id, index, "NOT_REACHED") for check in step.checks)


# Executes a scenario's steps in order on a context the caller owns. If the revision changes while running, the evidence
# belongs to two builds and the verdict is "can't tell". Flows act; checkpoints only observe; a stop leaves the rest NOT_REACHED.
def run_steps(
    scenario: Scenario,
    context: FlowContext,
    *,
    directory: Path,
    revision: Revision = lambda: None,
    collectors: Collectors | None = None,
    now: Callable[[], str] = now_iso,
    rerun: str = "Run the scenario again",
    diagnose: str = "Check that the app is running and the build is fresh",
) -> Receipt:
    receipt = Receipt(
        verdict="ERROR", scenario=scenario.id, revision=revision(), app=context.app_url, at=now(), surfaces=list(scenario.surfaces),
        artifacts=str(directory), provenance={"context": "fresh isolated visitor", "appUrl": context.app_url, "apiUrl": context.api_url},
    )
    receipt.provenance["revision"] = receipt.revision
    mark = collectors.mark() if collectors else (0, 0, 0)
    for index, step in enumerate(scenario.steps):
        if isinstance(step, FlowStep):
            try:
                step.flow.run(context)
            except Exception as exception:  # A flow may raise anything; that is a finding about the run, not a crash of the kit.
                receipt.trace.append(TraceEntry(index, "flow", step.flow.id, "failed"))
                receipt.error = f'Flow "{step.flow.id}" raised {type(exception).__name__}: {_first_line(exception)}'
                _remaining(scenario, index + 1, receipt)
                break
            receipt.trace.append(TraceEntry(index, "flow", step.flow.id, "done"))
        else:
            context.window = collectors.window(mark) if collectors else EventWindow()
            results = _checkpoint(step, index, context, directory, now)
            if collectors:
                mark = collectors.mark()
            receipt.results.extend(results)
            passed = all(result.verdict == "PASS" for result in results)
            receipt.trace.append(TraceEntry(index, "proof", "+".join(check.id for check in step.checks), "done" if passed else "failed"))
            if not passed:
                _remaining(scenario, index + 1, receipt)
                break
        current = revision()
        if current != receipt.revision:
            receipt.error = f"The source changed while running (started on {receipt.revision}, now {current}). Evidence from two builds proves neither."
            _remaining(scenario, index + 1, receipt)
            break
    verdict, problem = scenario_verdict(scenario, receipt.results, directory)
    receipt.verdict = "ERROR" if receipt.error else verdict
    if receipt.verdict == "ERROR" and not receipt.error:
        receipt.error = problem or next((result.error for result in receipt.results if result.error), None)
    if collectors:
        receipt.page_errors = collectors.page_errors()
    _advise(receipt, rerun, diagnose)
    return receipt


def _advise(receipt: Receipt, rerun: str, diagnose: str) -> None:
    if receipt.verdict == "PASS":
        receipt.next_steps = [
            "These checks passed on this revision, each on its own evidence. They cover nothing else: read the evidence for anything they missed."
        ]
    elif receipt.verdict == "FAIL":
        receipt.next_steps = [
            *(
                result.hint or f'Fix "{result.check}": expected {_show(result.expected)}, got {_show(result.actual)}. Evidence: {", ".join(r.artifact for r in result.evidence)}'
                for result in receipt.results if result.verdict == "FAIL"
            ),
            f"Then re-run: {rerun}",
        ]
    else:
        receipt.next_steps = [
            receipt.error or "Unknown error.",
            f"Can't tell is not the same as broken. {diagnose}, then run again.",
        ]


# Runs one scenario against a running app in its own fresh visitor (no storage, no cookies) and returns a receipt.
def run_scenario(
    browser: Browser,
    app: str,
    scenario: Scenario,
    *,
    directory: Path,
    # Where to save a full-page screenshot of the end state (web surface only).
    screenshot: Path | None = None,
    revision: Revision = lambda: None,
    api_url: str | None = None,
    fetch: Fetch,
    settle: Settle = settle_on_load,
    rerun: str = "Run the scenario again",
    diagnose: str = "Check that the app is running and the build is fresh",
    timeout_ms: int = 5000,
    now: Callable[[], str] = now_iso,
) -> Receipt:
    directory.mkdir(parents=True, exist_ok=True)
    collectors = Collectors()
    try:
        browser_context = browser.new_context(ignore_https_errors=True)
    except PlaywrightError as exception:
        return _browser_failed(scenario, app, directory, exception, diagnose, now)
    try:
        page = browser_context.new_page()
        page.set_default_timeout(timeout_ms)
        collectors.attach(page)
        context = FlowContext(page=page, app_url=app, api_url=api_url, fetch=fetch, surfaces=scenario.surfaces, settle=settle)
        receipt = run_steps(scenario, context, directory=directory, revision=revision, collectors=collectors, now=now, rerun=rerun, diagnose=diagnose)
        # A run with no web surface has no page worth a picture.
        if screenshot and "web" in scenario.surfaces:
            try:
                page.screenshot(path=str(screenshot), full_page=True)
                receipt.screenshot = str(screenshot)
            except (PlaywrightError, OSError) as exception:
                # The receipt tells the agent to read the screenshot, so a missing one can't pass.
                receipt.verdict = "ERROR"
                receipt.error = f"Couldn't save the screenshot ({_first_line(exception)}). A receipt without its screenshot can't be read."
                _advise(receipt, rerun, diagnose)
        return receipt
    except PlaywrightError as exception:
        return _browser_failed(scenario, app, directory, exception, diagnose, now)
    finally:
        browser_context.close()


def _browser_failed(scenario: Scenario, app: str, directory: Path, exception: BaseException, diagnose: str, now: Callable[[], str]) -> Receipt:
    receipt = Receipt(
        verdict="ERROR", scenario=scenario.id, revision=None, app=app, at=now(), surfaces=list(scenario.surfaces), artifacts=str(directory),
        error=f"The browser failed: {_first_line(exception)}",
    )
    _remaining(scenario, 0, receipt)
    _advise(receipt, "", diagnose)
    return receipt
