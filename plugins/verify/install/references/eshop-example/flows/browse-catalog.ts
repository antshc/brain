// Reference only (eShop): proof/flows/browse-catalog.ts. User actions only: they act and hand back variables, never a verdict.
import { defineFlow } from "../kit";
import { CatalogPage } from "../pages/catalog-page";

export const openCatalog = defineFlow("open-catalog", async env => {
  await new CatalogPage(env.page).open(env.appUrl);
});

export const goToPage2 = defineFlow("go-to-page-2", async env => {
  const catalog = new CatalogPage(env.page);
  const first = await catalog.productNames();
  await catalog.goToPage(2);
  return { page1: first };
});

export const filterByDaybird = defineFlow("filter-by-daybird", async env => {
  await new CatalogPage(env.page).filterByBrand("Daybird");
});
