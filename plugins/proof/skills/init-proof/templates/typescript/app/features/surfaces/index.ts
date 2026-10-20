import type { Page } from "@playwright/test";
import type { Surface } from "../../kit";
import type { SurfaceAdapter } from "./types";
// <surface: api>
import { apiSurface } from "./api";
// </surface: api>
// <surface: web>
import { webSurface } from "./web";
// </surface: web>

export * from "./types";
// <surface: web>
export { COLD, webSurface, type WebSurface } from "./web";
// </surface: web>
// <surface: api>
export { apiSurface, type ApiSurface } from "./api";
// </surface: api>

// A surface's adapter for one run. The API has no browser and needs the URL that `up` recorded; without it every call says so.
export function adapterFor(surface: Surface, target: { page: Page | null; apiUrl: string | null }): SurfaceAdapter {
  // <surface: web>
  if (surface === "web") {
    if (!target.page) throw new Error("The web surface needs a browser page.");
    return webSurface(target.page);
  }
  // </surface: web>
  // <surface: api>
  if (surface === "api") return apiSurface(target.apiUrl);
  // </surface: api>
  throw new Error(`The ${surface} surface is not supported by this repo's proof kit.`);
}
