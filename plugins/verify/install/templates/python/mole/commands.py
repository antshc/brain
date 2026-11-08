"""The built-in mole commands: group, usage, summary. A feature's name must not collide with one."""

from __future__ import annotations

MOLE = "python3 -m mole"
PROVE_CLI = "python3 -m mole.prove_cli"
# Handed to the proof kit, which quotes them in receipts.
RERUN = f"{MOLE} run (or {PROVE_CLI})"
DIAGNOSE = f"Run {MOLE} doctor (or check the app is running at --url)"

COMMANDS: dict[str, tuple[str, str, str]] = {
    "up": ("Health", "up [--url URL] [--start] [--headless]", "Open a Chrome you can drive on the app and find the API. --start also runs the app (APP.start). Leave it running in its own terminal."),
    "down": ("Health", "down", "Stop what up started (Chrome, and the app if --start)."),
    "doctor": ("Health", "doctor", "Is this instance worth driving? Tools, session, app, API, loaded build, last proof."),
    "open": ("Drive", "open [path]", "Go to an app path. Default: the home page."),
    "reload": ("Drive", "reload", "Reload the page, like a user."),
    "reset": ("Drive", "reset [--dry-run]", "Clear cookies and the app's storage and reload: a fresh visitor."),
    "flow": ("Drive", "flow <id>", "Run one named flow from proof/flows/ on the attached page, the same code `run` uses. Prints what the page shows after."),
    "snapshot": ("Look", "snapshot", "What a user sees: url, title, heading, accessibility tree."),
    "storage": ("Look", "storage", "The app's localStorage and cookie names, read through the DevTools protocol."),
    "console": ("Look", "console [--errors]", "Console messages and uncaught errors since up."),
    "network": ("Look", "network", "Responses and failed requests since up."),
    "screenshot": ("Look", "screenshot [path]", "Save a full-page screenshot."),
    "eval": ("Look", "eval <expression>", "Read page state after the user path ran. Not for calling app internals."),
    "api": ("Look", "api get <path>", "Exploration only: GET a path on the API and show the answer. No proof depends on it."),
    "features": ("Prove", "features [--changed]", "List features, sub-features and scenarios with their maps. --changed: only the features your uncommitted changes touch."),
    "run": ("Prove", "run [id ...]", "Prove scenarios, each in a fresh visitor, with a receipt per scenario. An id is a feature, a sub-feature or a scenario. No id runs all. Exit 0 PASS, 1 FAIL, 2 can't tell."),
    "receipts": ("Prove", "receipts [id ...]", "The latest receipt of each scenario and whether it is still current. An id selects like `run`."),
}
