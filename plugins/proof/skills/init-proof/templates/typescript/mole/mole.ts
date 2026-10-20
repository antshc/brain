// mole: a remote control for the running app, built for agents.
// One small CLI that launches, drives, inspects, and proves the app over the
// Chrome DevTools Protocol. JSON out; every error says what to do next.
import { appendFile, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { createServer } from "node:net";
import { join } from "node:path";
import { parseArgs } from "node:util";
import { chromium, type Browser, type Page } from "@playwright/test";
import { APP } from "../proof/app";
import { FEATURES } from "../proof/features";
import { SurfaceError, exitCode, featureNames, featuresFor, isSurface, proveFeatures, readStorage, runProof, selectFeatures, surfacesFor, type Surface } from "../proof/kit";
import { COMMANDS, type Command } from "./commands";
import { coverageNotes, proofStatus, saveReceipt } from "./receipts";
import { DEFAULT_URL, ROOT, apiAnswers, changedFiles, discoverApi, reachable, sourceRevision, startApp, type StartedApp } from "./runtime";

// MOLE_DIR isolates a second instance (tests, a parallel checkout) from the default one.
const DIR = process.env.MOLE_DIR ?? join(ROOT, "proof", ".runs", "mole");
const SESSION = join(DIR, "session.json");
const EVENTS = join(DIR, "events.jsonl");
const RECEIPT = join(DIR, "receipt.json");
const PROFILE = join(DIR, "profile");
const LOCK = join(DIR, "up.lock");
const APP_LOG = join(DIR, "app.log");
const MAPS = APP.featureMaps ?? ".github/skills/verify-mole/features";
const SURFACES = APP.surfaces;
const hasWeb = APP.surfaces.includes("web");
const hasApi = APP.surfaces.includes("api");

class MoleError extends Error {
  constructor(message: string, readonly next: string, readonly code = 2) { super(message); }
}
const out = (value: unknown) => console.log(JSON.stringify(value, null, 2));
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

type Session = { pid: number; appUrl: string; apiUrl: string | null; cdpUrl: string; startedApp: boolean; builtRevision: string | null; headless: boolean; startedAt: string };
const alive = (pid: number) => { try { process.kill(pid, 0); return true; } catch { return false; } };
// A live pid alone could be a reused one: on Linux, check that it is a mole process.
const isMole = (pid: number) => {
  try { return readFileSync(`/proc/${pid}/cmdline`, "utf8").includes("mole"); } catch { return process.platform !== "linux"; }
};

async function readSession(): Promise<Session> {
  let session: Session;
  try { session = JSON.parse(await readFile(SESSION, "utf8")); } catch {
    throw new MoleError("Nothing is running.", "Start it in its own terminal and leave it running: pnpm mole up (add --start to run the app)");
  }
  if (!alive(session.pid) || !isMole(session.pid)) {
    await rm(SESSION, { force: true });
    throw new MoleError("The browser from the last `up` is no longer running.", "Start it again: pnpm mole up");
  }
  return session;
}

// Attach to the browser that `up` launched, do one thing, and detach.
async function withPage<T>(fn: (page: Page, browser: Browser, session: Session) => Promise<T>): Promise<T> {
  const session = await readSession();
  const browser = await chromium.connectOverCDP(session.cdpUrl).catch(() => {
    throw new MoleError(`Can't reach Chrome at ${session.cdpUrl}.`, "Stop up (Ctrl+C or pnpm mole down), then start it again.");
  });
  try {
    const context = browser.contexts()[0];
    let page = context.pages().find(p => p.url().startsWith(session.appUrl)) ?? context.pages()[0];
    if (!page) page = await context.newPage();
    if (!page.url().startsWith(session.appUrl)) await page.goto(session.appUrl);
    page.setDefaultTimeout(5000);
    return await fn(page, browser, session);
  } finally {
    await browser.close(); // Over CDP this disconnects; up keeps the browser alive.
  }
}

async function textOf(locator: ReturnType<Page["locator"]>) {
  return (await locator.count()) ? (await locator.first().innerText()).trim() : null;
}

async function settle(page: Page) {
  if (APP.web?.settle) await APP.web.settle(page); else await page.waitForLoadState("load");
}

async function snapshot(page: Page) {
  const extra = APP.web?.snapshot ? await APP.web.snapshot(page) : {};
  return {
    url: page.url(),
    title: await page.title(),
    revision: await sourceRevision(),
    heading: await textOf(page.getByRole("heading", { level: 1 })),
    ...extra,
    aria: await page.locator("body").ariaSnapshot({ timeout: 1500 }).catch(() => null),
  };
}

async function readEvents(types: string[]) {
  const text = existsSync(EVENTS) ? await readFile(EVENTS, "utf8") : "";
  return text.split("\n").filter(Boolean).map(line => JSON.parse(line)).filter(event => types.includes(event.type));
}

// Held from before up touches the profile and event log until it exits, so two ups can't share them.
async function claimUp() {
  await mkdir(DIR, { recursive: true });
  for (let attempt = 0; attempt < 2; attempt++) {
    try { return await writeFile(LOCK, String(process.pid), { flag: "wx" }); } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error;
    }
    const owner = Number(await readFile(LOCK, "utf8").catch(() => ""));
    if (owner && alive(owner) && isMole(owner)) break;
    await rm(LOCK, { force: true }); // Left by an up that was killed.
  }
  throw new MoleError("Another up is already starting or running here.", "Use it, or stop it first: pnpm mole down");
}

// The API may come up after the app, so when mole started the app give it a minute. Not finding it is not fatal for the web surface.
async function findApi(patient: boolean): Promise<string | null> {
  if (!hasApi) return null;
  const deadline = Date.now() + (patient ? 60_000 : 0);
  for (;;) {
    const url = await discoverApi();
    if (url && await apiAnswers(url)) return url;
    if (!url && !patient) return null;
    if (Date.now() >= deadline) return null;
    await sleep(2000);
  }
}

// Where the API answers: what `up` recorded, or look again (the API may have been started after mole).
async function apiUrlOf(session: Session) {
  const url = session.apiUrl ?? await findApi(false);
  if (!url) throw new MoleError("The API was not found.",
    "Start the app, then: pnpm mole down; pnpm mole up. Or set PROOF_API_URL, or make APP.api.discover in proof/app.ts return the base URL (see pnpm mole doctor).");
  return url;
}

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer().once("error", reject).listen(0, "127.0.0.1", () => {
      const address = server.address();
      server.close(() => typeof address === "object" && address ? resolve(address.port) : reject(new Error("No free port")));
    });
  });
}

const startHint = () => APP.start ? [APP.start.command, ...APP.start.args].join(" ") : "start the app";

async function up(options: { url: string; start: boolean; headless: boolean }) {
  const existing = await readSession().catch(() => null);
  if (existing) throw new MoleError(`Already running at ${existing.appUrl} (pid ${existing.pid}).`, "Use it, or stop it first: pnpm mole down");
  const running = await reachable(options.url);
  if (options.start && running) throw new MoleError(`Something already answers at ${options.url}, so --start would collide with it.`,
    "Attach to it: pnpm mole up (without --start), or stop it first.");
  if (options.start && !APP.start) throw new MoleError("proof/app.ts has no `start`, so mole cannot run the app.", "Start it yourself, then: pnpm mole up. Or fill in APP.start.");
  if (!options.start && !running) throw new MoleError(`No ${APP.name} answers at ${options.url}.`,
    `Run it yourself (${startHint()}), or let mole do it: pnpm mole up --start`);
  if (options.start) {
    try { APP.start!.prerequisites?.(); } catch (error) {
      throw new MoleError((error as Error).message, "Fix that, then: pnpm mole up --start");
    }
  }
  await claimUp();
  const opened: { close(): Promise<unknown> }[] = [];
  try {
    await rm(PROFILE, { recursive: true, force: true });
    await writeFile(EVENTS, "");
    let app: StartedApp | undefined;
    if (options.start) {
      console.error("Starting the app; the first start can take a while...");
      app = await startApp({ url: options.url, log: APP_LOG });
      opened.push(app);
    }
    const builtRevision = await sourceRevision();
    const apiUrl = await findApi(options.start);
    const port = await freePort();
    const headless = options.headless || Boolean(process.env.CI) || (process.platform === "linux" && !process.env.DISPLAY);
    const context = await chromium.launchPersistentContext(PROFILE, {
      headless, ignoreHTTPSErrors: true, viewport: { width: 1280, height: 900 }, args: [`--remote-debugging-port=${port}`],
    });
    opened.unshift(context);
    const log = (event: Record<string, unknown>) =>
      appendFile(EVENTS, JSON.stringify({ t: new Date().toISOString(), ...event }) + "\n").catch(() => {});
    const watch = (page: Page) => {
      page.on("console", message => log({ type: "console", level: message.type(), text: message.text() }));
      page.on("pageerror", error => log({ type: "pageerror", level: "error", text: error.message }));
      page.on("load", () => log({ type: "load", url: page.url() }));
      page.on("response", response => log({ type: "response", method: response.request().method(), status: response.status(), url: response.url() }));
      page.on("requestfailed", request => log({ type: "requestfailed", method: request.method(), url: request.url(), text: request.failure()?.errorText }));
    };
    context.pages().forEach(watch);
    context.on("page", watch);
    const page = context.pages()[0] ?? await context.newPage();
    await page.goto(options.url);
    const session: Session = { pid: process.pid, appUrl: options.url, apiUrl, cdpUrl: `http://127.0.0.1:${port}`, startedApp: Boolean(app), builtRevision, headless, startedAt: new Date().toISOString() };
    await writeFile(SESSION, JSON.stringify(session, null, 2));
    out({ ok: true, ...session, ...(app ? { appLog: APP_LOG } : {}),
      next: hasApi && !apiUrl ? "Leave this running. The API was not found, so only the web surface works: see pnpm mole doctor"
        : "Leave this running. In another terminal: pnpm mole doctor" });

    let stopping = false;
    const stop = async () => {
      if (stopping) return;
      stopping = true;
      await rm(SESSION, { force: true });
      await context.close().catch(() => {});
      await app?.close().catch(() => {});
      await rm(LOCK, { force: true });
      process.exit(0);
    };
    process.once("SIGINT", stop);
    process.once("SIGTERM", stop);
    context.on("close", stop); // Someone closed the browser window.
  } catch (error) {
    // A failed start must not leave the app holding the process open.
    for (const resource of opened) await resource.close().catch(() => {});
    await rm(LOCK, { force: true });
    throw error;
  }
  await new Promise(() => {});
}

async function down() {
  const session = await readSession();
  process.kill(session.pid, "SIGTERM");
  // Stopping the app shuts its services down gracefully, which can take a while.
  for (let i = 0; i < 400 && alive(session.pid); i++) await sleep(100);
  out({ ok: !alive(session.pid), stopped: session.pid, next: "Start again with: pnpm mole up" });
}

async function doctor() {
  const checks: { name: string; ok: boolean; detail: string; next?: string }[] = [];
  const node = Number(process.versions.node.split(".")[0]);
  checks.push({ name: "node", ok: node >= 20, detail: process.version, ...(node < 20 ? { next: "Install Node 20 or newer" } : {}) });
  const browserInstalled = existsSync(chromium.executablePath());
  checks.push({ name: "chromium", ok: browserInstalled, detail: browserInstalled ? "installed" : "missing", ...(!browserInstalled ? { next: "pnpm exec playwright install chromium" } : {}) });
  let proof: { status: string; next?: string } = { status: "unknown: nothing running" };
  const session = await readSession().catch((error: MoleError) => {
    checks.push({ name: "session", ok: false, detail: error.message, next: error.next });
    return null;
  });
  if (session) {
    checks.push({ name: "session", ok: true, detail: `${session.startedApp ? "app started by mole" : "attached"} at ${session.appUrl}, pid ${session.pid}` });
    const answering = await reachable(session.appUrl);
    checks.push({ name: "app", ok: answering, detail: answering ? "answers" : `no answer at ${session.appUrl}`,
      ...(!answering ? { next: "Start the app, then: pnpm mole down; pnpm mole up (or pnpm mole up --start)" } : {}) });
    if (hasApi) {
      const apiUrl = session.apiUrl ?? await findApi(false);
      const apiOk = apiUrl ? await apiAnswers(apiUrl) : false;
      checks.push({ name: "api", ok: apiOk, detail: apiOk ? `the API answers at ${apiUrl}` : apiUrl ? `no answer from ${apiUrl}` : "the API base URL was not found",
        ...(!apiOk ? { next: `Start the app, then: pnpm mole down; pnpm mole up. Or set PROOF_API_URL.${hasWeb ? " Without it only --surface web can be proved." : ""}` } : {}) });
    }
    const source = await sourceRevision();
    const fresh = source !== null && source === session.builtRevision;
    checks.push({ name: "build", ok: fresh,
      detail: fresh ? `the running build matches the source (${source})` : `STALE: the app was started on ${session.builtRevision}, the source is now ${source}`,
      ...(!fresh ? { next: session.startedApp ? "pnpm mole down; pnpm mole up --start" : "Restart the app, then: pnpm mole down; pnpm mole up" } : {}) });
    proof = await proofStatus(RECEIPT, source);
  }
  const ok = checks.every(check => check.ok);
  out({ ok, checks, proof });
  if (!ok) process.exitCode = 1;
}

async function prove(features: string[], surfaceNames: string[]) {
  let selected: string[];
  let surfaces: Surface[];
  try {
    selected = selectFeatures(FEATURES, features);
    surfaces = surfacesFor(FEATURES, selected, SURFACES, surfaceNames);
  } catch (error) {
    throw new MoleError((error as Error).message, "See the features: pnpm mole features. The surfaces are: " + SURFACES.join(", "));
  }
  const receipt = await withPage(async (_page, browser, session) => {
    const apiUrl = surfaces.includes("api") ? await apiUrlOf(session) : null;
    const source = await sourceRevision();
    if (source !== session.builtRevision) throw new MoleError(
      `The running build was started on ${session.builtRevision} but the source is now ${source}. A proof would describe code that is not running.`,
      session.startedApp ? "Restart it: pnpm mole down; pnpm mole up --start" : "Restart the app, then: pnpm mole down; pnpm mole up");
    // One screenshot per run, so each saved receipt keeps the image it was proved with.
    return runProof(browser, session.appUrl, proveFeatures(FEATURES, selected), {
      screenshot: join(DIR, `proof-${source}-${Date.now()}.png`), revision: sourceRevision, surfaces, apiUrl, features: selected,
      rerun: "pnpm mole prove (or pnpm prove)", diagnose: "Run pnpm mole doctor (or check the app is running at --url)",
    });
  });
  receipt.next.push(...coverageNotes({ features: selected, surfaces }));
  await saveReceipt(DIR, RECEIPT, receipt);
  out(receipt);
  process.exitCode = exitCode(receipt);
}

// Which features need proving: all of them, or those whose files your uncommitted changes touch.
function listFeatures(changed: boolean) {
  const files = changed ? changedFiles() : [];
  const names = changed ? featuresFor(FEATURES, files) : featureNames(FEATURES);
  out({
    ...(changed ? { changedFiles: files.length } : {}),
    features: names.map(name => ({
      name, surfaces: FEATURES[name].surfaces, map: `${MAPS}/${name}.md`, prove: `pnpm mole prove --feature ${name}`,
      ...(FEATURES[name].drive ? { drive: `pnpm mole ${name} ${FEATURES[name].drive!.usage}` } : {}),
    })),
    next: !changed ? "Open the map of the feature you are touching, then: pnpm mole prove --feature <name>"
      : names.length ? "Prove each, then run pnpm mole prove with no --feature once before you report." : "No feature's files changed. Run pnpm mole prove if you still need proof.",
  });
}

// `mole <feature> <verb> ...`: the feature's own drive hook, on one surface. The answer says which.
async function driveFeature(name: string, argv: string[]) {
  const feature = FEATURES[name];
  if (!feature.drive) throw new MoleError(`The feature "${name}" has no drive hook, so it cannot be driven by hand.`,
    `Prove it instead: pnpm mole prove --feature ${name}. Or add a \`drive\` to it in proof/features/index.ts.`);
  const requested: string[] = [];
  const rest: string[] = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--surface") requested.push(argv[++i] ?? "");
    else if (argv[i].startsWith("--surface=")) requested.push(argv[i].slice("--surface=".length));
    else rest.push(argv[i]);
  }
  if (requested.length > 1) throw new MoleError("Give one --surface.", `One of: ${feature.surfaces.join(", ")}. To run all of them: pnpm mole prove`);
  const surface = requested[0] ?? (feature.surfaces.includes("web") ? "web" : feature.surfaces[0]);
  if (!isSurface(surface)) throw new MoleError(`Unknown surface "${surface}".`, `Use one of: ${feature.surfaces.join(", ")}`);
  if (!feature.surfaces.includes(surface)) throw new MoleError(`${name} has no ${surface} surface.`, `It has: ${feature.surfaces.join(", ")}`);
  try {
    const result = surface === "api"
      ? await feature.drive.run({ argv: rest, surface, page: null, apiUrl: await apiUrlOf(await readSession()) })
      : await withPage((page, _browser, session) => feature.drive!.run({ argv: rest, surface, page, apiUrl: session.apiUrl }));
    const other = feature.surfaces.find(candidate => candidate !== surface);
    return out({ ...result, ...(other ? { next: `The same call on the ${other} surface: add --surface ${other}` } : {}) });
  } catch (error) {
    if (error instanceof SurfaceError) throw new MoleError(error.message, error.next);
    throw error;
  }
}

function help(command?: string) {
  if (command && command in COMMANDS) {
    const [group, usage, summary] = COMMANDS[command as Command];
    return out({ command, group, usage: `pnpm mole ${usage}`, summary });
  }
  if (command && FEATURES[command]?.drive) {
    const { usage, summary } = FEATURES[command].drive!;
    return out({ command, group: "Drive", usage: `pnpm mole ${command} ${usage}`, summary, surfaces: FEATURES[command].surfaces });
  }
  const groups: Record<string, string[]> = {};
  const add = (group: string, usage: string, summary: string) => (groups[group] ??= []).push(`${usage.padEnd(52)} ${summary}`);
  for (const [, [group, usage, summary]] of Object.entries(COMMANDS)) add(group, usage, summary);
  for (const [name, feature] of Object.entries(FEATURES)) if (feature.drive) add("Drive", `${name} ${feature.drive.usage}`, feature.drive.summary);
  console.log(`mole: drive and prove ${APP.name}.\n\nUsage: pnpm mole <command>\n`);
  for (const [group, lines] of Object.entries(groups)) console.log(`${group}\n${lines.map(line => "  " + line).join("\n")}\n`);
  console.log("Start with: pnpm mole up --start   (own terminal)   then: pnpm mole doctor\nGuide for agents: .github/skills/verify-mole/SKILL.md");
}

async function main() {
  try { process.loadEnvFile?.(join(ROOT, ".env")); } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
  }
  const argv = process.argv.slice(2);
  const firstAt = argv.findIndex(token => !token.startsWith("-"));
  const first = firstAt < 0 ? undefined : argv[firstAt];
  // A feature name is a command of its own; its flags belong to its drive hook, so they are not parsed here.
  if (first && !(first in COMMANDS) && first in FEATURES) {
    if (argv.slice(firstAt + 1).some(token => token === "-h" || token === "--help")) return help(first);
    return driveFeature(first, argv.slice(firstAt + 1));
  }
  let parsed;
  try {
    parsed = parseArgs({ args: argv, allowPositionals: true, options: {
      url: { type: "string", default: DEFAULT_URL }, start: { type: "boolean", default: false }, headless: { type: "boolean", default: false },
      feature: { type: "string", multiple: true }, surface: { type: "string", multiple: true }, changed: { type: "boolean", default: false },
      "dry-run": { type: "boolean", default: false }, errors: { type: "boolean", default: false }, help: { type: "boolean", short: "h", default: false },
    } });
  } catch (error) {
    throw new MoleError(error instanceof Error ? error.message : "Bad arguments", "See the options: pnpm mole help");
  }
  const { values, positionals: [command, ...args] } = parsed;
  if (!command || command === "help") return help(args[0]);
  if (!(command in COMMANDS)) throw new MoleError(`Unknown command "${command}".`, "See the commands: pnpm mole help");
  if (values.help) return help(command);
  switch (command as Command) {
    case "up": return up({ url: values.url!, start: values.start, headless: values.headless });
    case "down": return down();
    case "doctor": return doctor();
    case "open": return out(await withPage(async (page, _browser, session) => {
      await page.goto(new URL(args[0] ?? "/", session.appUrl).href, { waitUntil: "load" });
      await settle(page);
      return snapshot(page);
    }));
    case "reload": return out(await withPage(async page => { await page.reload({ waitUntil: "load" }); await settle(page); return snapshot(page); }));
    case "reset": return out(await withPage(async page => {
      const storage = await readStorage(page);
      const cookies = (await page.context().cookies()).map(cookie => cookie.name);
      if (values["dry-run"]) return { dryRun: true, wouldClear: { localStorage: storage, cookies }, next: "Run without --dry-run to clear it." };
      const cdp = await page.context().newCDPSession(page);
      const origin = new URL(page.url()).origin;
      for (const isLocalStorage of [true, false]) await cdp.send("DOMStorage.clear", { storageId: { securityOrigin: origin, isLocalStorage } });
      await cdp.detach();
      await page.context().clearCookies();
      await page.goto(new URL("/", origin).href, { waitUntil: "load" });
      await settle(page);
      return { cleared: { localStorage: storage, cookies }, ...await snapshot(page) };
    }));
    case "snapshot": return out(await withPage(snapshot));
    case "storage": return out(await withPage(async page => ({
      origin: new URL(page.url()).origin,
      localStorage: await readStorage(page),
      cookies: (await page.context().cookies()).map(cookie => cookie.name),
    })));
    case "console": {
      await readSession();
      const entries = (await readEvents(["console", "pageerror", "load"])).filter(event => !values.errors || event.level === "error");
      return out({ entries: entries.slice(-30), note: "pageerror = an uncaught exception. load = the page (re)loaded." });
    }
    case "network": {
      await readSession();
      return out({ entries: (await readEvents(["response", "requestfailed", "load"])).slice(-40) });
    }
    case "screenshot": {
      const path = args[0] ?? join(DIR, `screenshot-${Date.now()}.png`);
      return out(await withPage(async page => { await page.screenshot({ path, fullPage: true }); return { path }; }));
    }
    case "eval": {
      if (!args[0]) throw new MoleError("eval needs an expression.", `pnpm mole eval "document.title"`);
      return out(await withPage(async page => ({ result: await page.evaluate(args.join(" ")) })));
    }
    case "api": {
      if (args[0] !== "get" || !args[1]) throw new MoleError("api needs get <path>.", `pnpm mole api get "/health"`);
      const base = await apiUrlOf(await readSession());
      const url = new URL(args[1], base);
      const response = await fetch(url, { signal: AbortSignal.timeout(10_000) }).catch(error => {
        throw new MoleError(`Can't reach ${url.origin}: ${error instanceof Error ? error.message : String(error)}.`, "Check the app: pnpm mole doctor");
      });
      const text = await response.text();
      let body: unknown = text;
      try { body = JSON.parse(text); } catch { /* not JSON: show the text */ }
      return out({ url: url.href, status: response.status, body: typeof body === "string" ? body.slice(0, 4000) : body,
        note: "For looking around. A proof goes through a surface adapter, not through this." });
    }
    case "features": return listFeatures(values.changed);
    case "prove": return prove(values.feature ?? [], values.surface ?? []);
  }
}

main().catch(error => {
  const known = error instanceof MoleError;
  console.error(JSON.stringify({ ok: false, error: error instanceof Error ? error.message.split("\n")[0] : String(error),
    next: known ? error.next : "Run pnpm mole doctor" }, null, 2));
  process.exitCode = known ? error.code : 2;
});
