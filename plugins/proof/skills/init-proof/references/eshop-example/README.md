# eShop example (reference only)

eShop is the repository this kit was extracted from: a .NET Aspire AppHost, a Blazor storefront (web) and a catalog API behind a mobile-bff proxy (api). These files are a worked example of what `/init-proof` leaves for you to write; they are not compiled or copied.

| File | Seam it shows |
|---|---|
| `app.ts` | `proof/app.ts`: AppHost start command, SDK prerequisite, `aspire describe` API discovery, Blazor settle and snapshot hooks. |
| `types.ts` | `proof/features/surfaces/types.ts`: one shape per contract (`CatalogList`, `ProductShow`) shared by every surface. |
| `web.ts` | `proof/features/surfaces/web.ts`: all selectors, routes and URL state of the storefront. |
| `api.ts` | `proof/features/surfaces/api.ts`: versioning, 0-based paging, ids to names, hidden from features. |
| `catalog.ts` | `proof/features/catalog.ts`: the contract checked on each surface, plus a block for what only the web has. |
| `catalog.md` | the feature map: Contract, Driving it, Web only, Gotchas. |

Differences from the generic kit: eShop's `mole catalog list` and `mole product show` were hard-coded commands. In the generic kit they are a feature's `drive` hook (`{ usage, summary, run(call) }` in `proof/features/index.ts`), so `pnpm mole catalog list --page 2 --surface api` works the same way. eShop also had an optional LLM `judge` command; it is not part of the kit.
