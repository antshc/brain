# eShop example (reference only)

eShop is the repository this kit was extracted from: a .NET Aspire AppHost, a Blazor storefront (web) and a catalog API behind a mobile-bff proxy (api). These files show what `init-proof` leaves for you to write in the TypeScript scenario model; they are not compiled or copied.

| File | Seam it shows |
|---|---|
| `app.ts` | `proof/app.ts`: AppHost start command, SDK prerequisite, `aspire describe` API discovery, Blazor settle and snapshot hooks. |
| `adapters/api.ts` | `proof/adapters/api.ts`: the `api-response` source with the proxy's `api-version` query. |
| `components/filter-group.ts` | `proof/components/`: a reusable part (a group of filter tags). |
| `pages/catalog-page.ts` | `proof/pages/`: all selectors, routes and URL rules of the storefront catalog. |
| `flows/browse-catalog.ts` | `proof/flows/`: user actions that return variables, never a verdict. |
| `checks/catalog.ts` | `proof/checks/`: proof checks that observe through declared evidence and return a Finding. |
| `features/catalog.ts` | `proof/features/catalog.ts`: `defineFeature` with sub-features, scenarios, flows and proofs. |
| `catalog.md` | the feature map: four sections, one paragraph per scenario with its evidence. |

`v1/` keeps the older per-surface adapter shape (`observe`, `kit.check`, `drive` hooks) that the Python kit still uses: `types.ts`, `web.ts`, `api.ts`, `catalog.ts` and the Contract-style `catalog.md`.

eShop also had an optional LLM `judge` command; it is not part of the kit.
