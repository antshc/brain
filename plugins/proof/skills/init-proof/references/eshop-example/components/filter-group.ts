// Reference only (eShop): proof/components/filter-group.ts. A reusable part: one group of filter tags (Brand or Type).
import type { Locator, Page } from "@playwright/test";

export class FilterGroup {
  private readonly tags: Locator;
  constructor(page: Page, readonly name: "Brand" | "Type") {
    this.tags = page.locator(".catalog-search-group", { has: page.getByRole("heading", { name, exact: true }) }).locator(".catalog-search-tag");
  }
  /** A disabled tag (no matches) cannot be clicked but its link works, so follow the link as a bookmark would. */
  async hrefOf(option: string) {
    const tag = this.tags.filter({ has: this.tags.page().locator("span", { hasText: new RegExp(`^${option}$`, "i") }) });
    if (!(await tag.count())) throw new Error(`There is no ${this.name.toLowerCase()} filter called "${option}".`);
    return (await tag.first().getAttribute("href"))!;
  }
}
