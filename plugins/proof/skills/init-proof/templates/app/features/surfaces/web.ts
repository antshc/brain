import type { Page } from "@playwright/test";
import { APP } from "../../app";
import { SurfaceError, type AppStatus, type SurfaceAdapter } from "./types";

// A freshly started app renders its first pages slowly; waits for first renders use this.
export const COLD = 15_000;

const fail = (message: string, next: string) => new SurfaceError("web", message, next);

// Everything about the app's pages lives here: selectors, routes, the URL it keeps state in. Features never touch them.
export function webSurface(page: Page) {
  const home = () => new URL("/", page.url().startsWith("http") ? page.url() : APP.url).href;

  async function settle() {
    if (APP.web?.settle) await APP.web.settle(page);
    else await page.waitForLoadState("load");
  }

  async function go(url: string) {
    const response = await page.goto(url, { waitUntil: "load", timeout: COLD }).catch((error: Error) => {
      throw fail(`Can't open ${url}: ${error.message.split("\n")[0]}.`, "Is the app up? pnpm mole doctor");
    });
    await settle();
    return response;
  }

  const adapter: SurfaceAdapter = {
    surface: "web",
    app: {
      async status(): Promise<AppStatus> {
        const response = await go(home());
        const status = response?.status() ?? 0;
        return { surface: "web", ok: status > 0 && status < 400, status };
      },
    },
  };

  // What only a browser visitor has: the page chrome, URL state, navigation. No other surface has these.
  return { ...adapter, go, settle, url: () => page.url() };
}

export type WebSurface = ReturnType<typeof webSurface>;
