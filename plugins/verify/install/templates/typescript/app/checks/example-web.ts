import { defineProof } from "../kit";
import { AppPage } from "../pages/app-page";

// A proof check observes through its declared evidence and returns a Finding. It never navigates or changes the app.
export const pageShowsHeading = defineProof("page-shows-heading", ["dom-assertion"], async ctx => {
  const heading = await ctx.observe<string | null>("dom-assertion", { describe: "the first heading on the page", read: page => new AppPage(page).heading() });
  return { pass: Boolean(heading), expected: "a visible heading", actual: heading, hint: "The app opened but shows no heading. Is the build fresh? pnpm mole doctor" };
});
