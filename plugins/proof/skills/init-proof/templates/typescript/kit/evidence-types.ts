import type { Surface } from "./types";
export interface EvidenceReader {
  text(path: string): Promise<string>;
  json<T = unknown>(path: string): Promise<T>;
  bytes(path: string): Promise<Uint8Array>;
}
export type EvidenceKit = {
  evidence: EvidenceReader;
  check(name: string, actual: unknown, expected: unknown, hint?: string): void;
};
export type EvidenceContract = {
  feature: string;
  required: readonly string[];
  optional?: readonly string[];
  surfaces: readonly Surface[];
  /** A persisted GET, or explicitly approved DB when no suitable read API exists. */
  resource: { path: string; kind: "api" | "db"; noReadApiReason?: string };
  verify(kit: EvidenceKit): Promise<void>;
};
export type Artifact = {
  sha256: string; runId: string; revision: string; build: string;
  capturedAt: string; complete: boolean;
  kind: "api" | "db" | "ui" | "task" | "logs" | "network" | "console" | "tests" | "metadata" | "screenshot";
};
export type EvidenceManifest = {
  runId: string; revision: string; build: string; startedAt: string; endedAt: string;
  contractDigest: string; artifacts: Record<string, Artifact>;
  /** An opaque attestation checked by the project's trust policy, never trusted by the kit. */
  provenance: unknown;
};
export type ContractModule = { path: string; sha256: string };
export type TestPolicy = {
  report: string; metadata: string; format: "junit" | "trx" | "json";
  requiredIds: readonly string[]; requiredSuites: readonly string[]; allowedSkips: readonly string[];
};
export type EvidencePolicy = {
  revision: string; build: string;
  /** Digest pinned by the reviewer/CI outside the run, before implementation. */
  contractDigest: string; approvedAt: string;
  /** Include the registry, contract modules, and all local acceptance-policy dependencies. */
  modules: readonly ContractModule[];
  tests: TestPolicy;
  authorize(manifest: EvidenceManifest, rawManifest: string): Promise<boolean>;
};
export interface DatabaseAdapter {
  getResource(kind: string, key: string): Promise<Record<string, unknown> | null>;
}
