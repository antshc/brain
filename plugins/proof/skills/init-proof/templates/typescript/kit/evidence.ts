import { createHash } from "node:crypto";
import { readFile, realpath } from "node:fs/promises";
import { isAbsolute, relative, resolve, sep } from "node:path";
import type { EvidenceManifest, EvidencePolicy, EvidenceReader } from "./evidence-types";

export const sha256 = (input: string | Uint8Array) => createHash("sha256").update(input).digest("hex");
export function safePath(path: string): void {
  if (!path || isAbsolute(path) || path.includes("\\") || path.includes("\0") || path.split("/").some(p => !p || p === "." || p === "..") || /^[A-Za-z]:/.test(path)) throw new Error(`Unsafe artifact path: ${path}`);
}
export async function localBytes(root: string, path: string): Promise<Buffer> {
  safePath(path);
  const base = await realpath(root), target = await realpath(resolve(base, path));
  const rel = relative(base, target);
  if (rel === ".." || rel.startsWith(`..${sep}`) || isAbsolute(rel)) throw new Error(`Artifact escapes root: ${path}`);
  return readFile(target);
}
export const time = (value: string) => {
  const n = Date.parse(value);
  if (!Number.isFinite(n)) throw new Error("Invalid evidence timestamp");
  return n;
};
export async function contractDigest(root: string, modules: EvidencePolicy["modules"]): Promise<string> {
  if (!modules.length || new Set(modules.map(m => m.path)).size !== modules.length) throw new Error("Missing/duplicate contract modules");
  const entries = [];
  for (const module of [...modules].sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0)) {
    if (sha256(await localBytes(root, module.path)) !== module.sha256) throw new Error(`Changed contract module: ${module.path}`);
    entries.push([module.path, module.sha256]);
  }
  return sha256(JSON.stringify(entries));
}
/** Snapshot verified bytes once: later reads never reopen mutable artifacts. */
export async function openEvidence(root: string, runDir: string, policy: EvidencePolicy): Promise<{ manifest: EvidenceManifest; reader: EvidenceReader; used: Set<string> }> {
  if (!/^[a-f0-9]{40}$/.test(policy.revision) || !policy.build || !/^[a-f0-9]{64}$/.test(policy.contractDigest)) throw new Error("Expected full revision, build and approved digest");
  if (await contractDigest(root, policy.modules) !== policy.contractDigest) throw new Error("Contract digest differs from approval");
  const raw = (await localBytes(runDir, "evidence.json")).toString("utf8");
  const manifest: EvidenceManifest = JSON.parse(raw);
  if (!manifest || typeof manifest !== "object" || !manifest.runId || manifest.revision !== policy.revision || manifest.build !== policy.build || manifest.contractDigest !== policy.contractDigest) throw new Error("Run identity/revision/build/contract mismatch");
  if (time(policy.approvedAt) > time(manifest.startedAt) || time(manifest.startedAt) > time(manifest.endedAt) || time(manifest.endedAt) > Date.now()) throw new Error("Invalid approval/capture window");
  if (!await policy.authorize(manifest, raw)) throw new Error("Run provenance is not authorized");
  if (!manifest.artifacts || typeof manifest.artifacts !== "object" || Array.isArray(manifest.artifacts)) throw new Error("Missing artifact allowlist");
  const saved = new Map<string, Buffer>(), used = new Set<string>();
  for (const [path, entry] of Object.entries(manifest.artifacts)) {
    safePath(path);
    if (!entry || entry.complete !== true || entry.runId !== manifest.runId || entry.revision !== policy.revision || entry.build !== policy.build ||
      time(entry.capturedAt) < time(manifest.startedAt) || time(entry.capturedAt) > time(manifest.endedAt)) throw new Error(`Incomplete/stale artifact: ${path}`);
    const bytes = await localBytes(runDir, path);
    if (sha256(bytes) !== entry.sha256) throw new Error(`Artifact hash mismatch: ${path}`);
    saved.set(path, bytes);
  }
  const bytes = async (path: string) => {
    safePath(path);
    const value = saved.get(path);
    if (!value) throw new Error(`Artifact not allowlisted: ${path}`);
    used.add(path);
    return new Uint8Array(value);
  };
  const text = async (path: string) => new TextDecoder("utf-8", { fatal: true }).decode(await bytes(path));
  return { manifest, used, reader: { bytes, text, json: async <T>(path: string) => JSON.parse(await text(path)) as T } };
}
