import { execFileSync, spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { createWriteStream } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { APP } from "../proof/app";

// pnpm runs scripts from the package root, which is where proof/ and mole/ live.
export const ROOT = process.cwd();
export const DEFAULT_URL = APP.url;

const git = (...args: string[]) => execFileSync("git", args, { cwd: ROOT, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });

// Proof and mole files are not part of the build, so editing them must not stale the running app.
const pathspec = () => ["--", ...(APP.sourcePaths.length ? APP.sourcePaths : ["."]), ":(exclude)proof", ":(exclude)mole", ":(exclude).github"];

// An app rarely serves its revision, so derive one from the source: HEAD plus a hash of uncommitted changes under APP.sourcePaths.
export async function sourceRevision(): Promise<string | null> {
  try {
    const head = git("rev-parse", "--short", "HEAD").trim();
    const diff = git("diff", "HEAD", ...pathspec());
    const untracked = git("ls-files", "--others", "--exclude-standard", ...pathspec()).split("\n").filter(Boolean).sort();
    const hash = createHash("sha256").update(diff);
    for (const file of untracked) hash.update(file).update(await readFile(join(ROOT, file)).catch(() => ""));
    return diff || untracked.length ? `${head}+${hash.digest("hex").slice(0, 8)}` : head;
  } catch { return null; }
}

/** Files changed since HEAD, relative to ROOT, plus untracked ones. */
export function changedFiles(): string[] {
  const lines = (...args: string[]) => git(...args).split("\n").filter(Boolean);
  return [...new Set([...lines("diff", "--name-only", "--relative", "HEAD"), ...lines("ls-files", "--others", "--exclude-standard")])];
}

// PROOF_API_URL wins, then APP.api.discover. A repo with no web surface is its own API.
export async function discoverApi(): Promise<string | null> {
  if (process.env.PROOF_API_URL) return process.env.PROOF_API_URL;
  try {
    const found = await APP.api?.discover?.();
    if (found) return found;
  } catch { /* not found */ }
  return APP.surfaces.includes("web") ? null : APP.url;
}

export async function reachable(url: string, timeoutMs = 2000) {
  try { return (await fetch(url, { signal: AbortSignal.timeout(timeoutMs), redirect: "manual" })).status < 500; } catch { return false; }
}

export async function apiAnswers(baseUrl: string) {
  try { return APP.api?.probe ? Boolean(await APP.api.probe(baseUrl)) : await reachable(baseUrl); } catch { return false; }
}

export type StartedApp = { url: string; pid: number; log: string; close(): Promise<void> };

const tail = async (file: string) => (await readFile(file, "utf8").catch(() => "")).trim().split("\n").filter(Boolean).slice(0, 3).join(" ").slice(0, 300) || "no output";

// Runs APP.start and waits until the app answers (and APP.start.ready agrees).
export async function startApp(options: { url?: string; log: string; timeoutMs?: number }): Promise<StartedApp> {
  const start = APP.start;
  if (!start) throw new Error("proof/app.ts has no `start`, so mole cannot run the app. Start it yourself, or fill in APP.start.");
  const url = options.url ?? DEFAULT_URL;
  const extra = start.prerequisites?.() ?? {};
  const child = spawn(start.command, start.args, {
    cwd: start.cwd ? join(ROOT, start.cwd) : ROOT, detached: true, stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, ...extra, ...start.env },
  });
  const log = createWriteStream(options.log);
  child.stdout.pipe(log);
  child.stderr.pipe(log);
  let exited: number | null = null;
  child.once("close", code => { exited = code ?? 1; });
  child.once("error", error => { exited = 1; log.write(String(error) + "\n"); });

  const close = async () => {
    if (exited === null && child.pid) {
      try { process.kill(-child.pid, "SIGINT"); } catch { /* already gone */ }
      for (let i = 0; i < 150 && exited === null; i++) await new Promise(resolve => setTimeout(resolve, 100));
      if (exited === null) { try { process.kill(-child.pid, "SIGKILL"); } catch { /* already gone */ } }
    }
    log.end();
  };

  const deadline = Date.now() + (options.timeoutMs ?? start.timeoutMs ?? 120_000);
  while (Date.now() < deadline) {
    if (exited !== null) throw new Error(`The app exited with code ${exited} before it answered: ${await tail(options.log)} (log: ${options.log})`);
    if (await reachable(url) && (!start.ready || await start.ready(url).catch(() => false))) return { url, pid: child.pid!, log: options.log, close };
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  await close();
  throw new Error(`${APP.name} did not answer at ${url} in time. See ${options.log}`);
}
