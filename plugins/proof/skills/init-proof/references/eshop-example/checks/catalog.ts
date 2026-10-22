// Reference only (eShop): proof/checks/catalog.ts. A check observes through the evidence it declares and returns a Finding.
// It names facts a user would state; the seed numbers are constants with a hint that says where the seed lives.
import { defineProof } from "../kit";
import { CATALOG_PATH } from "../adapters/api";
import { CatalogPage, PAGE_SIZE } from "../pages/catalog-page";

const SEED = 101;
const DAYBIRD = 10;
type Paged = { pageIndex: number; pageSize: number; count: number; data: { id: number; name: string }[] };

export const page2SharesNothingWithPage1 = defineProof("page-2-shares-nothing-with-page-1", ["dom-assertion"], async ctx => {
  const names = await ctx.observe<string[]>("dom-assertion", { describe: "the product names on page 2", read: page => new CatalogPage(page).productNames() });
  const shared = names.filter(name => (ctx.vars.page1 as string[]).includes(name));
  return { pass: names.length === PAGE_SIZE && shared.length === 0, expected: { count: PAGE_SIZE, shared: [] }, actual: { count: names.length, shared },
    hint: "Page 2 should list 9 products and none from page 1 (see e2e/BrowseItemTest.spec.ts)." };
});

export const brandFilterDropsThePageNumber = defineProof("brand-filter-drops-the-page-number", ["dom-assertion"], async ctx => {
  const search = await ctx.observe<string>("dom-assertion", { describe: "the address after filtering from page 2", read: page => new CatalogPage(page).url().search });
  const params = new URLSearchParams(search);
  return { pass: !params.has("page") && params.has("brand"), expected: "?brand=ID with no page", actual: search,
    hint: "Choosing a filter must reset to page 1: the filter links should clear `page`." };
});

// The API counts pages from 0: this is the only place that knows.
export const apiPage2SharesNothingWithPage1 = defineProof("api-page-2-shares-nothing-with-page-1", ["api-response"], async ctx => {
  const { body: first } = await ctx.observe<{ body: Paged }>("api-response", { path: `${CATALOG_PATH}/items`, params: { pageIndex: 0, pageSize: PAGE_SIZE } });
  const { body: second } = await ctx.observe<{ body: Paged }>("api-response", { path: `${CATALOG_PATH}/items`, params: { pageIndex: 1, pageSize: PAGE_SIZE } });
  const shared = second.data.filter(item => first.data.some(other => other.id === item.id)).map(item => item.id);
  return { pass: second.count === SEED && second.data.length === PAGE_SIZE && shared.length === 0, expected: { total: SEED, shared: [] }, actual: { total: second.count, shared },
    hint: "Is Catalog.API seeded from src/Catalog.API/Setup/catalog.json? Paging returned the same product on two pages." };
});

export const daybirdHasTenProducts = defineProof("daybird-has-ten-products", ["api-response"], async ctx => {
  const brands = await ctx.observe<{ body: { id: number; brand: string }[] }>("api-response", { path: `${CATALOG_PATH}/catalogBrands` });
  const id = brands.body.find(row => row.brand === "Daybird")?.id;
  const { body } = await ctx.observe<{ body: Paged }>("api-response", { path: `${CATALOG_PATH}/items`, params: { brand: id, pageSize: PAGE_SIZE } });
  return { pass: body.count === DAYBIRD, expected: DAYBIRD, actual: body.count, hint: "The total after the Daybird filter should be 10 (see src/Catalog.API/Setup/catalog.json)." };
});
