// Reference only (eShop): proof/pages/catalog-page.ts. Every selector, route and URL rule of the storefront's catalog lives here.
import type { Page } from "@playwright/test";
import { FilterGroup } from "../components/filter-group";

export const PAGE_SIZE = 9;

export class CatalogPage {
  readonly brands: FilterGroup;
  constructor(private readonly page: Page) { this.brands = new FilterGroup(page, "Brand"); }

  // Blazor streams the catalog in after the first paint: wait for products, an empty result, or an item.
  async settle() {
    await this.page.waitForLoadState("load");
    await this.page.locator(".catalog-product, .catalog-empty").first().waitFor({ timeout: 15_000 }).catch(() => {});
  }

  async open(url: string) {
    await this.page.goto(url, { waitUntil: "load", timeout: 15_000 });
    await this.settle();
  }

  async goToPage(n: number) {
    await this.page.getByRole("link", { name: String(n), exact: true }).first().click();
    await this.page.waitForURL(new RegExp(`[?&]page=${n}(&|$)`), { timeout: 15_000 });
    await this.settle();
  }

  async filterByBrand(name: string) {
    await this.open(new URL(await this.brands.hrefOf(name), this.page.url()).href);
  }

  async productNames() { return this.page.locator(".catalog-product .name").allInnerTexts(); }
  async emptyState() { return (await this.page.locator(".catalog-empty").count()) ? (await this.page.locator(".catalog-empty").innerText()).trim() : null; }
  url() { return new URL(this.page.url()); }
}
