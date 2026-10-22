import { existsSync } from "node:fs";
import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { APP } from "../proof/app";
import { ROOT } from "./runtime";

export const MAPS = APP.featureMaps ?? ".github/skills/verify-mole/features";

/** The feature maps by feature name (their file name without .md). README.md describes the format and is not a map. */
export async function loadMaps(): Promise<Record<string, string>> {
  const dir = join(ROOT, MAPS);
  if (!existsSync(dir)) return {};
  const maps: Record<string, string> = {};
  for (const file of (await readdir(dir)).filter(name => name.endsWith(".md") && name.toLowerCase() !== "readme.md")) {
    maps[file.slice(0, -3)] = await readFile(join(dir, file), "utf8");
  }
  return maps;
}
