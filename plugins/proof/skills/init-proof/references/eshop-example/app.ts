import { execFileSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";
import type { AppConfig } from "./engine/runtime";

// Reference only: the proof/app.ts that eShop (a .NET Aspire AppHost, a Blazor storefront on :5045 and a catalog API
// behind a mobile-bff proxy) would use with this kit. Everything eShop-specific lives here, none of it in the engine.

// An SDK that satisfies global.json may exist without being on PATH (a user-level install in ~/.dotnet is common).
// Returns the extra environment to run dotnet with, or throws when no SDK matches.
function dotnetEnv(): NodeJS.ProcessEnv {
  for (const root of [undefined, process.env.DOTNET_ROOT, join(homedir(), ".dotnet")]) {
    const env = root ? { ...process.env, DOTNET_ROOT: root, PATH: `${root}:${process.env.PATH ?? ""}` } : process.env;
    try {
      execFileSync("dotnet", ["--version"], { env, stdio: "ignore" }); // Resolves the SDK global.json asks for.
      return root ? { DOTNET_ROOT: root, PATH: env.PATH } : {};
    } catch { /* try the next place */ }
  }
  throw new Error("No .NET SDK that satisfies global.json was found on PATH, in DOTNET_ROOT, or in ~/.dotnet. Install the SDK version listed in global.json.");
}

export const APP: AppConfig = {
  name: "eShop",
  url: process.env.ESHOP_URL ?? "http://localhost:5045",
  surfaces: ["web", "api"],
  // What a change to the storefront or to the catalog API it reads would touch.
  sourcePaths: ["src/WebApp", "src/WebAppComponents", "src/Catalog.API"],
  start: {
    command: "dotnet",
    args: ["run", "--project", "src/eShop.AppHost/eShop.AppHost.csproj"],
    env: { ESHOP_USE_HTTP_ENDPOINTS: "1", ASPIRE_ALLOW_UNSECURED_TRANSPORT: "true" }, // HTTP endpoints keep WebApp on :5045.
    prerequisites: dotnetEnv,
    // The home page streams its catalog, so a 200 alone can mean the catalog is not up yet.
    ready: async url => (await (await fetch(url, { signal: AbortSignal.timeout(5000) })).text()).includes("catalog-product"),
    timeoutMs: 300_000, // The first start restores packages and pulls containers.
  },
  api: {
    // The catalog API is reached through the mobile-bff proxy, whose port Aspire picks at random. PROOF_API_URL overrides it.
    discover: () => {
      try {
        const text = execFileSync("aspire", ["describe", "--format", "Json", "--non-interactive", "--nologo"], { encoding: "utf8", timeout: 15_000, stdio: ["ignore", "pipe", "ignore"] });
        const described = JSON.parse(text.slice(text.indexOf("{"))) as { resources: { displayName: string; urls?: { name: string; url: string }[] }[] };
        return described.resources.find(resource => resource.displayName === "mobile-bff")?.urls?.find(url => url.name === "http")?.url ?? null;
      } catch { return null; }
    },
  },
  web: {
    // Blazor streams the catalog in after the first paint, so wait for products, an empty result, or an item.
    settle: async page => {
      await page.waitForLoadState("load");
      await page.locator(".catalog-product, .catalog-empty, .item-details").first().waitFor({ timeout: 5000 }).catch(() => {});
    },
    snapshot: async page => ({
      count: (await page.locator(".catalog-count").first().innerText().catch(() => null))?.trim() ?? null,
    }),
  },
};
