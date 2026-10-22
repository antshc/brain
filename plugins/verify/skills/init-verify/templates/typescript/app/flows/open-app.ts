import { defineFlow } from "../kit";
import { AppPage } from "../pages/app-page";

// A flow is a user action: it acts and returns variables, never a verdict. Compose flows in a scenario.
export const openApp = defineFlow("open-app", async env => {
  await new AppPage(env.page).open(env.appUrl);
});
