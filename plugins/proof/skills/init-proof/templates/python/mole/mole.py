"""mole: a remote control for the running app, built for agents.

One small CLI that launches, drives, inspects, and proves the app over the
Chrome DevTools Protocol. JSON out; every error says what to do next.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import socket
import sys
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType
from typing import Any, NoReturn, TypedDict, TypeVar
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import Browser, Page, Request, Response, sync_playwright
from playwright.sync_api import Error as PlaywrightError

from proof.app import APP
from proof.features import FEATURES
from proof.kit import Receipt, SurfaceError, exit_code, feature_names, features_for, is_surface, prove_features, read_storage, run_proof, select_features, surfaces_for

from .commands import COMMANDS, DIAGNOSE, MOLE, RERUN
from .feature import DriveCall
from .receipts import coverage_notes, proof_status, save_receipt
from .runtime import DEFAULT_URL, ROOT, SURFACES, StartedApp, api_answers, changed_files, discover_api, fetch, reachable, source_revision, start_app

T = TypeVar("T")

# MOLE_DIR isolates a second instance (tests, a parallel checkout) from the default one.
DIR = Path(os.environ.get("MOLE_DIR") or ROOT / "proof" / ".runs" / "mole")
SESSION = DIR / "session.json"
EVENTS = DIR / "events.jsonl"
RECEIPT = DIR / "receipt.json"
PROFILE = DIR / "profile"
LOCK = DIR / "up.lock"
APP_LOG = DIR / "app.log"
MAPS = APP.feature_maps
HAS_WEB = "web" in APP.surfaces
HAS_API = "api" in APP.surfaces


class MoleError(Exception):
    def __init__(self, message: str, next_step: str, code: int = 2) -> None:
        super().__init__(message)
        self.next_step = next_step
        self.code = code


class Session(TypedDict):
    pid: int
    appUrl: str
    apiUrl: str | None
    cdpUrl: str
    startedApp: bool
    builtRevision: str | None
    headless: bool
    startedAt: str


def out(value: Any) -> None:
    print(json.dumps(value, indent=2, default=str), flush=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    try:  # An exited process that nobody has waited for yet is a zombie: gone for our purposes.
        return Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return True


# A live pid alone could be a reused one: on Linux, check that it is a mole process.
def is_mole(pid: int) -> bool:
    try:
        return "mole" in Path(f"/proc/{pid}/cmdline").read_text(errors="replace")
    except OSError:
        return sys.platform != "linux"


def read_session() -> Session:
    try:
        session: Session = json.loads(SESSION.read_text())
    except (OSError, ValueError) as exception:
        raise MoleError("Nothing is running.", f"Start it in its own terminal and leave it running: {MOLE} up (add --start to run the app)") from exception
    if not alive(session["pid"]) or not is_mole(session["pid"]):
        SESSION.unlink(missing_ok=True)
        raise MoleError("The browser from the last `up` is no longer running.", f"Start it again: {MOLE} up")
    return session


# Attach to the browser that `up` launched, do one thing, and detach.
def with_page(fn: Callable[[Page, Browser, Session], T]) -> T:
    session = read_session()
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.connect_over_cdp(session["cdpUrl"])
        except PlaywrightError as exception:
            raise MoleError(f"Can't reach Chrome at {session['cdpUrl']}.", "Stop up (Ctrl+C or mole down), then start it again.") from exception
        try:
            context = browser.contexts[0]
            page = next((candidate for candidate in context.pages if candidate.url.startswith(session["appUrl"])), None)
            if page is None:
                page = context.pages[0] if context.pages else context.new_page()
            if not page.url.startswith(session["appUrl"]):
                page.goto(session["appUrl"])
            page.set_default_timeout(5000)
            return fn(page, browser, session)
        finally:
            browser.close()  # Over CDP this disconnects; up keeps the browser alive.


def text_of(page: Page, role_level: int) -> str | None:
    locator = page.get_by_role("heading", level=role_level)
    return locator.first.inner_text().strip() if locator.count() else None


def settle(page: Page) -> None:
    if APP.web and APP.web.settle:
        APP.web.settle(page)
    else:
        page.wait_for_load_state("load")


def snapshot(page: Page) -> dict[str, Any]:
    extra = APP.web.snapshot(page) if APP.web and APP.web.snapshot else {}
    try:
        aria: str | None = page.locator("body").aria_snapshot(timeout=1500)
    except PlaywrightError:
        aria = None
    return {"url": page.url, "title": page.title(), "revision": source_revision(), "heading": text_of(page, 1), **extra, "aria": aria}


def read_events(types: list[str]) -> list[dict[str, Any]]:
    text = EVENTS.read_text() if EVENTS.exists() else ""
    events = [json.loads(line) for line in text.split("\n") if line]
    return [event for event in events if event["type"] in types]


# Held from before up touches the profile and event log until it exits, so two ups can't share them.
def claim_up() -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    for _ in range(2):
        try:
            descriptor = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                owner = int(LOCK.read_text() or 0)
            except (OSError, ValueError):
                owner = 0
            if owner and alive(owner) and is_mole(owner):
                break
            LOCK.unlink(missing_ok=True)  # Left by an up that was killed.
            continue
        with os.fdopen(descriptor, "w") as handle:
            handle.write(str(os.getpid()))
        return
    raise MoleError("Another up is already starting or running here.", f"Use it, or stop it first: {MOLE} down")


# The API may come up after the app, so when mole started the app give it a minute. Not finding it is not fatal for the web surface.
def find_api(patient: bool) -> str | None:
    if not HAS_API:
        return None
    deadline = time.monotonic() + (60 if patient else 0)
    while True:
        url = discover_api()
        if url and api_answers(url):
            return url
        if not url and not patient:
            return None
        if time.monotonic() >= deadline:
            return None
        time.sleep(2)


# Where the API answers: what `up` recorded, or look again (the API may have been started after mole).
def api_url_of(session: Session) -> str:
    url = session["apiUrl"] or find_api(False)
    if not url:
        raise MoleError(
            "The API was not found.",
            f"Start the app, then: {MOLE} down; {MOLE} up. Or set PROOF_API_URL, or make APP.api.discover in proof/app.py return the base URL (see {MOLE} doctor).",
        )
    return url


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def start_hint() -> str:
    return " ".join([APP.start.command, *APP.start.args]) if APP.start else "start the app"


class _Stop:
    requested = False

    def request(self, *_: int | FrameType | None) -> None:
        self.requested = True


def up(url: str, start: bool, headless: bool) -> int:
    try:
        existing: Session | None = read_session()
    except MoleError:
        existing = None
    if existing:
        raise MoleError(f"Already running at {existing['appUrl']} (pid {existing['pid']}).", f"Use it, or stop it first: {MOLE} down")
    running = reachable(url)
    if start and running:
        raise MoleError(f"Something already answers at {url}, so --start would collide with it.", f"Attach to it: {MOLE} up (without --start), or stop it first.")
    if start and not APP.start:
        raise MoleError("proof/app.py has no `start`, so mole cannot run the app.", f"Start it yourself, then: {MOLE} up. Or fill in APP.start.")
    if not start and not running:
        raise MoleError(f"No {APP.name} answers at {url}.", f"Run it yourself ({start_hint()}), or let mole do it: {MOLE} up --start")
    if start and APP.start and APP.start.prerequisites:
        try:
            APP.start.prerequisites()
        except (OSError, RuntimeError, ValueError) as exception:
            raise MoleError(str(exception), f"Fix that, then: {MOLE} up --start") from exception
    claim_up()
    app: StartedApp | None = None
    try:
        shutil.rmtree(PROFILE, ignore_errors=True)
        EVENTS.write_text("")
        if start:
            print("Starting the app; the first start can take a while...", file=sys.stderr)
            app = start_app(url=url, log=APP_LOG)
        built_revision = source_revision()
        api_url = find_api(start)
        port = free_port()
        headless_run = headless or bool(os.environ.get("CI")) or (sys.platform == "linux" and not os.environ.get("DISPLAY"))
        stop = _Stop()
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                str(PROFILE), headless=headless_run, ignore_https_errors=True,
                viewport={"width": 1280, "height": 900}, args=[f"--remote-debugging-port={port}"],
            )

            def log(event: dict[str, Any]) -> None:
                try:
                    with EVENTS.open("a") as handle:
                        handle.write(json.dumps({"t": _now_iso(), **event}) + "\n")
                except OSError:
                    pass

            def on_response(response: Response) -> None:
                log({"type": "response", "method": response.request.method, "status": response.status, "url": response.url})

            def on_request_failed(request: Request) -> None:
                log({"type": "requestfailed", "method": request.method, "url": request.url, "text": request.failure})

            def watch(page: Page) -> None:
                page.on("console", lambda message: log({"type": "console", "level": message.type, "text": message.text}))
                page.on("pageerror", lambda error: log({"type": "pageerror", "level": "error", "text": error.message}))
                page.on("load", lambda _: log({"type": "load", "url": page.url}))
                page.on("response", on_response)
                page.on("requestfailed", on_request_failed)

            for existing_page in context.pages:
                watch(existing_page)
            context.on("page", watch)
            context.on("close", lambda _: stop.request())  # Someone closed the browser window.
            try:
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(url)
                session: Session = {
                    "pid": os.getpid(), "appUrl": url, "apiUrl": api_url, "cdpUrl": f"http://127.0.0.1:{port}",
                    "startedApp": app is not None, "builtRevision": built_revision, "headless": headless_run, "startedAt": _now_iso(),
                }
                SESSION.write_text(json.dumps(session, indent=2))
                out({
                    "ok": True, **session, **({"appLog": str(APP_LOG)} if app else {}),
                    "next": f"Leave this running. The API was not found, so only the web surface works: see {MOLE} doctor"
                    if HAS_API and not api_url else f"Leave this running. In another terminal: {MOLE} doctor",
                })
                signal.signal(signal.SIGINT, stop.request)
                signal.signal(signal.SIGTERM, stop.request)
                # Playwright delivers events only while it is pumped, so wait through it rather than sleeping.
                while not stop.requested:
                    pump = context.pages[0] if context.pages else None
                    try:
                        if pump is None:
                            pump = context.new_page()
                        pump.wait_for_timeout(250)
                    except PlaywrightError:
                        time.sleep(0.25)
            finally:
                SESSION.unlink(missing_ok=True)
                try:
                    context.close()
                except PlaywrightError:
                    pass
    finally:
        # A failed start must not leave the app holding the process open.
        if app:
            app.close()
        LOCK.unlink(missing_ok=True)
    return 0


def down() -> int:
    session = read_session()
    os.kill(session["pid"], signal.SIGTERM)
    # Stopping the app shuts its services down gracefully, which can take a while.
    for _ in range(400):
        if not alive(session["pid"]):
            break
        time.sleep(0.1)
    out({"ok": not alive(session["pid"]), "stopped": session["pid"], "next": f"Start again with: {MOLE} up"})
    return 0


def doctor() -> int:
    checks: list[dict[str, Any]] = []
    python_ok = sys.version_info >= (3, 10)
    checks.append({"name": "python", "ok": python_ok, "detail": sys.version.split()[0], **({} if python_ok else {"next": "Install Python 3.10 or newer"})})
    with sync_playwright() as playwright:
        installed = Path(playwright.chromium.executable_path).exists()
    checks.append({
        "name": "chromium", "ok": installed, "detail": "installed" if installed else "missing",
        **({} if installed else {"next": "python3 -m playwright install chromium"}),
    })
    proof: dict[str, Any] = {"status": "unknown: nothing running"}
    try:
        session: Session | None = read_session()
    except MoleError as exception:
        checks.append({"name": "session", "ok": False, "detail": str(exception), "next": exception.next_step})
        session = None
    if session:
        origin = "app started by mole" if session["startedApp"] else "attached"
        checks.append({"name": "session", "ok": True, "detail": f"{origin} at {session['appUrl']}, pid {session['pid']}"})
        answering = reachable(session["appUrl"])
        checks.append({
            "name": "app", "ok": answering, "detail": "answers" if answering else f"no answer at {session['appUrl']}",
            **({} if answering else {"next": f"Start the app, then: {MOLE} down; {MOLE} up (or {MOLE} up --start)"}),
        })
        if HAS_API:
            api_url = session["apiUrl"] or find_api(False)
            api_ok = api_answers(api_url) if api_url else False
            checks.append({
                "name": "api", "ok": api_ok,
                "detail": f"the API answers at {api_url}" if api_ok else f"no answer from {api_url}" if api_url else "the API base URL was not found",
                **({} if api_ok else {"next": f"Start the app, then: {MOLE} down; {MOLE} up. Or set PROOF_API_URL.{' Without it only --surface web can be proved.' if HAS_WEB else ''}"}),
            })
        source = source_revision()
        fresh = source is not None and source == session["builtRevision"]
        checks.append({
            "name": "build", "ok": fresh,
            "detail": f"the running build matches the source ({source})" if fresh else f"STALE: the app was started on {session['builtRevision']}, the source is now {source}",
            **({} if fresh else {"next": f"{MOLE} down; {MOLE} up --start" if session["startedApp"] else f"Restart the app, then: {MOLE} down; {MOLE} up"}),
        })
        proof = proof_status(RECEIPT, source)
    ok = all(check["ok"] for check in checks)
    out({"ok": ok, "checks": checks, "proof": proof})
    return 0 if ok else 1


def prove(features: list[str], surface_names: list[str]) -> int:
    try:
        selected = select_features(FEATURES, features)
        surfaces = surfaces_for(FEATURES, selected, SURFACES, surface_names)
    except ValueError as exception:
        raise MoleError(str(exception), f"See the features: {MOLE} features. The surfaces are: {', '.join(SURFACES)}") from exception

    def run(_page: Page, browser: Browser, session: Session) -> Receipt:
        api_url = api_url_of(session) if "api" in surfaces else None
        source = source_revision()
        if source != session["builtRevision"]:
            raise MoleError(
                f"The running build was started on {session['builtRevision']} but the source is now {source}. A proof would describe code that is not running.",
                f"Restart it: {MOLE} down; {MOLE} up --start" if session["startedApp"] else f"Restart the app, then: {MOLE} down; {MOLE} up",
            )
        # One screenshot per run, so each saved receipt keeps the image it was proved with.
        shot = DIR / f"proof-{source}-{int(time.time() * 1000)}.png"
        return run_proof(
            browser, session["appUrl"], prove_features(FEATURES, selected), screenshot=shot, revision=source_revision,
            surfaces=surfaces, api_url=api_url, features=selected, rerun=RERUN, diagnose=DIAGNOSE,
        )

    receipt = with_page(run)
    receipt.next_steps.extend(coverage_notes(selected, surfaces))
    print(save_receipt(DIR, RECEIPT, receipt), flush=True)
    return exit_code(receipt)


# Which features need proving: all of them, or those whose files your uncommitted changes touch.
def list_features(changed: bool) -> int:
    files = changed_files() if changed else []
    names = features_for(FEATURES, files) if changed else feature_names(FEATURES)
    listing = []
    for name in names:
        feature = FEATURES[name]
        entry: dict[str, Any] = {"name": name, "surfaces": feature.surfaces, "map": f"{MAPS}/{name}.md", "prove": f"{MOLE} prove --feature {name}"}
        if feature.drive:
            entry["drive"] = f"{MOLE} {name} {feature.drive.usage}"
        listing.append(entry)
    if not changed:
        next_step = "Open the map of the feature you are touching, then: " + f"{MOLE} prove --feature <name>"
    elif names:
        next_step = f"Prove each, then run {MOLE} prove with no --feature once before you report."
    else:
        next_step = f"No feature's files changed. Run {MOLE} prove if you still need proof."
    out({**({"changedFiles": len(files)} if changed else {}), "features": listing, "next": next_step})
    return 0


# `mole <feature> <verb> ...`: the feature's own drive hook, on one surface. The answer says which.
def drive_feature(name: str, argv: list[str]) -> int:
    feature = FEATURES[name]
    drive = feature.drive
    if drive is None:
        raise MoleError(
            f'The feature "{name}" has no drive hook, so it cannot be driven by hand.',
            f"Prove it instead: {MOLE} prove --feature {name}. Or add a `drive` to it in proof/features/__init__.py.",
        )
    requested: list[str] = []
    rest: list[str] = []
    tokens = iter(argv)
    for token in tokens:
        if token == "--surface":
            requested.append(next(tokens, ""))
        elif token.startswith("--surface="):
            requested.append(token[len("--surface="):])
        else:
            rest.append(token)
    if len(requested) > 1:
        raise MoleError("Give one --surface.", f"One of: {', '.join(feature.surfaces)}. To run all of them: {MOLE} prove")
    surface = requested[0] if requested else ("web" if "web" in feature.surfaces else feature.surfaces[0])
    if not is_surface(surface):
        raise MoleError(f'Unknown surface "{surface}".', f"Use one of: {', '.join(feature.surfaces)}")
    if surface not in feature.surfaces:
        raise MoleError(f"{name} has no {surface} surface.", f"It has: {', '.join(feature.surfaces)}")
    try:
        if surface == "api":
            result = drive.run(DriveCall(argv=rest, surface=surface, page=None, api_url=api_url_of(read_session())))
        else:
            result = with_page(lambda page, _browser, session: drive.run(DriveCall(argv=rest, surface=surface, page=page, api_url=session["apiUrl"])))
    except SurfaceError as exception:
        raise MoleError(str(exception), exception.next_step) from exception
    other = next((candidate for candidate in feature.surfaces if candidate != surface), None)
    out({**result, **({"next": f"The same call on the {other} surface: add --surface {other}"} if other else {})})
    return 0


def show_help(command: str | None = None) -> int:
    if command and command in COMMANDS:
        group, usage, summary = COMMANDS[command]
        out({"command": command, "group": group, "usage": f"{MOLE} {usage}", "summary": summary})
        return 0
    if command and command in FEATURES and FEATURES[command].drive:
        hook = FEATURES[command].drive
        assert hook is not None
        out({"command": command, "group": "Drive", "usage": f"{MOLE} {command} {hook.usage}", "summary": hook.summary, "surfaces": FEATURES[command].surfaces})
        return 0
    groups: dict[str, list[str]] = {}
    for _, (group, usage, summary) in COMMANDS.items():
        groups.setdefault(group, []).append(f"{usage:<52} {summary}")
    for name, feature in FEATURES.items():
        if feature.drive:
            groups.setdefault("Drive", []).append(f"{name + ' ' + feature.drive.usage:<52} {feature.drive.summary}")
    print(f"mole: drive and prove {APP.name}.\n\nUsage: {MOLE} <command>\n")
    for group, lines in groups.items():
        print(group)
        print("\n".join("  " + line for line in lines) + "\n")
    print(f"Start with: {MOLE} up --start   (own terminal)   then: {MOLE} doctor\nGuide for agents: .github/skills/verify-mole/SKILL.md")
    return 0


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise MoleError(message, f"See the options: {MOLE} help")


def _parser() -> _Parser:
    parser = _Parser(prog="mole", add_help=False, allow_abbrev=False)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--feature", action="append", default=[])
    parser.add_argument("--surface", action="append", default=[])
    parser.add_argument("--changed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--errors", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("command", nargs="?")
    parser.add_argument("args", nargs="*")
    return parser


def _run(argv: list[str]) -> int:
    first = next((token for token in argv if not token.startswith("-")), None)
    # A feature name is a command of its own; its flags belong to its drive hook, so they are not parsed here.
    if first and first not in COMMANDS and first in FEATURES:
        rest = argv[argv.index(first) + 1:]
        if any(token in ("-h", "--help") for token in rest):
            return show_help(first)
        return drive_feature(first, rest)
    parsed = _parser().parse_intermixed_args(argv)
    command: str | None = parsed.command
    args: list[str] = parsed.args
    if not command or command == "help":
        return show_help(args[0] if args else None)
    if command not in COMMANDS:
        raise MoleError(f'Unknown command "{command}".', f"See the commands: {MOLE} help")
    if parsed.help:
        return show_help(command)
    if command == "up":
        return up(parsed.url, parsed.start, parsed.headless)
    if command == "down":
        return down()
    if command == "doctor":
        return doctor()
    if command == "open":
        return _emit(lambda page, _b, session: _open(page, session, args[0] if args else "/"))
    if command == "reload":
        return _emit(lambda page, _b, _s: _reload(page))
    if command == "reset":
        return _emit(lambda page, _b, _s: _reset(page, parsed.dry_run))
    if command == "snapshot":
        return _emit(lambda page, _b, _s: snapshot(page))
    if command == "storage":
        return _emit(lambda page, _b, _s: {
            "origin": _origin(page.url), "localStorage": read_storage(page), "cookies": [cookie["name"] for cookie in page.context.cookies()],
        })
    if command == "console":
        read_session()
        entries = [event for event in read_events(["console", "pageerror", "load"]) if not parsed.errors or event.get("level") == "error"]
        out({"entries": entries[-30:], "note": "pageerror = an uncaught exception. load = the page (re)loaded."})
        return 0
    if command == "network":
        read_session()
        out({"entries": read_events(["response", "requestfailed", "load"])[-40:]})
        return 0
    if command == "screenshot":
        path = args[0] if args else str(DIR / f"screenshot-{int(time.time() * 1000)}.png")
        return _emit(lambda page, _b, _s: _screenshot(page, path))
    if command == "eval":
        if not args:
            raise MoleError("eval needs an expression.", f'{MOLE} eval "document.title"')
        return _emit(lambda page, _b, _s: {"result": page.evaluate(" ".join(args))})
    if command == "api":
        return _api_get(args)
    if command == "features":
        return list_features(parsed.changed)
    return prove(parsed.feature, parsed.surface)


def _origin(url: str) -> str:
    split = urlsplit(url)
    return f"{split.scheme}://{split.netloc}"


def _emit(fn: Callable[[Page, Browser, Session], dict[str, Any]]) -> int:
    out(with_page(fn))
    return 0


def _open(page: Page, session: Session, path: str) -> dict[str, Any]:
    page.goto(urljoin(session["appUrl"], path), wait_until="load")
    settle(page)
    return snapshot(page)


def _reload(page: Page) -> dict[str, Any]:
    page.reload(wait_until="load")
    settle(page)
    return snapshot(page)


def _reset(page: Page, dry_run: bool) -> dict[str, Any]:
    storage = read_storage(page)
    cookies = [cookie["name"] for cookie in page.context.cookies()]
    if dry_run:
        return {"dryRun": True, "wouldClear": {"localStorage": storage, "cookies": cookies}, "next": "Run without --dry-run to clear it."}
    cdp = page.context.new_cdp_session(page)
    origin = _origin(page.url)
    for is_local in (True, False):
        cdp.send("DOMStorage.clear", {"storageId": {"securityOrigin": origin, "isLocalStorage": is_local}})
    cdp.detach()
    page.context.clear_cookies()
    page.goto(f"{origin}/", wait_until="load")
    settle(page)
    return {"cleared": {"localStorage": storage, "cookies": cookies}, **snapshot(page)}


def _screenshot(page: Page, path: str) -> dict[str, Any]:
    page.screenshot(path=path, full_page=True)
    return {"path": path}


def _api_get(args: list[str]) -> int:
    if len(args) < 2 or args[0] != "get":
        raise MoleError("api needs get <path>.", f'{MOLE} api get "/health"')
    url = urljoin(api_url_of(read_session()), args[1])
    try:
        response = fetch(url)
    except OSError as exception:
        raise MoleError(f"Can't reach {_origin(url)}: {exception}.", f"Check the app: {MOLE} doctor") from exception
    body: Any = response.body
    try:
        body = json.loads(response.body)
    except ValueError:
        body = response.body[:4000]
    out({"url": url, "status": response.status, "body": body, "note": "For looking around. A proof goes through a surface adapter, not through this."})
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return _run(sys.argv[1:] if argv is None else argv)
    except MoleError as exception:
        print(json.dumps({"ok": False, "error": str(exception).split("\n")[0], "next": exception.next_step}, indent=2), file=sys.stderr)
        return exception.code
    except (RuntimeError, PlaywrightError, OSError, ValueError) as exception:
        print(json.dumps({"ok": False, "error": str(exception).split("\n")[0], "next": f"Run {MOLE} doctor"}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
