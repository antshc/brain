# Catalog browsing (eShop)

An anonymous visitor lists the product catalog, pages through it, and narrows it by brand. The seed has 101 products and 13 brands, 9 products per page. The same catalog is read on two surfaces: the storefront (`web`) and the catalog API behind it (`api`).

## Sub-features

- `paging` — Pages hold 9 products, count from 1 and share nothing.
- `brand-filter` — Choosing a brand narrows the list to that brand and starts at page 1.

## How to get to it (user POV)

Open the storefront's home page: the catalog is the grid under the hero. Page links sit under the grid; brand tags sit beside it. Anyone can reach the catalog API through the mobile-bff proxy.

## Driving it with Mole

**(paging | web):** **Given** a visitor on the first catalog page; **When** they go to page 2; **Then** page 2 lists 9 products and none from page 1. **Proof:** page 2 shares nothing with page 1 (DOM assertion).

**(paging | api):** **Given** the seeded catalog; **When** a client asks for page 2; **Then** the total is 101, the page holds 9 products and none repeat page 1. **Proof:** page 2 shares nothing with page 1 (API response).

**(brand-filter | web):** **Given** a visitor on page 2; **When** they choose the Daybird brand; **Then** the address keeps the brand and drops the page number. **Proof:** the address has the brand and no page (DOM assertion).

**(brand-filter | api):** **Given** the seeded catalog; **When** a client filters by Daybird; **Then** the total is 10. **Proof:** the Daybird total is 10 (API response).

## Gotchas

- The grid streams in after the first paint, and the first load after a cold start is slow. A total of 0 straight after `open` is not a finding: ask again.
- The API is reached through the mobile-bff proxy, whose port Aspire picks at random. `up` finds it and `doctor` shows it. Set `ESHOP_API_URL` to the proxy URL if mole cannot find it.
- The API counts pages from 0 and defaults to 10 per page; filters are ids on the wire. The API adapter and the checks hide that, so a raw `api get` does not.
- After editing `src/WebApp`, `src/WebAppComponents` or `src/Catalog.API`, restart the app (`pnpm mole down`, then `up`). Blazor does not hot-reload under mole, and `doctor` reports the build STALE until you do.
- Anonymous visitor only. Signed-in behavior needs the `e2e/` credentials and is out of scope.
