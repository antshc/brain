import { SurfaceError, type AppStatus, type SurfaceAdapter } from "./types";

// Everything about the HTTP wire lives here: base path, versioning, auth headers, paging and id translation.
// Features see the same shapes the other surfaces return.
export function apiSurface(baseUrl: string | null, fetcher: typeof fetch = fetch) {
  const fail = (message: string, next = "Is the app running? pnpm mole doctor") => new SurfaceError("api", message, next);

  async function request(path: string, params: Record<string, string | number | undefined> = {}) {
    if (!baseUrl) throw fail("No API URL is known for this run.", "Start the app, then: pnpm mole down; pnpm mole up. Or set PROOF_API_URL.");
    const url = new URL(path, baseUrl);
    for (const [key, value] of Object.entries(params)) if (value !== undefined) url.searchParams.set(key, String(value));
    try { return await fetcher(url, { signal: AbortSignal.timeout(10_000) }); } catch (error) {
      throw fail(`Can't reach ${url.origin}: ${error instanceof Error ? error.message : String(error)}.`,
        "Check the app is running and the URL is right: pnpm mole doctor. To set it by hand: PROOF_API_URL=<url>");
    }
  }

  async function json<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
    const response = await request(path, params);
    if (!response.ok) throw fail(`GET ${path} answered ${response.status}.`, "Check the route in the app's API definition.");
    return await response.json() as T;
  }

  const adapter: SurfaceAdapter = {
    surface: "api",
    app: {
      async status(): Promise<AppStatus> {
        const response = await request("/");
        return { surface: "api", ok: response.status < 500, status: response.status };
      },
    },
  };

  return { ...adapter, request, json };
}

export type ApiSurface = ReturnType<typeof apiSurface>;
