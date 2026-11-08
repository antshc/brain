// The built-in mole commands: group, usage, summary. 
export const COMMANDS = {
  up: ["Health", "up [--url URL] [--start] [--headless]", "Open a Chrome you can drive on the app and find the API. --start also runs the app (APP.start). Leave it running in its own terminal."],
  down: ["Health", "down", "Stop what up started (Chrome, and the app if --start)."],
  doctor: ["Health", "doctor", "Is this instance worth driving? Tools, session, app, API, loaded build, last proof."],
  open: ["Drive", "open [path]", "Go to an app path. Default: the home page."],
  reload: ["Drive", "reload", "Reload the page, like a user."],
  reset: ["Drive", "reset [--dry-run]", "Clear cookies and the app's storage and reload: a fresh visitor."],
  snapshot: ["Look", "snapshot", "What a user sees: url, title, heading, accessibility tree."],
  storage: ["Look", "storage", "The app's localStorage and cookie names, read through the DevTools protocol."],
  console: ["Look", "console [--errors]", "Console messages and uncaught errors since up."],
  network: ["Look", "network", "Responses and failed requests since up."],
  screenshot: ["Look", "screenshot [path]", "Save a full-page screenshot."],
  eval: ["Look", "eval <expression>", "Read page state after the user path ran. Not for calling app internals."],
  api: ["Look", "api get <path>", "Exploration only: GET a path on the API and show the answer. No proof depends on it."],
  features: ["Prove", "features [--changed]", "List the features, their sub-features, scenarios and flows. --changed: only those your uncommitted changes touch."],
  flow: ["Prove", "flow <id> [--var k=v]", "Run a registered flow on the open page, as a scenario would. Drives only; proves nothing."],
  run: ["Prove", "run [target...]", "Fresh visitor per scenario, evidence, a receipt. target: feature | feature.sub-feature | feature.sub-feature.scenario; none runs all. Exit 0 PASS, 1 FAIL, 2 can't tell."],
  receipts: ["Prove", "receipts [target]", "The recent receipts and the evidence artifacts each check left."],
} as const;
export type Command = keyof typeof COMMANDS;
