// Reference only (eShop): proof/features/catalog.ts. Sub-features own scenarios; a scenario composes flows and attaches
// proof checks in the order the map lists them. The map is .github/skills/verify-mole/features/catalog.md.
import { defineFeature } from "../kit";
import { apiPage2SharesNothingWithPage1, brandFilterDropsThePageNumber, daybirdHasTenProducts, page2SharesNothingWithPage1 } from "../checks/catalog";
import { filterByDaybird, goToPage2, openCatalog } from "../flows/browse-catalog";

export const catalog = defineFeature("catalog", feature => {
  feature.touches("src/WebApp/Components/Pages/Catalog/", "src/WebAppComponents/Catalog/", "src/Catalog.API/");
  feature.surfaces("web", "api");
  feature.subFeature("paging", sub => {
    sub.scenario("web", scenario => scenario.flow(openCatalog).flow(goToPage2).proof(page2SharesNothingWithPage1));
    sub.scenario("api", scenario => scenario.proof(apiPage2SharesNothingWithPage1));
  });
  feature.subFeature("brand-filter", sub => {
    sub.scenario("web", scenario => scenario.flow(openCatalog).flow(goToPage2).flow(filterByDaybird).proof(brandFilterDropsThePageNumber));
    sub.scenario("api", scenario => scenario.proof(daybirdHasTenProducts));
  });
});
