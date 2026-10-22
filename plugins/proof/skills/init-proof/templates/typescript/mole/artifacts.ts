import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import type { ArtifactStore } from "../proof/kit";

const safe = (text: string) => text.replace(/[^A-Za-z0-9._-]+/g, "_");

/**
 * Evidence artifacts for one run: DIR/artifacts/<revision>/<stamp>/<scenario>/<check>.<source>.<ext>.
 * The receipt keeps the path relative to DIR, so a receipt and its evidence stay together.
 */
export function fileArtifactStore(dir: string, revision: string | null, stamp = new Date().toISOString().replace(/[:.]/g, "-")): ArtifactStore {
  const root = join("artifacts", safe(revision ?? "unknown"), stamp);
  return {
    async save({ scenario, check, source, ext, data }) {
      const relative = join(root, safe(scenario), `${safe(check)}.${safe(source)}.${safe(ext)}`);
      await mkdir(dirname(join(dir, relative)), { recursive: true });
      await writeFile(join(dir, relative), data);
      return relative;
    },
  };
}
