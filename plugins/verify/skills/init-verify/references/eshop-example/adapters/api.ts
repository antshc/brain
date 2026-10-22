// Reference only (eShop): proof/adapters/api.ts. The wire details no check should know: the mobile-bff proxy only matches
// a request that carries api-version, and Catalog.API counts pages from 0. A source with the same id replaces the kit's.
import { apiResponseAdapter } from "../kit";

export const CATALOG_PATH = "/catalog-api/api/catalog";

export const apiResponse = apiResponseAdapter({
  fetcher: (input, init) => {
    const url = new URL(String(input));
    url.searchParams.set("api-version", "2.0");
    return fetch(url, init);
  },
});
