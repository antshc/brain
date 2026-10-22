import type { Page } from "@playwright/test";
import { APP } from "../app";

// Everything about this app's pages lives here: selectors, routes, the URL it keeps state in. Flows and checks never touch them.
// Reusable parts of a page (a dropdown, a modal, a table) belong in proof/components/ once a second feature needs them.
export class AppPage {
  constructor(private readonly page: Page) {}

  async settle() {
    if (APP.web?.settle) await APP.web.settle(this.page); else await this.page.waitForLoadState("load");
  }

  async open(url: string) {
    await this.page.goto(url, { waitUntil: "load", timeout: 15_000 });
    await this.settle();
  }

  async heading() {
    const heading = this.page.getByRole("heading", { level: 1 });
    return (await heading.count()) ? (await heading.first().innerText()).trim() : null;
  }
}
