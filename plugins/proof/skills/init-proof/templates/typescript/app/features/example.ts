import { defineFeature } from "../kit";
// <surface: web>
import { openApp } from "../flows/open-app";
import { pageShowsHeading } from "../checks/example-web";
// </surface: web>
// <surface: api>
import { apiAnswers } from "../checks/example-api";
// </surface: api>

// Map: .github/skills/verify-mole/features/example.md. Sub-features own scenarios; a scenario composes flows (user actions)
// and attaches proof checks in the order the map lists them. Replace this placeholder, or keep it as a smoke check.
export const example = defineFeature("example", feature => {
  feature.touches("src/"); // TODO(proof): the path prefixes of this feature's files
  feature.surfaces({{SURFACES_LIST}});
  feature.subFeature("app-answers", sub => {
    // <surface: web>
    sub.scenario("web", scenario => scenario.flow(openApp).proof(pageShowsHeading));
    // </surface: web>
    // <surface: api>
    sub.scenario("api", scenario => scenario.proof(apiAnswers));
    // </surface: api>
  });
});
